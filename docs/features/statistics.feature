@statistics
Feature: Statistical reports and data analysis
  As a genealogist
  I want to view statistical information about the database
  So that I can analyze family data patterns

  # -------------------
  # Smoke Scenarios
  # -------------------
  @smoke
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


  # -------------------
  # Access Control Scenarios
  # -------------------
  Scenario: Restrict statistics for private persons
    Given some persons are marked as private
    When I request database statistics as a regular user
    Then private persons should be excluded from statistical counts

  Scenario: Admin sees all data in statistics
    Given some persons are marked as private
    And I am logged in as an administrator
    When I request database statistics
    Then all persons including private ones should be counted


  # -------------------
  # Error Handling Scenarios
  # -------------------
  Scenario: Handle empty database
    Given the database contains no persons or families
    When I request general statistics
    Then I should see counts of zero for all categories

  Scenario: Handle missing location data
    Given some persons do not have location information
    When I request geographical statistics
    Then only persons with location data should be included
    And a warning should indicate incomplete data


  # -------------------
  # Configuration / Variants
  # -------------------
  Scenario: Limit statistics to a specific database
    Given multiple databases exist
    When I request statistics for the "galichet" database only
    Then I should see statistics restricted to that database

  Scenario: Include historical data if configured
    Given historical events are present in the database
    And statistics include historical data
    When I request general statistics
    Then counts should include both current and historical records


  # -------------------
  # Golden Master Consistency Scenarios
  # -------------------
  Scenario: Preserve statistical output format
    Given the database contains genealogical data
    When I request general statistics multiple times
    Then the layout and ordering of counts should remain consistent

  Scenario: Preserve surname frequency ordering
    Given the database contains multiple surnames
    When I request surname statistics
    Then surnames should be ordered consistently across requests
