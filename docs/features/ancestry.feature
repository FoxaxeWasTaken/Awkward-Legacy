@ancestry
Feature: Ancestry trees and timelines
  As a genealogist
  I want to view ancestry information in various formats
  So that I can understand family lineages

  # -------------------
  # Smoke Scenarios
  # -------------------
  @smoke
  Scenario: Display basic ancestry tree
    Given person ID 26 has ancestors in the database
    When I request a basic ancestry tree with 5 generations
    Then I should see a tree showing ancestors up to 5 generations

  Scenario: Display compact ancestry tree
    Given person ID 26 has ancestors
    When I request a compact ancestry tree with 5 generations
    Then I should see a condensed ancestry tree format

  Scenario: Display ancestry with cousins
    Given person ID 26 has cousins through shared ancestors
    When I request ancestry tree with cousins for 5 generations
    Then I should see ancestors plus cousin relationships

  Scenario: Display fan chart ancestry
    Given person ID 26 has multiple generations of ancestors
    When I request a fan chart ancestry with 5 generations
    Then I should see a circular/fan-shaped ancestry display

  Scenario: Display chronological ancestry with SOSA
    Given person ID 26 has ancestors with dates
    When I request chronological ancestry with SOSA numbering
    Then I should see ancestors ordered by time with SOSA numbers


  # -------------------
  # Access Control Scenarios
  # -------------------
  Scenario: Deny ancestry view for private person
    Given person ID 42 is marked as private
    When I request their ancestry tree
    Then I should be denied access

  Scenario: Admin can view private person ancestry
    Given person ID 42 is marked as private
    And I am logged in as an administrator
    When I request their ancestry tree
    Then I should see full ancestry information


  # -------------------
  # Error Handling Scenarios
  # -------------------
  Scenario: Handle request for unknown person
    Given person ID 9999 does not exist
    When I request their ancestry tree
    Then I should see an error message indicating the person was not found

  Scenario: Handle person without ancestors
    Given person ID 55 exists but has no recorded ancestors
    When I request their ancestry tree
    Then I should see an empty ancestry display


  # -------------------
  # Configuration / Variants
  # -------------------
  Scenario: Limit ancestry depth to configured level
    Given person ID 26 has multiple generations of ancestors
    And the ancestry depth limit is set to 3 generations
    When I request their ancestry tree
    Then I should only see up to 3 generations of ancestors

  Scenario: Display full ancestry when depth is unlimited
    Given person ID 26 has multiple generations of ancestors
    And the ancestry depth limit is unlimited
    When I request their ancestry tree
    Then I should see all available generations


  # -------------------
  # Golden Master Consistency Scenarios
  # -------------------
  Scenario: Preserve ancestor ordering
    Given person ID 26 has multiple ancestors across generations
    When I request the ancestry list
    Then the ancestors should be ordered by generation
    And within each generation, by chronological order

  Scenario: Preserve layout for compact and fan chart views
    Given person ID 26 has multiple generations of ancestors
    When I view ancestry in compact or fan chart format
    Then the layout and structure should remain consistent across requests
