@special_views
Feature: Special views and advanced displays
  As a genealogist
  I want to access specialized views of genealogical data
  So that I can analyze information in unique ways

  Scenario: Display family branches
    Given a family has multiple branches
    When I request a branch view
    Then I should see family organized by branches

  Scenario: View cousin connections
    Given persons have cousin relationships
    When I request cousin connections
    Then I should see how cousins are related

  Scenario: Display name variations
    Given persons have name variations
    When I search for name variations
    Then I should see different spellings and forms

  Scenario: View advanced search results
    Given complex search criteria
    When I perform an advanced search
    Then I should see filtered results matching all criteria

  Scenario: Display interactive family tree
    Given a person has extended family
    When I request an interactive tree view
    Then I should see a navigable family tree interface
