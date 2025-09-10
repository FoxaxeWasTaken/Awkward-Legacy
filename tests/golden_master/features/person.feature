@regression @person
Feature: Person display and access
  As a user
  I want to view person information
  So that I can learn about individuals in the database

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
