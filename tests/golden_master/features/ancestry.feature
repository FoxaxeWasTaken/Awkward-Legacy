@ancestry
Feature: Ancestry trees and timelines
  As a genealogist
  I want to view ancestry information in various formats
  So that I can understand family lineages

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
