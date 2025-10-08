@smoke @search
Feature: Search functionality
  As a genealogist
  I want to search for persons in the database
  So that I can find specific individuals

  # -------------------
  # Smoke Scenarios
  # -------------------
  @smoke
  Scenario: Search for existing person
    Given the Geneweb database contains person "anthoine geruzet"
    When I search for "anthoine+geruzet"
    Then I should see search results with matching persons

  Scenario: Search by partial name
    Given the Geneweb database contains persons "Jean Dupont" and "Jean Duval"
    When I search for "Jean D"
    Then I should see both matching persons in the results

  Scenario: Search is case-insensitive
    Given the Geneweb database contains person "Marie Dubois"
    When I search for "marie dubois"
    Then I should see "Marie Dubois" in the results


  # -------------------
  # Access Control Scenarios
  # -------------------
  Scenario: Do not show private persons in search for regular users
    Given person "Pauline Durand" is marked as private
    When I search for "Pauline Durand" as a regular user
    Then I should not see her in the search results

  Scenario: Admin can see private persons in search
    Given person "Pauline Durand" is marked as private
    And I am logged in as an administrator
    When I search for "Pauline Durand"
    Then I should see her in the search results


  # -------------------
  # Error Handling Scenarios
  # -------------------
  Scenario: Search for nonexistent person
    Given no person named "xxx yyy" exists in the database
    When I search for "xxx yyy"
    Then I should see an empty search result or an appropriate message

  Scenario: Handle malformed search query
    Given the database contains multiple persons
    When I search for "!!!@@@"
    Then I should see a message indicating invalid search input or no results


  # -------------------
  # Configuration / Variants
  # -------------------
  Scenario: Limit search results to top N matches
    Given the database contains many matching persons
    And the search is configured to return at most 5 results
    When I search for "Jean"
    Then I should see only the top 5 matching persons

  Scenario: Search with extended matching enabled
    Given the database contains "Jean Dupont" and "Jean Duval"
    And extended matching is enabled
    When I search for "J Dupont"
    Then I should see "Jean Dupont" in the results


  # -------------------
  # Golden Master Consistency Scenarios
  # -------------------
  Scenario: Preserve search result ordering
    Given the database contains multiple persons matching "Jean"
    When I search for "Jean"
    Then the ordering of results should be consistent across repeated searches

  Scenario: Preserve search output formatting
    Given the database contains person "Marie Dubois"
    When I search for "Marie Dubois"
    Then the result display should match the current system format
