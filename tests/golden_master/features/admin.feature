@admin
Feature: Administrative and database functions
  As a system administrator
  I want to access administrative functions and database information
  So that I can manage the genealogy database

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
