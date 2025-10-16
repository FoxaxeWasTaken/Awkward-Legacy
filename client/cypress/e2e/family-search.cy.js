describe('Family Search and Visualization', () => {
  beforeEach(() => {
    // Visit the home page
    cy.visit('/');
  });

  it('should display the main search interface', () => {
    // Check that the main elements are present
    cy.contains('h1', 'Genealogy Family Search').should('be.visible');
    cy.contains('h2', 'Family Search').should('be.visible');
    cy.get('input[placeholder*="Enter family name"]').should('be.visible');
    cy.get('button').contains('Search').should('be.visible');
  });

  it('should show welcome state initially', () => {
    // Check welcome state elements
    cy.contains('Welcome to Family Search').should('be.visible');
    cy.contains('Enter a family name above to search').should('be.visible');
    cy.contains('Search Examples:').should('be.visible');
  });

  it('should handle empty search gracefully', () => {
    // Try to search with empty input
    cy.get('button').contains('Search').click();
    
    // Button should be disabled or no action should occur
    cy.get('input[placeholder*="Enter family name"]').should('have.value', '');
  });

  it('should perform a family search', () => {
    // Mock API response for family search
    cy.intercept('GET', '/api/v1/families/search*', {
      statusCode: 200,
      body: [
        {
          id: '123e4567-e89b-12d3-a456-426614174000',
          husband_name: 'John Doe',
          wife_name: 'Jane Smith',
          marriage_date: '2005-06-20',
          marriage_place: 'New York City',
          children_count: 2,
          summary: 'John Doe & Jane Smith (2005)'
        }
      ]
    }).as('familySearch');

    // Perform search
    cy.get('input[placeholder*="Enter family name"]').type('John');
    cy.get('button').contains('Search').click();

    // Wait for API call
    cy.wait('@familySearch');

    // Check that results are displayed
    cy.contains('Search Results (1)').should('be.visible');
    cy.contains('John Doe & Jane Smith (2005)').should('be.visible');
    cy.contains('Husband: John Doe').should('be.visible');
    cy.contains('Wife: Jane Smith').should('be.visible');
    cy.contains('Children: 2').should('be.visible');
  });

  it('should handle search with no results', () => {
    // Mock API response with no results
    cy.intercept('GET', '/api/v1/families/search*', {
      statusCode: 404,
      body: {
        detail: 'No families found matching the search criteria'
      }
    }).as('noResults');

    // Perform search
    cy.get('input[placeholder*="Enter family name"]').type('Nonexistent');
    cy.get('button').contains('Search').click();

    // Wait for API call
    cy.wait('@noResults');

    // Check that no results message is displayed
    cy.contains('No Families Found').should('be.visible');
    cy.contains('No families match your search criteria').should('be.visible');
  });

  it('should handle API errors gracefully', () => {
    // Mock API error response
    cy.intercept('GET', '/api/v1/families/search*', {
      statusCode: 500,
      body: {
        detail: 'Internal server error'
      }
    }).as('apiError');

    // Perform search
    cy.get('input[placeholder*="Enter family name"]').type('Test');
    cy.get('button').contains('Search').click();

    // Wait for API call
    cy.wait('@apiError');

    // Check that error message is displayed
    cy.contains('Search Error').should('be.visible');
    cy.contains('Internal server error').should('be.visible');
    cy.get('button').contains('Try Again').should('be.visible');
  });

  it('should navigate to family tree view', () => {
    // Mock API responses
    cy.intercept('GET', '/api/v1/families/search*', {
      statusCode: 200,
      body: [
        {
          id: '123e4567-e89b-12d3-a456-426614174000',
          husband_name: 'John Doe',
          wife_name: 'Jane Smith',
          marriage_date: '2005-06-20',
          marriage_place: 'New York City',
          children_count: 2,
          summary: 'John Doe & Jane Smith (2005)'
        }
      ]
    }).as('familySearch');

    cy.intercept('GET', '/api/v1/families/123e4567-e89b-12d3-a456-426614174000/detail', {
      statusCode: 200,
      body: {
        id: '123e4567-e89b-12d3-a456-426614174000',
        husband_id: '456e7890-e89b-12d3-a456-426614174001',
        wife_id: '789e0123-e89b-12d3-a456-426614174002',
        marriage_date: '2005-06-20',
        marriage_place: 'New York City',
        notes: 'First marriage',
        husband: {
          id: '456e7890-e89b-12d3-a456-426614174001',
          first_name: 'John',
          last_name: 'Doe',
          sex: 'M',
          birth_date: '1980-01-01'
        },
        wife: {
          id: '789e0123-e89b-12d3-a456-426614174002',
          first_name: 'Jane',
          last_name: 'Smith',
          sex: 'F',
          birth_date: '1982-05-15'
        },
        children: [
          {
            id: '111e2222-e89b-12d3-a456-426614174003',
            family_id: '123e4567-e89b-12d3-a456-426614174000',
            person_id: '222e3333-e89b-12d3-a456-426614174004',
            person: {
              id: '222e3333-e89b-12d3-a456-426614174004',
              first_name: 'Child',
              last_name: 'Doe',
              sex: 'M',
              birth_date: '2010-01-01'
            }
          }
        ],
        events: []
      }
    }).as('familyDetail');

    // Perform search
    cy.get('input[placeholder*="Enter family name"]').type('John');
    cy.get('button').contains('Search').click();

    // Wait for search results
    cy.wait('@familySearch');

    // Click on family card to view details
    cy.contains('View Family Tree').click();

    // Wait for family detail API call
    cy.wait('@familyDetail');

    // Check that we're on the family tree page
    cy.url().should('include', '/family/123e4567-e89b-12d3-a456-426614174000');
    cy.contains('John Doe & Jane Smith').should('be.visible');
    cy.contains('Back to Search').should('be.visible');
  });

  it('should display family tree visualization', () => {
    // Mock family detail API response
    cy.intercept('GET', '/api/v1/families/123e4567-e89b-12d3-a456-426614174000/detail', {
      statusCode: 200,
      body: {
        id: '123e4567-e89b-12d3-a456-426614174000',
        husband_id: '456e7890-e89b-12d3-a456-426614174001',
        wife_id: '789e0123-e89b-12d3-a456-426614174002',
        marriage_date: '2005-06-20',
        marriage_place: 'New York City',
        notes: 'First marriage',
        husband: {
          id: '456e7890-e89b-12d3-a456-426614174001',
          first_name: 'John',
          last_name: 'Doe',
          sex: 'M',
          birth_date: '1980-01-01'
        },
        wife: {
          id: '789e0123-e89b-12d3-a456-426614174002',
          first_name: 'Jane',
          last_name: 'Smith',
          sex: 'F',
          birth_date: '1982-05-15'
        },
        children: [
          {
            id: '111e2222-e89b-12d3-a456-426614174003',
            family_id: '123e4567-e89b-12d3-a456-426614174000',
            person_id: '222e3333-e89b-12d3-a456-426614174004',
            person: {
              id: '222e3333-e89b-12d3-a456-426614174004',
              first_name: 'Child',
              last_name: 'Doe',
              sex: 'M',
              birth_date: '2010-01-01'
            }
          }
        ],
        events: []
      }
    }).as('familyDetail');

    // Navigate directly to family tree page
    cy.visit('/family/123e4567-e89b-12d3-a456-426614174000');

    // Wait for family detail API call
    cy.wait('@familyDetail');

    // Check that tree visualization elements are present
    cy.get('.tree-svg').should('be.visible');
    cy.contains('Reset View').should('be.visible');
    cy.contains('Fullscreen').should('be.visible');
  });

  it('should handle family tree loading errors', () => {
    // Mock API error response
    cy.intercept('GET', '/api/v1/families/123e4567-e89b-12d3-a456-426614174000/detail', {
      statusCode: 404,
      body: {
        detail: 'Family not found'
      }
    }).as('familyNotFound');

    // Navigate to family tree page
    cy.visit('/family/123e4567-e89b-12d3-a456-426614174000');

    // Wait for API call
    cy.wait('@familyNotFound');

    // Check that error message is displayed
    cy.contains('Error Loading Family Tree').should('be.visible');
    cy.contains('Family not found').should('be.visible');
    cy.get('button').contains('Retry').should('be.visible');
  });

  it('should navigate back from family tree to search', () => {
    // Mock family detail API response
    cy.intercept('GET', '/api/v1/families/123e4567-e89b-12d3-a456-426614174000/detail', {
      statusCode: 200,
      body: {
        id: '123e4567-e89b-12d3-a456-426614174000',
        husband_id: '456e7890-e89b-12d3-a456-426614174001',
        wife_id: '789e0123-e89b-12d3-a456-426614174002',
        marriage_date: '2005-06-20',
        marriage_place: 'New York City',
        notes: 'First marriage',
        husband: {
          id: '456e7890-e89b-12d3-a456-426614174001',
          first_name: 'John',
          last_name: 'Doe',
          sex: 'M',
          birth_date: '1980-01-01'
        },
        wife: {
          id: '789e0123-e89b-12d3-a456-426614174002',
          first_name: 'Jane',
          last_name: 'Smith',
          sex: 'F',
          birth_date: '1982-05-15'
        },
        children: [],
        events: []
      }
    }).as('familyDetail');

    // Navigate to family tree page
    cy.visit('/family/123e4567-e89b-12d3-a456-426614174000');

    // Wait for API call
    cy.wait('@familyDetail');

    // Click back button
    cy.contains('Back to Search').click();

    // Check that we're back on the search page
    cy.url().should('eq', Cypress.config().baseUrl + '/');
    cy.contains('Family Search').should('be.visible');
  });

  it('should be responsive on mobile devices', () => {
    // Set mobile viewport
    cy.viewport(375, 667);

    // Check that elements are still visible and functional
    cy.contains('Family Search').should('be.visible');
    cy.get('input[placeholder*="Enter family name"]').should('be.visible');
    cy.get('button').contains('Search').should('be.visible');

    // Check that search form is responsive
    cy.get('.search-input-group').should('have.css', 'flex-direction', 'column');
  });
});
