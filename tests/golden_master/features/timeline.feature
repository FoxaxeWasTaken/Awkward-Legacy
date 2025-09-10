@timeline
Feature: Timeline and chronological displays
  As a genealogist
  I want to view events in chronological order
  So that I can understand historical context

  Scenario: Display basic timeline
    Given the database contains events with dates
    When I request a basic timeline view
    Then I should see events ordered chronologically

  Scenario: Display anniversary timeline
    Given persons have birth and death dates
    When I request an anniversary timeline
    Then I should see anniversaries organized by date

  Scenario: Display family timeline
    Given a family has multiple events
    When I request a family-specific timeline
    Then I should see family events in chronological order
