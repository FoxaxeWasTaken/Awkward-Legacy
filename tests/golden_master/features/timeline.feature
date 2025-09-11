@timeline
Feature: Timeline and chronological displays
  As a genealogist
  I want to view events in chronological order
  So that I can understand historical context

  # -------------------
  # Smoke Scenarios
  # -------------------
  @smoke
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


  # -------------------
  # Access Control Scenarios
  # -------------------
  Scenario: Hide private person events from timeline
    Given some events are associated with private persons
    And I am logged in as a regular user
    When I view the timeline
    Then events for private persons should be hidden

  Scenario: Admin can view all events including private persons
    Given some events are associated with private persons
    And I am logged in as an administrator
    When I view the timeline
    Then all events should be visible


  # -------------------
  # Error Handling Scenarios
  # -------------------
  Scenario: Handle events with missing dates
    Given some events do not have dates
    When I request the timeline
    Then events without dates should be excluded
    And a warning should indicate incomplete event data

  Scenario: Handle empty timeline
    Given the database contains no events
    When I request a timeline view
    Then I should see an empty timeline message


  # -------------------
  # Configuration / Variants
  # -------------------
  Scenario: Limit timeline to specific date range
    Given the database contains events from multiple years
    When I request the timeline for the range 1900–1950
    Then only events within 1900–1950 should be displayed

  Scenario: Display events by category if configured
    Given events have types (birth, death, marriage)
    And timeline is configured to group by category
    When I request the timeline
    Then events should be displayed grouped by category


  # -------------------
  # Golden Master Consistency Scenarios
  # -------------------
  Scenario: Preserve event ordering across requests
    Given the database contains multiple events
    When I request the timeline multiple times
    Then the order of events should be consistent

  Scenario: Preserve anniversary display format
    Given persons have anniversaries recorded
    When I request the anniversary timeline
    Then the layout and formatting should remain consistent across requests
