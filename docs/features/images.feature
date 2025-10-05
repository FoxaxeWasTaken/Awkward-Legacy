@images
Feature: Image and media handling
  As a user
  I want to view and manage images associated with persons
  So that I can see visual representations of family members

  # -------------------
  # Smoke Scenarios
  # -------------------
  @smoke
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


  # -------------------
  # Access Control Scenarios
  # -------------------
  Scenario: Deny access to private person image
    Given person ID 42 is marked as private
    And person ID 42 has an associated image
    When I view their profile
    Then I should not see their image

  Scenario: Restrict image gallery for non-authenticated user
    Given the database contains person images marked as private
    And I am not logged in
    When I request the image gallery
    Then I should only see public images


  # -------------------
  # Error Handling Scenarios
  # -------------------
  Scenario: Handle missing image file
    Given person ID 55 has an associated image reference
    And the image file is missing from the server
    When I view the person's profile
    Then I should see a placeholder image

  Scenario: Handle invalid image format
    Given person ID 77 has an associated image in an unsupported format
    When I view their profile
    Then I should see a message indicating the image cannot be displayed


  # -------------------
  # Configuration Scenarios
  # -------------------
  Scenario: Display images as thumbnails in gallery mode
    Given the database contains multiple person images
    And the gallery display mode is set to thumbnails
    When I request the image gallery
    Then I should see thumbnails for each image

  Scenario: Display images as full-size in gallery mode
    Given the database contains multiple person images
    And the gallery display mode is set to full-size
    When I request the image gallery
    Then I should see full-size images


  # -------------------
  # Golden Master Consistency Scenarios
  # -------------------
  Scenario: Preserve image ordering in gallery
    Given the database contains multiple person images
    When I request the image gallery
    Then the images should be displayed in a consistent order
    And subsequent requests should return the same ordering
