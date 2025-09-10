#!/usr/bin/env python3
"""
Functional Test Runner - Example Implementation

This demonstrates a better testing approach that focuses on functionality
rather than HTML comparison. This can run alongside the current golden
master tests during the migration period.
"""

import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum


class FunctionalTestResult(Enum):
    PASS = "pass"
    FAIL = "fail"
    ERROR = "error"


@dataclass
class FunctionalTest:
    name: str
    description: str
    test_function: str  # Method name to call
    category: str = "functional"


class FunctionalTestRunner:
    """
    Functional test runner that tests Geneweb behavior rather than HTML output.

    This approach is:
    - More robust than HTML comparison
    - Survives CSS and template changes
    - Compatible with future Vue.js migration
    - Focuses on actual functionality
    """

    def __init__(self, base_url: str, database: str):
        self.base_url = base_url
        self.database = database
        self.session = requests.Session()

        # Test data (should match your test database)
        self.test_person_id = 26
        self.test_person_first_name = "anthoine"
        self.test_person_last_name = "geruzet"
        self.test_family_id = 13

    def run_all_tests(self) -> Dict[str, FunctionalTestResult]:
        """Run all functional tests and return results."""
        tests = self.get_functional_tests()
        results = {}

        for test in tests:
            try:
                test_method = getattr(self, test.test_function)
                result = test_method()
                results[test.name] = result
                print(f"✓ {test.name}: {result.value}")
            except Exception as e:
                results[test.name] = FunctionalTestResult.ERROR
                print(f"✗ {test.name}: ERROR - {e}")

        return results

    def get_functional_tests(self) -> List[FunctionalTest]:
        """Define all functional tests."""
        return [
            FunctionalTest(
                name="server_responding",
                description="Verify server is responding to requests",
                test_function="test_server_responding"
            ),
            FunctionalTest(
                name="database_accessible",
                description="Verify database is accessible",
                test_function="test_database_accessible"
            ),
            FunctionalTest(
                name="person_search_finds_results",
                description="Person search returns expected results",
                test_function="test_person_search_finds_results"
            ),
            FunctionalTest(
                name="person_display_shows_data",
                description="Person display page shows correct data",
                test_function="test_person_display_shows_data"
            ),
            FunctionalTest(
                name="ancestry_tree_renders",
                description="Ancestry tree page renders without errors",
                test_function="test_ancestry_tree_renders"
            ),
            FunctionalTest(
                name="navigation_links_work",
                description="Navigation links are functional",
                test_function="test_navigation_links_work"
            ),
            FunctionalTest(
                name="no_server_errors",
                description="Pages don't contain server error messages",
                test_function="test_no_server_errors"
            ),
        ]

    def _make_request(self, url_params: str) -> requests.Response:
        """Make a request to Geneweb with given parameters."""
        url = f"{self.base_url}/{self.database}?{url_params}"
        response = self.session.get(url, timeout=10)
        return response

    def test_server_responding(self) -> FunctionalTestResult:
        """Test that the server responds to basic requests."""
        try:
            response = self._make_request("")
            if response.status_code == 200:
                return FunctionalTestResult.PASS
            else:
                return FunctionalTestResult.FAIL
        except requests.RequestException:
            return FunctionalTestResult.ERROR

    def test_database_accessible(self) -> FunctionalTestResult:
        """Test that the database is accessible."""
        try:
            response = self._make_request("m=TT")  # Welcome page

            # Check for database access errors
            error_indicators = [
                "database not found",
                "access denied",
                "file not found",
                "permission denied"
            ]

            content_lower = response.text.lower()
            for error in error_indicators:
                if error in content_lower:
                    return FunctionalTestResult.FAIL

            return FunctionalTestResult.PASS

        except requests.RequestException:
            return FunctionalTestResult.ERROR

    def test_person_search_finds_results(self) -> FunctionalTestResult:
        """Test that person search returns expected results."""
        try:
            # Search for test person
            response = self._make_request(
                f"m=S&n={self.test_person_first_name}+{self.test_person_last_name}&p="
            )

            if response.status_code != 200:
                return FunctionalTestResult.FAIL

            content_lower = response.text.lower()

            # Should contain the person's name
            full_name = f"{self.test_person_first_name} {self.test_person_last_name}"
            if full_name.lower() not in content_lower:
                return FunctionalTestResult.FAIL

            # Should not contain error messages
            error_indicators = ["no results", "not found", "error", "exception"]
            for error in error_indicators:
                if error in content_lower:
                    return FunctionalTestResult.FAIL

            return FunctionalTestResult.PASS

        except requests.RequestException:
            return FunctionalTestResult.ERROR

    def test_person_display_shows_data(self) -> FunctionalTestResult:
        """Test that person display page shows correct data."""
        try:
            # Get person display page
            response = self._make_request(f"m=A&i={self.test_person_id}")

            if response.status_code != 200:
                return FunctionalTestResult.FAIL

            content_lower = response.text.lower()

            # Should contain person's name
            if self.test_person_first_name.lower() not in content_lower:
                return FunctionalTestResult.FAIL
            if self.test_person_last_name.lower() not in content_lower:
                return FunctionalTestResult.FAIL

            # Should have typical person page elements (flexible check)
            # Look for common words that appear on person pages
            expected_elements = ["born", "birth", "family", "parents", "children"]
            found_elements = sum(1 for element in expected_elements if element in content_lower)

            # At least some biographical elements should be present
            if found_elements < 2:
                return FunctionalTestResult.FAIL

            return FunctionalTestResult.PASS

        except requests.RequestException:
            return FunctionalTestResult.ERROR

    def test_ancestry_tree_renders(self) -> FunctionalTestResult:
        """Test that ancestry tree page renders without errors."""
        try:
            # Get ancestry tree page
            response = self._make_request(f"m=A&i={self.test_person_id}&t=T&v=5")

            if response.status_code != 200:
                return FunctionalTestResult.FAIL

            content_lower = response.text.lower()

            # Should not contain error messages
            error_indicators = ["error", "exception", "failed", "not found"]
            for error in error_indicators:
                if error in content_lower:
                    return FunctionalTestResult.FAIL

            # Should contain ancestry-related content
            ancestry_indicators = ["ancestor", "tree", "generation", "parent"]
            found_indicators = sum(1 for indicator in ancestry_indicators if indicator in content_lower)

            if found_indicators < 1:
                return FunctionalTestResult.FAIL

            return FunctionalTestResult.PASS

        except requests.RequestException:
            return FunctionalTestResult.ERROR

    def test_navigation_links_work(self) -> FunctionalTestResult:
        """Test that common navigation links are functional."""
        try:
            # Get a person page and parse it
            response = self._make_request(f"m=A&i={self.test_person_id}")
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find links that should work
            links = soup.find_all('a', href=True)

            # Test a few important navigation links
            important_patterns = ['m=A', 'm=D', 'm=S', 'm=TT']
            working_links = 0

            for link in links[:10]:  # Test first 10 links to avoid too many requests
                href = link['href']

                # Only test internal Geneweb links
                if any(pattern in href for pattern in important_patterns):
                    try:
                        # Extract parameters and test
                        if '?' in href:
                            params = href.split('?', 1)[1]
                            test_response = self._make_request(params)
                            if test_response.status_code == 200:
                                working_links += 1
                    except:
                        continue  # Skip problematic links

            # At least some navigation should work
            return FunctionalTestResult.PASS if working_links > 0 else FunctionalTestResult.FAIL

        except Exception:
            return FunctionalTestResult.ERROR

    def test_no_server_errors(self) -> FunctionalTestResult:
        """Test that common pages don't show server errors."""
        try:
            # Test several common pages
            test_pages = [
                "",  # Home page
                "m=TT",  # Welcome
                f"m=A&i={self.test_person_id}",  # Person display
                "m=S",  # Search form
                "m=AN",  # Names list
            ]

            error_patterns = [
                "internal server error",
                "500 error",
                "exception",
                "stack trace",
                "ocaml error",
                "fatal error"
            ]

            for page_params in test_pages:
                response = self._make_request(page_params)
                content_lower = response.text.lower()

                for error_pattern in error_patterns:
                    if error_pattern in content_lower:
                        return FunctionalTestResult.FAIL

            return FunctionalTestResult.PASS

        except requests.RequestException:
            return FunctionalTestResult.ERROR


def main():
    """Example usage of functional testing."""
    base_url = "http://localhost:2317"
    database = "galichet"

    runner = FunctionalTestRunner(base_url, database)

    print("Running functional tests...")
    print("=" * 50)

    results = runner.run_all_tests()

    print("\n" + "=" * 50)
    print("Results Summary:")

    passed = sum(1 for r in results.values() if r == FunctionalTestResult.PASS)
    failed = sum(1 for r in results.values() if r == FunctionalTestResult.FAIL)
    errors = sum(1 for r in results.values() if r == FunctionalTestResult.ERROR)
    total = len(results)

    print(f"  Total:  {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Errors: {errors}")

    if failed > 0 or errors > 0:
        print("\n⚠️  Some tests failed. Check Geneweb server and database.")
        return 1
    else:
        print("\n✅ All functional tests passed!")
        return 0


if __name__ == "__main__":
    exit(main())
