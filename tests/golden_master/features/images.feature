@images
Feature: Image and media handling
  As a user
  I want to view and manage images associated with persons
  So that I can see visual representations of family members

  Scenario: Display person with image
    Given person ID 26 has an associated image
    When I view the person's profile
    Then I should see their image displayed

  Scenario: Browse image gallery
    Given the database contains multiple person images
    When I request the image gallery
    Then I should see a collection of person images

  Scenario: View image in different sizes
    Given a person has an image
    When I request different image sizes
    Then I should see the image in various resolutions
