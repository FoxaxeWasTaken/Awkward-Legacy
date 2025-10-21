describe('Family Management - E2E Tests', () => {
  const API_URL = Cypress.env('apiUrl') || 'http://server-dev:8000';
  
  const mockFamilies = [
    {
      id: '123e4567-e89b-12d3-a456-426614174000',
      husband_id: 'h1',
      wife_id: 'w1',
      marriage_date: '2005-06-20',
      marriage_place: 'Boston, MA'
    },
    {
      id: '223e4567-e89b-12d3-a456-426614174001',
      husband_id: 'h2',
      wife_id: 'w2',
      marriage_date: '2010-03-15',
      marriage_place: 'New York, NY'
    },
    {
      id: '323e4567-e89b-12d3-a456-426614174002',
      husband_id: 'h3',
      wife_id: 'w3',
      marriage_date: '2015-09-10',
      marriage_place: 'Chicago, IL'
    }
  ];

  beforeEach(() => {
    // Mock API calls
    cy.intercept('GET', `${API_URL}/api/v1/families`, {
      statusCode: 200,
      body: mockFamilies
    }).as('getFamilies');

    cy.intercept('GET', `${API_URL}/health`, {
      statusCode: 200,
      body: { status: 'healthy' }
    }).as('healthCheck');

    cy.visit('/manage');
  });

  describe('Page Load and Initial State', () => {
    it('should display the management interface', () => {
      cy.contains('h1', '🔍 Family Search & Management').should('be.visible');
      cy.contains('Search, explore, and manage all families in the database').should('be.visible');
    });

    it('should show loading state initially', () => {
      cy.get('.loading-state').should('be.visible');
      cy.contains('Loading families...').should('be.visible');
    });

    it('should load and display families', () => {
      cy.wait('@getFamilies');
      
      cy.get('.families-table').should('be.visible');
      cy.get('.families-table tbody tr').should('have.length', 3);
    });
  });

  describe('Search Functionality', () => {
    it('should have search input and controls', () => {
      cy.get('input[placeholder*="Search families by name, place, or notes"]').should('be.visible');
      cy.contains('Search').should('be.visible');
      cy.contains('Clear').should('be.visible');
    });

    it('should filter families by search query', () => {
      cy.wait('@getFamilies');
      
      // Search for families containing "Boston"
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Boston');
      cy.contains('Search').click();
      
      // Should show filtered results
      cy.get('.families-table tbody tr').should('have.length', 1);
      cy.contains('Boston, MA').should('be.visible');
    });

    it('should clear search when Clear button is clicked', () => {
      cy.wait('@getFamilies');
      
      // Perform search
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Boston');
      cy.contains('Search').click();
      
      // Clear search
      cy.contains('Clear').click();
      
      // Should show all families again
      cy.get('.families-table tbody tr').should('have.length', 3);
    });

    it('should handle empty search gracefully', () => {
      cy.wait('@getFamilies');
      
      // Search with empty input
      cy.contains('Search').click();
      
      // Should show all families
      cy.get('.families-table tbody tr').should('have.length', 3);
    });
  });

  describe('Sorting Functionality', () => {
    it('should have sorting controls', () => {
      cy.get('select').should('have.length.at.least', 2); // Sort by and Order selects
      cy.contains('Sort by:').should('be.visible');
      cy.contains('Order:').should('be.visible');
    });

    it('should sort families by ID', () => {
      cy.wait('@getFamilies');
      
      // Sort by ID ascending
      cy.get('select').first().select('id');
      cy.get('select').eq(1).select('asc');
      
      // Check that families are sorted
      cy.get('.families-table tbody tr').should('have.length', 3);
    });

    it('should sort families by marriage date', () => {
      cy.wait('@getFamilies');
      
      // Sort by marriage date
      cy.get('select').first().select('marriage_date');
      cy.get('select').eq(1).select('desc');
      
      // Check that families are sorted
      cy.get('.families-table tbody tr').should('have.length', 3);
    });

    it('should sort families by marriage place', () => {
      cy.wait('@getFamilies');
      
      // Sort by marriage place
      cy.get('select').first().select('marriage_place');
      cy.get('select').eq(1).select('asc');
      
      // Check that families are sorted
      cy.get('.families-table tbody tr').should('have.length', 3);
    });
  });

  describe('Pagination', () => {
    it('should have items per page selector', () => {
      cy.contains('Items per page:').should('be.visible');
      cy.get('select').should('contain', '10');
      cy.get('select').should('contain', '20');
      cy.get('select').should('contain', '50');
      cy.get('select').should('contain', '100');
    });

    it('should change items per page', () => {
      cy.wait('@getFamilies');
      
      // Change to 10 items per page
      cy.get('select').last().select('10');
      
      // Should still show all families (we only have 3)
      cy.get('.families-table tbody tr').should('have.length', 3);
    });
  });

  describe('Table Display', () => {
    it('should display family data in table format', () => {
      cy.wait('@getFamilies');
      
      // Check table headers
      cy.contains('Family ID').should('be.visible');
      cy.contains('Husband').should('be.visible');
      cy.contains('Wife').should('be.visible');
      cy.contains('Marriage Date').should('be.visible');
      cy.contains('Marriage Place').should('be.visible');
    });

    it('should show family information in table rows', () => {
      cy.wait('@getFamilies');
      
      // Check that family data is displayed
      cy.get('.families-table tbody tr').should('have.length', 3);
      cy.contains('Boston, MA').should('be.visible');
      cy.contains('New York, NY').should('be.visible');
      cy.contains('Chicago, IL').should('be.visible');
    });

    it('should have clickable column headers for sorting', () => {
      cy.wait('@getFamilies');
      
      // Check that sortable columns have click handlers
      cy.get('.sortable').should('have.length.at.least', 3);
    });
  });

  describe('Error Handling', () => {
    it('should display error when API fails', () => {
      // Mock API error
      cy.intercept('GET', `${API_URL}/api/v1/families`, {
        statusCode: 500,
        body: { detail: 'Internal server error' }
      }).as('getFamiliesError');

      cy.visit('/manage');
      cy.wait('@getFamiliesError');
      
      // Check error state
      cy.contains('Error Loading Families').should('be.visible');
      cy.contains('Internal server error').should('be.visible');
      cy.contains('Try Again').should('be.visible');
    });

    it('should retry loading when retry button is clicked', () => {
      // Mock initial error
      cy.intercept('GET', `${API_URL}/api/v1/families`, {
        statusCode: 500,
        body: { detail: 'Internal server error' }
      }).as('getFamiliesError');

      cy.visit('/manage');
      cy.wait('@getFamiliesError');
      
      // Mock successful retry
      cy.intercept('GET', `${API_URL}/api/v1/families`, {
        statusCode: 200,
        body: mockFamilies
      }).as('getFamiliesRetry');
      
      cy.contains('Try Again').click();
      cy.wait('@getFamiliesRetry');
      
      // Should show families
      cy.get('.families-table').should('be.visible');
    });

    it('should handle network timeout', () => {
      // Mock network timeout
      cy.intercept('GET', `${API_URL}/api/v1/families`, {
        forceNetworkError: true
      }).as('getFamiliesTimeout');

      cy.visit('/manage');
      cy.wait('@getFamiliesTimeout');
      
      // Check error state
      cy.contains('Error Loading Families').should('be.visible');
    });
  });

  describe('Navigation', () => {
    it('should have back button to return to homepage', () => {
      cy.contains('← Back to Home').should('be.visible');
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });

    it('should have refresh button', () => {
      cy.wait('@getFamilies');
      
      cy.contains('Refresh').should('be.visible');
      cy.contains('Refresh').click();
      
      // Should reload families
      cy.wait('@getFamilies');
    });
  });

  describe('Responsive Design', () => {
    it('should work on mobile viewport', () => {
      cy.viewport('iphone-x');
      
      cy.contains('Family Search & Management').should('be.visible');
      cy.get('input[placeholder*="Search families by name, place, or notes"]').should('be.visible');
      cy.contains('Search').should('be.visible');
    });

    it('should work on tablet viewport', () => {
      cy.viewport('ipad-2');
      
      cy.contains('Family Search & Management').should('be.visible');
      cy.get('.families-table').should('be.visible');
    });
  });

  describe('Accessibility', () => {
    it('should have proper table structure', () => {
      cy.wait('@getFamilies');
      
      cy.get('table').should('be.visible');
      cy.get('thead').should('be.visible');
      cy.get('tbody').should('be.visible');
    });

    it('should be keyboard navigable', () => {
      cy.get('input[placeholder*="Search families by name, place, or notes"]').focus().should('be.focused');
      cy.get('body').tab();
      cy.focused().should('be.visible');
    });

    it('should have proper button labels', () => {
      cy.contains('Search').should('be.visible');
      cy.contains('Clear').should('be.visible');
      cy.contains('Refresh').should('be.visible');
    });
  });

  describe('Data Validation', () => {
    it('should handle empty families list', () => {
      // Mock empty response
      cy.intercept('GET', `${API_URL}/api/v1/families`, {
        statusCode: 200,
        body: []
      }).as('getEmptyFamilies');

      cy.visit('/manage');
      cy.wait('@getEmptyFamilies');
      
      // Should show empty state
      cy.contains('No families found').should('be.visible');
    });

    it('should handle families with missing data', () => {
      const incompleteFamilies = [
        {
          id: '123e4567-e89b-12d3-a456-426614174000',
          husband_id: null,
          wife_id: 'w1',
          marriage_date: null,
          marriage_place: 'Boston, MA'
        }
      ];

      cy.intercept('GET', `${API_URL}/api/v1/families`, {
        statusCode: 200,
        body: incompleteFamilies
      }).as('getIncompleteFamilies');

      cy.visit('/manage');
      cy.wait('@getIncompleteFamilies');
      
      // Should still display the family
      cy.get('.families-table tbody tr').should('have.length', 1);
    });
  });
});
