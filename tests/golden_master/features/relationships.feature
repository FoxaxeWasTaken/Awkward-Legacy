@relationships
Feature: Relationship calculations and displays
  As a genealogist
  I want to understand relationships between persons
  So that I can determine family connections

  # -------------------
  # Smoke Scenarios
  # -------------------
  @smoke
  Scenario: Calculate relationship between two persons
    Given two persons exist in the database
    When I request the relationship calculation
    Then I should see how they are related

  Scenario: Display relationship with details
    Given two related persons exist
    When I request detailed relationship information
    Then I should see the relationship path and degree

  Scenario: Find common ancestors
    Given two persons share ancestors
    When I search for their common ancestors
    Then I should see their shared ancestral connections


  # -------------------
  # Access Control Scenarios
  # -------------------
  Scenario: Restrict relationship calculation for private persons
    Given person ID 42 is marked as private
    And person ID 43 is public
    When I request the relationship between ID 42 and ID 43
    Then the system should hide or restrict private person information

  Scenario: Admin can calculate relationships including private persons
    Given person ID 42 is marked as private
    And person ID 43 is public
    And I am logged in as an administrator
    When I request the relationship between ID 42 and ID 43
    Then I should see full relationship details


  # -------------------
  # Error Handling Scenarios
  # -------------------
  Scenario: Handle unknown persons in relationship calculation
    Given person ID 9999 does not exist
    And person ID 26 exists
    When I request their relationship
    Then I should see an error message indicating the unknown person

  Scenario: Handle persons with no shared ancestry
    Given person ID 26 and person ID 27 exist
    And they have no common ancestors
    When I search for their common ancestors
    Then I should see a message indicating no shared ancestry


  # -------------------
  # Configuration / Variants
  # -------------------
  Scenario: Display relationship using full generational path
    Given two persons exist with multi-generation lineage
    And the system is configured to show full lineage
    When I request the relationship
    Then I should see all intermediate generations in the relationship path

  Scenario: Display relationship using minimal generation summary
    Given two persons exist with multi-generation lineage
    And the system is configured to show minimal summary
    When I request the relationship
    Then I should see only the degree of relationship without intermediate generations


  # -------------------
  # Golden Master Consistency Scenarios
  # -------------------
  Scenario: Preserve relationship calculation order
    Given two persons exist with multiple shared ancestors
    When I request their relationship
    Then the calculation output should be consistent across multiple requests

  Scenario: Preserve formatting of detailed relationship display
    Given two related persons exist
    When I request detailed relationship information
    Then the displayed path and degree should match the current system layout
