@relationships
Feature: Relationship calculations and displays
  As a genealogist
  I want to understand relationships between persons
  So that I can determine family connections

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
