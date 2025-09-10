@statistics
Feature: Statistical reports and data analysis
  As a genealogist
  I want to view statistical information about the database
  So that I can analyze family data patterns

  Scenario: View general database statistics
    Given the database contains genealogical data
    When I request general statistics
    Then I should see counts of persons, families, and events

  Scenario: View birth and death statistics
    Given the database contains vital records
    When I request birth and death statistics
    Then I should see demographic analysis

  Scenario: View surname frequency statistics
    Given the database contains multiple surnames
    When I request surname statistics
    Then I should see frequency distribution of family names

  Scenario: View geographical statistics
    Given persons have location information
    When I request geographical statistics
    Then I should see location-based data analysis
