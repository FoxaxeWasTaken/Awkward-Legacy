@descendants
Feature: Descendant trees and lineage displays
  As a genealogist
  I want to view descendant information in various formats
  So that I can track family lineages forward in time

  # -------------------
  # Smoke Scenarios
  # -------------------
  @smoke
  Scenario: Display basic descendant tree
    Given person ID 26 has descendants in the database
    When I request a basic descendant tree
    Then I should see descendants organized in a tree structure

  Scenario: Display descendant tree with titles
    Given person ID 26 has descendants with titles
    When I request descendant tree with title display
    Then I should see descendants with their titles shown

  Scenario: Display horizontal descendant tree
    Given person ID 26 has descendants
    When I request a horizontal descendant tree layout
    Then I should see descendants arranged horizontally

  Scenario: Display descendant table format
    Given person ID 26 has descendants
    When I request descendants in table format
    Then I should see descendants organized in a tabular layout


  # -------------------
  # Access Control Scenarios
  # -------------------
  Scenario: Deny descendant tree for private person
    Given person ID 42 is marked as private
    When I request their descendant tree
    Then I should be denied access

  Scenario: Restrict descendant details for non-admin
    Given person ID 42 has descendants
    And person ID 42 is marked as private
    And I am logged in as a regular user
    When I request their descendant table
    Then I should see restricted information only


  # -------------------
  # Error Handling Scenarios
  # -------------------
  Scenario: Handle request for person with no descendants
    Given person ID 99 exists but has no recorded descendants
    When I request a descendant tree
    Then I should see a message indicating no descendants are available

  Scenario: Handle request for unknown person ID
    Given person ID 9999 does not exist
    When I request a descendant tree
    Then I should see an error message indicating the person was not found


  # -------------------
  # Configuration Scenarios
  # -------------------
  Scenario: Limit descendant depth to configured level
    Given person ID 26 has multiple generations of descendants
    And the descendant depth limit is set to 2 generations
    When I request their descendant tree
    Then I should only see 2 generations of descendants

  Scenario: Display full descendant lineage when depth is unlimited
    Given person ID 26 has multiple generations of descendants
    And the descendant depth limit is unlimited
    When I request their descendant tree
    Then I should see all available generations


  # -------------------
  # Golden Master Consistency Scenarios
  # -------------------
  Scenario: Preserve descendant ordering
    Given person ID 26 has multiple descendants across generations
    When I request the descendant tree
    Then descendants should be ordered by generation
    And within each generation, by chronological order
