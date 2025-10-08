@regression @person
Feature: Person display and access
  As a user
  I want to view person information
  So that I can learn about individuals in the database

  # -------------------
  # Smoke Scenarios
  # -------------------
  @smoke
  Scenario: Display person basic information
    Given person ID 26 exists in the database
    When I request to display person with ID 26
    Then I should see the person's basic information page

  Scenario: Direct person access by name
    Given person "anthoine geruzet" with occurrence 0 exists
    When I access the person directly by name parameters
    Then I should see the person's detail page

  Scenario: Access person without grandparents
    Given person "anthoine geruzet" exists but has no grandparents
    When I access this person's page
    Then I should see the person page without grandparent information

  Scenario: Access person without parents
    Given person "marie dupond" exists but has no parents
    When I access this person's page
    Then I should see the person page without parent information

  Scenario: Access nonexistent person
    Given no person named "xxx yyy" exists in the database
    When I try to access this nonexistent person
    Then I should receive an appropriate error or empty result


  # -------------------
  # Access Control Scenarios
  # -------------------
  Scenario: Deny access to private person
    Given person "Pauline Durand" is marked as private
    And I am logged in as a regular user
    When I access Pauline Durand's page
    Then I should be denied full access
    And sensitive information should be hidden

  Scenario: Admin can access private person
    Given person "Pauline Durand" is marked as private
    And I am logged in as an administrator
    When I access Pauline Durand's page
    Then I should see full information


  # -------------------
  # Error Handling Scenarios
  # -------------------
  Scenario: Handle missing person record
    Given person ID 9999 does not exist
    When I request to view person ID 9999
    Then I should see an error message indicating the person was not found

  Scenario: Handle malformed person parameters
    Given no person matches the name "!!!@@@"
    When I access this person by name parameters
    Then I should see an appropriate error message


  # -------------------
  # Configuration / Variants
  # -------------------
  Scenario: Display additional fields if configured
    Given person ID 26 exists in the database
    And the system is configured to show notes and sources
    When I view person ID 26
    Then I should see the notes and sources fields along with basic information

  Scenario: Hide optional fields if disabled
    Given person ID 26 exists in the database
    And the system is configured to hide notes and sources
    When I view person ID 26
    Then I should see only the basic information


  # -------------------
  # Golden Master Consistency Scenarios
  # -------------------
  Scenario: Preserve field ordering on person page
    Given person ID 26 exists with multiple fields
    When I view the person's page
    Then the fields should appear in the same order consistently across requests

  Scenario: Preserve page layout for person without parents or grandparents
    Given person "marie dupond" exists without parents or grandparents
    When I view the person's page
    Then the layout should render correctly without missing sections breaking the page
