#!/usr/bin/env python3
"""
Geneweb Test Runner

A Python-based test runner for Geneweb that provides clean, maintainable testing
with golden master functionality. This replaces the shell-based run_gw_test.sh
with better structure and cleaner code principles.

Usage:
    python geneweb_test_runner.py [options] [database_name] [wizard_credentials]

Options:
    --mode cgi          Test in CGI mode instead of local port
    --debug             Enable debug output
    --capture           Capture outputs as new reference files
    --compare           Compare outputs against reference files
    --config FILE       Configuration file to override defaults
    --help              Show this help message

Examples:
    python geneweb_test_runner.py                           # Run basic tests
    python geneweb_test_runner.py --capture                 # Capture new golden master files
    python geneweb_test_runner.py --compare                 # Compare against references
    python geneweb_test_runner.py galichet                  # Test specific database
"""

import argparse
import logging
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests


class TestMode(Enum):
    """Test execution modes."""
    BASIC = "basic"
    CGI = "cgi"
    CAPTURE = "capture"
    COMPARE = "compare"


class TestResult(Enum):
    """Test result states."""
    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class TestConfiguration:
    """Configuration for Geneweb testing."""

    # Database configuration
    database_name: str = "galichet"
    wizard_credentials: str = ""

    # Server configuration
    distribution_dir: str = "./distribution"
    bin_dir: str = "./distribution/gw"
    bases_dir: str = "./distribution/bases"
    gwd_log: str = "./distribution/gw/gwd.log"
    gwd_cgi: str = "gwd.cgi"
    gwd_log_cgi: str = "/tmp/gwd.log"

    # Test execution settings
    mode: TestMode = TestMode.BASIC
    clean_log: bool = True
    sudo_prefix: str = ""
    curl_max_time: int = 5
    start_gwd: bool = True
    debug: bool = False

    # Test data - main person for testing
    wizard_id: str = "hg"
    first_name: str = "anthoine"
    surname: str = "geruzet"
    occurrence: int = 0
    person_id: int = 26  # Individual ID, should have multiple events
    family_id: int = 13  # Family ID for this individual

    # Test data - person without grandparents
    first_name_1: str = "anthoine"
    surname_1: str = "geruzet"
    occurrence_1: int = 0

    # Test data - person without parents
    first_name_2: str = "marie"
    surname_2: str = "dupond"
    occurrence_2: int = 0

    # Test images and files
    carousel_image: str = "peugeot_206.png"
    carousel_saved_image: str = "850r.jpg"
    source_image: str = "carte.de.priere.png"
    source_text: str = "macros.txt"
    portrait_image: str = "jean_pierre.0.galichet.jpg"

    # Test locations and data
    note_name: str = "chantal"
    gallery_name: str = "Gallery"
    place_name: str = "Australie"

    # Output configuration
    reference_dir: str = "ref"
    golden_master_dir: str = "golden_master_outputs"

    # Error detection patterns
    failing_conditions: List[str] = field(default_factory=lambda: ["CRITICAL", "ERROR", "Failed"])
    warning_conditions: List[str] = field(default_factory=lambda: ["WARNING"])

    @classmethod
    def from_file(cls, config_file: Path) -> 'TestConfiguration':
        """Load configuration from a file."""
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_file}")

        # For now, support simple key=value format like the original shell script
        config = cls()
        with open(config_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    # Map shell variable names to Python attribute names
                    if key == 'DBNAME':
                        config.database_name = value
                    elif key == 'PWD':
                        config.wizard_credentials = value
                    elif key == 'FN':
                        config.first_name = value
                    elif key == 'SN':
                        config.surname = value
                    elif key == 'ID':
                        config.person_id = int(value)
                    elif key == 'FID':
                        config.family_id = int(value)
                    # Add more mappings as needed

        return config


@dataclass
class TestScenario:
    """Represents a single test scenario."""
    name: str
    description: str
    url_params: str
    expected_result: TestResult = TestResult.PASS
    skip_diff: bool = False
    category: str = "general"

    def get_filename_safe_name(self) -> str:
        """Get a filename-safe version of the test name."""
        return re.sub(r'[^a-zA-Z0-9_-]', '_', self.name.lower())


class GenewebTestRunner:
    """Main test runner for Geneweb."""

    def __init__(self, config: TestConfiguration):
        self.config = config
        self.logger = self._setup_logging()
        self.test_results: Dict[str, TestResult] = {}
        self.error_count = 0
        self.gwd_process: Optional[subprocess.Popen] = None

        # Setup directories
        self.test_dir = Path(__file__).parent
        self.reference_dir = self.test_dir / config.reference_dir
        self.golden_master_dir = self.test_dir / config.golden_master_dir
        self.temp_dir = Path("/tmp")

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        level = logging.DEBUG if self.config.debug else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)

    def _get_base_url(self) -> str:
        """Get the base URL for testing."""
        if self.config.mode == TestMode.CGI:
            return f"http://localhost/cgi-bin/{self.config.gwd_cgi}?b={self.config.database_name}&"
        else:
            return f"http://localhost:2317/{self.config.database_name}?"

    def _start_gwd_server(self) -> bool:
        """Start the Geneweb daemon if needed."""
        if not self.config.start_gwd or self.config.mode == TestMode.CGI:
            return True

        # Kill any existing gwd processes
        try:
            subprocess.run(["pkill", "gwd"], check=False)
            time.sleep(1)
        except subprocess.SubprocessError:
            pass

        # Build command
        cmd = [
            "env", f"OCAMLRUNPARAM=b",
            str(Path(self.config.bin_dir) / "gwd"),
            "-setup_link",
            "-bd", self.config.bases_dir,
            "-hd", self.config.bin_dir,
            "-trace_failed_passwd",
            "-robot_xcl", "10000,1",
            "-conn_tmout", "3600",
            "-lang", "en",
            "-log", "<stderr>",
            "-plugins", "-unsafe", f"{self.config.bin_dir}/plugins",
            "-n_workers", "0",
            "-predictable_mode"
        ]

        # Start server
        log_file = open(self.config.gwd_log, "a")
        self.gwd_process = subprocess.Popen(
            cmd,
            stderr=log_file,
            stdout=subprocess.DEVNULL
        )

        # Wait for server to start
        for attempt in range(10):
            try:
                response = requests.get(self._get_base_url(), timeout=2)
                if response.status_code == 200:
                    self.logger.info(f"gwd started successfully after {attempt + 1} attempts")
                    return True
            except requests.RequestException:
                time.sleep(1)

        self.logger.error("gwd failed to start after 10 attempts")
        return False

    def _stop_gwd_server(self):
        """Stop the Geneweb daemon."""
        if self.gwd_process:
            self.gwd_process.terminate()
            self.gwd_process.wait()

    def _make_request(self, scenario: TestScenario) -> Tuple[TestResult, str]:
        """Make an HTTP request for a test scenario."""
        url = self._get_base_url() + f"w={self.config.wizard_credentials}&" + scenario.url_params

        if self.config.debug:
            self.logger.debug(f"Testing {scenario.name}: {url}")

        try:
            response = requests.get(url, timeout=self.config.curl_max_time)
            content = response.text

            # Check for various error conditions
            if "<h1>Incorrect request</h1>" in content:
                if "<h1>404 Not Found</h1>" in content:
                    self.logger.error(f"Database {self.config.database_name} not found: {url}")
                    return TestResult.ERROR, content
                else:
                    self.logger.warning(f"Incorrect request: {scenario.name}")
                    return TestResult.FAIL, content

            if "404 Not Found" in content:
                self.logger.error(f"Web server unable to access CGI script: {url}")
                return TestResult.ERROR, content

            if "Access refused" in content:
                self.logger.error("gwd should not be started with robot protection")
                return TestResult.ERROR, content

            # Check for error variables in the response
            if "var.nb_errors.=" in content:
                if "var.nb_errors.=.0" not in content:
                    errors_match = re.search(r'var\.nb_errors\.=\s*(\d+)', content)
                    if errors_match:
                        error_count = int(errors_match.group(1))
                        self.logger.error(f"Test {scenario.name} reported {error_count} errors")
                        return TestResult.FAIL, content

            return TestResult.PASS, content

        except requests.Timeout:
            self.logger.error(f"Timeout for test {scenario.name}")
            return TestResult.ERROR, ""
        except requests.RequestException as e:
            self.logger.error(f"Request failed for {scenario.name}: {e}")
            return TestResult.ERROR, ""

    def _save_output(self, scenario: TestScenario, content: str):
        """Save test output for comparison."""
        if self.config.mode in [TestMode.CAPTURE, TestMode.COMPARE]:
            filename = scenario.get_filename_safe_name() + ".txt"

            if self.config.mode == TestMode.CAPTURE:
                # Save to both new golden_master structure AND legacy ref for compatibility
                self.reference_dir.mkdir(exist_ok=True)
                references_dir = self.golden_master_dir / "references"
                references_dir.mkdir(parents=True, exist_ok=True)

                # Save with clean name to golden_master_outputs/references/
                golden_output_file = references_dir / filename
                with open(golden_output_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                # Also save to legacy ref/ directory for backward compatibility
                legacy_output_file = self.reference_dir / filename
                with open(legacy_output_file, 'w', encoding='utf-8') as f:
                    f.write(content)
            else:
                # For comparison, save to temp directory first
                run_dir = self.temp_dir / "run"
                run_dir.mkdir(exist_ok=True)
                output_file = run_dir / filename
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(content)

    def _run_scenario(self, scenario: TestScenario) -> TestResult:
        """Run a single test scenario."""
        result, content = self._make_request(scenario)

        # Save output if needed
        if not scenario.skip_diff:
            self._save_output(scenario, content)

        # Update statistics
        self.test_results[scenario.name] = result
        if result in [TestResult.FAIL, TestResult.ERROR]:
            self.error_count += 1

        return result

    def get_test_scenarios(self) -> List[TestScenario]:
        """Get all test scenarios to run."""
        c = self.config  # Shorthand for cleaner code

        scenarios = [
            # Search tests
            TestScenario(
                name="search_person",
                description="Search for a specific person",
                url_params=f"m=S&n={c.first_name}+{c.surname}&p=",
                category="search"
            ),

            # Person display tests
            TestScenario(
                name="display_person_basic",
                description="Display basic person information",
                url_params=f"m=A&i={c.person_id}",
                category="person"
            ),

            # Ancestry tree variations
            TestScenario(
                name="ancestry_tree_basic",
                description="Display basic ancestry tree",
                url_params=f"m=A&i={c.person_id}&t=T&v=5",
                category="ancestry"
            ),
            TestScenario(
                name="ancestry_tree_compact",
                description="Display compact ancestry tree",
                url_params=f"m=A&i={c.person_id}&t=A&v=5",
                category="ancestry"
            ),
            TestScenario(
                name="ancestry_tree_cousins",
                description="Display ancestry tree with cousins",
                url_params=f"m=A&i={c.person_id}&t=C&v=5",
                category="ancestry"
            ),
            TestScenario(
                name="ancestry_tree_fanchart",
                description="Display fan chart ancestry",
                url_params=f"m=A&i={c.person_id}&t=FC&v=5",
                category="ancestry"
            ),
            TestScenario(
                name="ancestry_tree_numbered",
                description="Display numbered ancestry tree",
                url_params=f"m=A&i={c.person_id}&t=T&t1=7&v=5",
                category="ancestry"
            ),
            TestScenario(
                name="ancestry_tree_horizontal",
                description="Display horizontal ancestry tree",
                url_params=f"m=A&i={c.person_id}&t=T&t1=h6&v=5",
                category="ancestry"
            ),
            TestScenario(
                name="ancestry_tree_mixed",
                description="Display mixed ancestry tree",
                url_params=f"m=A&i={c.person_id}&t=T&t1=m&v=5",
                category="ancestry"
            ),
            TestScenario(
                name="ancestry_tree_chronological",
                description="Display chronological ancestry with SOSA",
                url_params=f"m=A&i={c.person_id}&t=T&t1=CT&v=5&sosa=on",
                category="ancestry"
            ),
            TestScenario(
                name="ancestry_horizontal_timeline",
                description="Display horizontal timeline",
                url_params=f"m=A&i={c.person_id}&t=H&v=5",
                category="ancestry"
            ),
            TestScenario(
                name="ancestry_detailed_report",
                description="Display detailed ancestry report",
                url_params=f"m=A&i={c.person_id}&t=Z&v=6&maxv=19&num=on&birth=on&birth_place=on&marr=on&marr_date=on&marr_place=on&child=on&death=on&death_place=on&age=on&occu=on&repeat=on&gen=1&ns=1&hl=1",
                category="ancestry"
            ),
            TestScenario(
                name="ancestry_graphical",
                description="Display graphical ancestry",
                url_params=f"m=A&i={c.person_id}&t=G&v=3&maxv=19&siblings=on&alias=on&parents=on&rel=on&witn=on&notes=on&src=on&hide=on",
                category="ancestry"
            ),

            # Administrative tests
            TestScenario(
                name="admin_add_database",
                description="Add database form",
                url_params="m=AD",
                category="admin"
            ),
            TestScenario(
                name="admin_add_family",
                description="Add family form",
                url_params="m=ADD_FAM",
                category="admin"
            ),
            TestScenario(
                name="admin_add_individual",
                description="Add individual form",
                url_params="m=ADD_IND",
                category="admin"
            ),
            TestScenario(
                name="admin_add_parents",
                description="Add parents form",
                url_params=f"m=ADD_PAR&pp={c.first_name_2}&np={c.surname_2}&ocp={c.occurrence_2}",
                category="admin"
            ),

            # Navigation tests
            TestScenario(
                name="nav_advanced_menu",
                description="Advanced menu",
                url_params="m=AM",
                category="navigation"
            ),
            TestScenario(
                name="nav_alphabetical_names",
                description="Alphabetical list of names",
                url_params="m=AN",
                category="navigation"
            ),
            TestScenario(
                name="nav_alphabetical_names_menu",
                description="Alphabetical names menu",
                url_params="m=ANM",
                category="navigation"
            ),
            TestScenario(
                name="nav_advanced_search",
                description="Advanced search",
                url_params="m=AS",
                category="navigation"
            ),

            # Cousins and relationships
            TestScenario(
                name="cousins_basic",
                description="Display cousins relationships",
                url_params=f"m=C&i={c.person_id}&v=3",
                category="relationships"
            ),
            TestScenario(
                name="cousins_alphabetical",
                description="Display cousins alphabetically",
                url_params=f"m=C&i={c.person_id}&t=AN",
                category="relationships"
            ),
            TestScenario(
                name="cousins_detailed",
                description="Display detailed cousins",
                url_params=f"m=C&i={c.person_id}",
                category="relationships"
            ),

            # Calendar test
            TestScenario(
                name="calendar",
                description="Display calendar",
                url_params="m=CAL",
                skip_diff=True,
                category="calendar"
            ),

            # Modification tests (these might fail on read-only databases)
            TestScenario(
                name="modify_children_order",
                description="Modify children order",
                url_params=f"m=CHG_CHN&ip={c.family_id}",
                expected_result=TestResult.FAIL,
                category="modification"
            ),
            TestScenario(
                name="modify_family_events_order",
                description="Modify family events order",
                url_params=f"m=CHG_EVT_FAM_ORD&i={c.family_id}&ip={c.person_id}",
                expected_result=TestResult.FAIL,
                category="modification"
            ),
            TestScenario(
                name="modify_individual_events_order",
                description="Modify individual events order",
                url_params=f"m=CHG_EVT_IND_ORD&i={c.person_id}",
                expected_result=TestResult.FAIL,
                category="modification"
            ),
            TestScenario(
                name="modify_family_order",
                description="Modify family order",
                url_params=f"m=CHG_FAM_ORD&f={c.family_id}&i={c.person_id}&n=2",
                expected_result=TestResult.FAIL,
                category="modification"
            ),

            # Descendants tests
            TestScenario(
                name="descendants_basic",
                description="Display basic descendants",
                url_params=f"m=D&i={c.person_id}",
                category="descendants"
            ),
            TestScenario(
                name="descendants_vertical",
                description="Display vertical descendants",
                url_params=f"m=D&i={c.person_id}&t=V&v=3",
                category="descendants"
            ),
            TestScenario(
                name="descendants_table_vertical",
                description="Display table vertical descendants",
                url_params=f"m=D&i={c.person_id}&t=TV&v=3",
                category="descendants"
            ),
            TestScenario(
                name="descendants_individual_detailed",
                description="Display individual detailed descendants",
                url_params=f"m=D&i={c.person_id}&t=I&v=3&num=on&birth=on&birth_place=on&marr=on&marr_date=on&marr_place=on&child=on&death=on&death_place=on&age=on&occu=on&gen=1&ns=1&hl=1",
                category="descendants"
            ),
            TestScenario(
                name="descendants_lineage",
                description="Display lineage descendants",
                url_params=f"m=D&i={c.person_id}&t=L&v=3&maxv=3&siblings=on&alias=on&parents=on&rel=on&witn=on&notes=on&src=on&hide=on",
                category="descendants"
            ),
            TestScenario(
                name="descendants_ancestry_numbered",
                description="Display numbered ancestry descendants",
                url_params=f"m=D&i={c.person_id}&t=A&num=on&v=3",
                category="descendants"
            ),

            # Deletion tests (these will fail on read-only databases)
            TestScenario(
                name="delete_family",
                description="Delete family",
                url_params=f"m=DEL_FAM&i={c.family_id}&ip={c.person_id}",
                expected_result=TestResult.FAIL,
                category="modification"
            ),
            TestScenario(
                name="delete_individual",
                description="Delete individual",
                url_params=f"m=DEL_IND&i={c.person_id}",
                expected_result=TestResult.FAIL,
                category="modification"
            ),
        ]

        # Add page module tests (like the shell script's modules section)
        page_modules = {
            "individu": ("i", [1, 2, 3]),
            "parents": ("p", [1, 2, 3, 4, 5]),
            "unions": ("u", [1, 2, 3, 4, 5]),
            "fratrie": ("f", [1, 2, 3, 4]),
            "relations": ("r", [1, 2]),
            "chronologie": ("c", [1, 2]),
            "notes": ("n", [1, 2]),
            "sources": ("s", [1, 2]),
            "arbres": ("a", [1, 2, 3, 4]),
            "htrees": ("h", [1, 2, 3, 4, 5]),
            "gr_parents": ("g", [1, 2]),
            "ligne": ("l", [1])
        }

        for module_name, (prefix, modes) in page_modules.items():
            for mode in modes:
                scenarios.append(TestScenario(
                    name=f"page_module_{module_name}_{mode}",
                    description=f"Test {module_name} page module mode {mode}",
                    url_params=f"p={c.first_name}&n={c.surname}&oc={c.occurrence}&p_mod={prefix}{mode}",
                    category="page_modules"
                ))

        # Add direct person access tests
        scenarios.extend([
            TestScenario(
                name="person_direct_access",
                description="Direct person access by name",
                url_params=f"p={c.first_name}&n={c.surname}&oc={c.occurrence}",
                category="person"
            ),
            TestScenario(
                name="person_without_grandparents",
                description="Person without grandparents",
                url_params=f"p={c.first_name_1}&n={c.surname_1}&oc={c.occurrence_1}",
                category="person"
            ),
            TestScenario(
                name="person_without_parents",
                description="Person without parents",
                url_params=f"p={c.first_name_2}&n={c.surname_2}&oc={c.occurrence_2}",
                category="person"
            ),
            TestScenario(
                name="nonexistent_person",
                description="Test with nonexistent person",
                url_params="p=xxx&n=yyy",
                expected_result=TestResult.FAIL,
                category="person"
            ),
        ])

        return scenarios


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Geneweb Test Runner - Clean Python-based testing for Geneweb",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'database',
        nargs='?',
        help='Database name to test (default: galichet)'
    )
    parser.add_argument(
        'wizard_credentials',
        nargs='?',
        default='',
        help='Wizard credentials in format wizard_id:password'
    )

    parser.add_argument(
        '--mode',
        choices=['cgi', 'basic'],
        default='basic',
        help='Test mode: cgi or basic (default: basic)'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug output'
    )
    parser.add_argument(
        '--capture',
        action='store_true',
        help='Capture outputs as new reference files'
    )
    parser.add_argument(
        '--compare',
        action='store_true',
        help='Compare outputs against reference files'
    )
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('./test-gw-vars.txt'),
        help='Configuration file (default: ./test-gw-vars.txt)'
    )
    parser.add_argument(
        '--category',
        help='Run only tests from specific category'
    )
    parser.add_argument(
        '--list-categories',
        action='store_true',
        help='List available test categories and exit'
    )
    parser.add_argument(
        '--list-scenarios',
        action='store_true',
        help='List all test scenarios and exit'
    )

    args = parser.parse_args()

    # Handle list commands
    if args.list_categories or args.list_scenarios:
        try:
            config = TestConfiguration()
            runner = GenewebTestRunner(config)
            scenarios = runner.get_test_scenarios()

            if args.list_categories:
                categories = set(scenario.category for scenario in scenarios)
                print("Available test categories:")
                for category in sorted(categories):
                    count = sum(1 for s in scenarios if s.category == category)
                    print(f"  {category}: {count} tests")

            if args.list_scenarios:
                if args.category:
                    scenarios = [s for s in scenarios if s.category == args.category]
                    print(f"Test scenarios in category '{args.category}':")
                else:
                    print("All test scenarios:")
                for scenario in scenarios:
                    print(f"  {scenario.name}: {scenario.description} ({scenario.category})")

            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

    # Load configuration
    try:
        if args.config.exists():
            config = TestConfiguration.from_file(args.config)
        else:
            config = TestConfiguration()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # Override configuration with command line arguments
    if args.database:
        config.database_name = args.database
    if args.wizard_credentials:
        config.wizard_credentials = args.wizard_credentials

    config.debug = args.debug

    if args.mode == 'cgi':
        config.mode = TestMode.CGI
    elif args.capture:
        config.mode = TestMode.CAPTURE
    elif args.compare:
        config.mode = TestMode.COMPARE
    else:
        config.mode = TestMode.BASIC

    # Create and run tests
    runner = GenewebTestRunner(config)

    try:
        print(f"Starting Geneweb tests for database '{config.database_name}'")

        # Start server if needed
        if not runner._start_gwd_server():
            print("Failed to start gwd server")
            sys.exit(1)

        # Get scenarios and filter by category if specified
        scenarios = runner.get_test_scenarios()
        if args.category:
            scenarios = [s for s in scenarios if s.category == args.category]

        # Run tests
        total_tests = len(scenarios)
        passed = 0
        failed = 0
        skipped = 0

        print(f"Running {total_tests} test scenarios...")

        for i, scenario in enumerate(scenarios, 1):
            result = runner._run_scenario(scenario)

            status_char = {
                TestResult.PASS: "✓",
                TestResult.FAIL: "✗",
                TestResult.SKIP: "○",
                TestResult.ERROR: "✗"
            }[result]

            print(f"[{i:3d}/{total_tests}] {status_char} {scenario.name}")

            if result == TestResult.PASS:
                passed += 1
            elif result in [TestResult.FAIL, TestResult.ERROR]:
                failed += 1
            else:
                skipped += 1

        # Print summary
        print(f"\nTest Summary:")
        print(f"  Total:  {total_tests}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Skipped: {skipped}")

        if config.mode == TestMode.CAPTURE:
            print(f"\nReference files saved to:")
            print(f"  Golden master: {runner.golden_master_dir}/references")
            print(f"  Legacy compat: {runner.reference_dir}")
        elif config.mode == TestMode.COMPARE:
            print(f"\nComparison files saved to: {runner.temp_dir}/run")

        # Check log for critical errors
        if Path(config.gwd_log).exists():
            with open(config.gwd_log, 'r') as f:
                log_content = f.read()
                for condition in config.failing_conditions:
                    if condition in log_content:
                        print(f"\nCRITICAL: Found '{condition}' in log file {config.gwd_log}")
                        failed += 1

        # Exit with appropriate code
        sys.exit(0 if failed == 0 else 1)

    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(1)
    finally:
        runner._stop_gwd_server()


if __name__ == "__main__":
    main()
