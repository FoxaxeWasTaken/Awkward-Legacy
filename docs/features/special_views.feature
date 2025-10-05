@special_views
Feature: Special views and advanced displays
  As a genealogist
  I want to access specialized views of genealogical data
  So that I can analyze information in unique ways

  # -------------------
  # Smoke Scenarios
  # -------------------
  @smoke
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


  # -------------------
  # Access Control Scenarios
  # -------------------
  Scenario: Restrict branch view for private persons
    Given a family branch contains private persons
    And I am a regular user
    When I request the branch view
    Then private persons should be hidden from the display

  Scenario: Admin can view all branches including private persons
    Given a family branch contains private persons
    And I am logged in as an administrator
    When I request the branch view
    Then all persons including private ones should be visible


  # -------------------
  # Error Handling Scenarios
  # -------------------
  Scenario: Handle family with no branches
    Given a family exists but has no branches
    When I request the branch view
    Then I should see a message indicating no branches are available

  Scenario: Handle advanced search with no results
    Given complex search criteria that match no persons
    When I perform the advanced search
    Then I should see a message indicating no results found


  # -------------------
  # Configuration / Variants
  # -------------------
  Scenario: Interactive tree with depth limit
    Given a person has an extended family
    And the tree display depth is limited to 3 generations
    When I request the interactive tree view
    Then I should see only 3 generations of family

  Scenario: Full interactive tree without depth limit
    Given a person has an extended family
    And the tree display depth is unlimited
    When I request the interactive tree view
    Then I should see all generations of the family


  # -------------------
  # Golden Master Consistency Scenarios
  # -------------------
  Scenario: Preserve branch ordering
    Given a family has multiple branches
    When I request a branch view
    Then the branches should appear in a consistent order across requests

  Scenario: Preserve interactive tree layout
    Given a person has extended family
    When I view the interactive tree
    Then the layout and node positions should remain consistent
