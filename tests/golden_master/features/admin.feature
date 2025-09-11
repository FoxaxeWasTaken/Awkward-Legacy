@admin
Feature: Administrative and database functions
  As a system administrator
  I want to access administrative functions and database information
  So that I can manage the genealogy database

  # -------------------
  # Smoke Scenarios
  # -------------------
  @smoke
  Scenario: Access welcome page
    Given the Geneweb server is running
    When I request the welcome page
    Then I should see the main welcome interface

  Scenario: View base statistics
    Given the galichet database is available
    When I request statistics for the galichet base
    Then I should see database statistics including person count

  Scenario: Browse alphabetical index
    Given the galichet database contains persons
    When I browse the alphabetical index
    Then I should see persons organized alphabetically

  Scenario: Access database selection
    Given multiple databases are available
    When I request the database selection page
    Then I should see available database options

  Scenario: View database maintenance options
    Given I have administrative access
    When I request the maintenance page
    Then I should see database maintenance functions

  Scenario: Check calendar functionality
    Given the calendar feature is enabled
    When I request the calendar view
    Then I should see genealogical calendar information


  # -------------------
  # Access Control Scenarios
  # -------------------
  Scenario: Deny maintenance access without admin rights
    Given I am not logged in as an administrator
    When I request the maintenance page
    Then I should be denied access

  Scenario: Deny database deletion without admin rights
    Given I am logged in as a regular user
    When I attempt to delete a database
    Then the operation should be forbidden


  # -------------------
  # Error Handling Scenarios
  # -------------------
  Scenario: Handle request for non-existent database
    Given the database "unknown_base" does not exist
    When I request statistics for "unknown_base"
    Then I should see an error message indicating the database was not found

  Scenario: Handle empty database statistics
    Given the empty_test database exists and contains no persons
    When I request statistics for the empty_test base
    Then I should see database statistics showing zero persons


  # -------------------
  # Configuration Scenarios
  # -------------------
  Scenario: Hide calendar when disabled
    Given the calendar feature is disabled
    When I request the calendar view
    Then I should see a message that the calendar is not available


  # -------------------
  # Golden Master Consistency Scenarios
  # -------------------
  Scenario: Preserve alphabetical index order
    Given the galichet database contains persons
    When I browse the alphabetical index
    Then I should see persons listed in lexicographic order
    And special characters should be ordered consistently
