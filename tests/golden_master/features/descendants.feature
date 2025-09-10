@descendants
Feature: Descendant trees and lineage displays
  As a genealogist
  I want to view descendant information in various formats
  So that I can track family lineages forward in time

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
