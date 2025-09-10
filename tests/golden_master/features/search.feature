@smoke @search
Feature: Search functionality
  As a genealogist
  I want to search for persons in the database
  So that I can find specific individuals

  Scenario: Search for existing person
    Given the Geneweb database contains person "anthoine geruzet"
    When I search for "anthoine+geruzet"
    Then I should see search results with matching persons
