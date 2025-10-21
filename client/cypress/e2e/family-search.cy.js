describe('Family Search and Visualization', () => {
  beforeEach(() => {
    // Visit the home page
    cy.visit('/');
  });

  it('should display the main homepage interface', () => {
    // Check that the main elements are present
    cy.contains('h1', '🏛️ Geneweb').should('be.visible');
    cy.contains('Upload Family File').should('be.visible');
    cy.contains('Search & Manage Families').should('be.visible');
  });

  it('should show action cards on homepage', () => {
    // Check that action cards are present
    cy.contains('Upload Family File').should('be.visible');
    cy.contains('Search & Manage Families').should('be.visible');
    cy.contains('Upload File').should('be.visible');
    cy.contains('Explore Families').should('be.visible');
  });

  it('should navigate to manage page when clicking Explore Families', () => {
    // Click the Explore Families button
    cy.contains('Explore Families').click();
    
    // Should navigate to manage page
    cy.url().should('include', '/manage');
    cy.contains('Family Search & Management').should('be.visible');
  });

  it('should perform a family search on manage page', () => {
    // Navigate to manage page first
    cy.visit('/manage');
    
    // Mock API response for loading families
    cy.intercept('GET', '/api/v1/families', {
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
        },
        {
          id: '223e4567-e89b-12d3-a456-426614174001',
          husband_name: 'Bob Wilson',
          wife_name: 'Alice Brown',
          marriage_date: '2010-03-15',
          marriage_place: 'Boston, MA',
          children_count: 1,
          summary: 'Bob Wilson & Alice Brown (2010)'
        }
      ]
    }).as('loadFamilies');

    // Wait for the page to load and show the table
    cy.get('.families-table').should('be.visible');
    
    // Wait a bit for the API call to complete
    cy.wait(1000);

    // Perform search (client-side filtering)
    cy.get('input[placeholder*="Search families by name, place, or notes"]').type('John');
    cy.get('button').contains('Search').click();

    // Check that filtered results are displayed in the table
    cy.get('.families-table tbody tr').should('have.length', 1);
    cy.contains('John Doe').should('be.visible');
    cy.contains('Jane Smith').should('be.visible');
    cy.contains('New York City').should('be.visible');
  });

  it('should handle search with no results', () => {
    // Navigate to manage page first
    cy.visit('/manage');
    
    // Mock API response with some families
    cy.intercept('GET', '/api/v1/families', {
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
    }).as('loadFamilies');

    // Wait for the page to load and show the table
    cy.get('.families-table').should('be.visible');
    
    // Wait a bit for the API call to complete
    cy.wait(1000);

    // Perform search for non-existent family
    cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Nonexistent');
    cy.get('button').contains('Search').click();

    // Check that no results are displayed in the table
    cy.get('.families-table tbody tr').should('have.length', 0);
    // The table should be empty, showing no rows
  });

  it('should handle API errors gracefully', () => {
    // Navigate to manage page first
    cy.visit('/manage');
    
    // Mock API error response for loading families
    cy.intercept('GET', '/api/v1/families', {
      statusCode: 500,
      body: {
        detail: 'Internal server error'
      }
    }).as('apiError');

    // Wait for error state to appear
    cy.contains('Error Loading Families').should('be.visible');
    cy.contains('Internal server error').should('be.visible');
    cy.get('button').contains('Try Again').should('be.visible');
  });

  it('should navigate to family tree view', () => {
    // Navigate to manage page first
    cy.visit('/manage');
    
    // Mock API responses for loading families
    cy.intercept('GET', '/api/v1/families', {
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
    }).as('loadFamilies');

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

    // Wait for the page to load and show the table
    cy.get('.families-table').should('be.visible');
    
    // Wait a bit for the API call to complete
    cy.wait(1000);

    // Click on the "View Tree" button in the table
    cy.get('.families-table tbody tr').first().within(() => {
      cy.get('button').contains('View Tree').click();
    });

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
    cy.get('.tree-container').should('be.visible');
    cy.get('button[title="Reset View"]').should('be.visible');
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

    // Navigate to manage page
    cy.visit('/manage');

    // Check that elements are still visible and functional
    cy.contains('Family Search & Management').should('be.visible');
    cy.get('input[placeholder*="Search families by name, place, or notes"]').should('be.visible');
    cy.get('button').contains('Search').should('be.visible');

    // Check that search form is responsive
    cy.get('.search-input-group').should('have.css', 'flex-direction', 'column');
  });
});
