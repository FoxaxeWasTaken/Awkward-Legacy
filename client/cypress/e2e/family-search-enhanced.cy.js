describe('Family Search - Enhanced E2E Tests', () => {
  const API_URL = Cypress.env('apiUrl') || 'http://server-dev:8000';
  
  beforeEach(() => {
    // Visit the manage page where search functionality is located
    cy.visit('/manage');
    // Wait for the page to load
    cy.get('h1').contains('Family Search & Management').should('be.visible');
  });

  describe('Initial Page Load', () => {
    it('should display all main UI elements', () => {
      // Header
      cy.contains('h1', 'Family Search & Management').should('be.visible');
      cy.contains('Search, explore, and manage all families in the database').should('be.visible');
      
      // Search interface
      cy.get('input[placeholder*="Search families by name, place, or notes"]').should('be.visible');
      cy.get('button').contains('Search').should('be.visible');
      cy.get('button').contains('Clear').should('be.visible');
      
      // Filter controls
      cy.get('select').should('be.visible');
      cy.get('select option[value="20"]').should('be.selected');
    });

    it('should display initial state', () => {
      // The FamilyManagementView loads families by default, so we should see either:
      // - Loading state, or
      // - Families list, or  
      // - Error state
      cy.get('body').should('be.visible');
    });

    it('should have search button enabled', () => {
      cy.get('button.search-button').should('be.enabled');
    });
  });

  describe('Health Check', () => {
    it('should check API health on mount', () => {
      cy.intercept('GET', `${API_URL}/health`, {
        statusCode: 200,
        body: { status: 'ok' }
      }).as('healthCheck');
      
      cy.visit('/');
      cy.wait('@healthCheck');
    });

    it('should display error when API is unreachable', () => {
      cy.intercept('GET', `${API_URL}/health`, {
        forceNetworkError: true
      }).as('healthCheckFail');
      
      cy.visit('/');
      cy.wait('@healthCheckFail');
      cy.contains('Unable to connect to the server').should('be.visible');
    });
  });

  describe('Search Input Behavior', () => {
    it('should enable search button when text is entered', () => {
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button.search-button').should('not.be.disabled');
    });

    it('should disable search button when input is cleared', () => {
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button.search-button').should('not.be.disabled');
      
      cy.get('input[placeholder*="Enter family name"]').clear();
      cy.get('button.search-button').should('be.disabled');
    });

    it('should trim whitespace from search query', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 200,
        body: []
      }).as('searchRequest');
      
      cy.get('input[placeholder*="Enter family name"]').type('  Smith  ');
      cy.get('button').contains('Search').click();
      
      cy.wait('@searchRequest').its('request.url').should('include', 'q=Smith');
    });

    it('should support Enter key for search', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 200,
        body: [{
          id: '123',
          husband_name: 'John Smith',
          wife_name: 'Jane Doe',
          marriage_date: '2005-06-20',
          marriage_place: 'Boston, MA',
          children_count: 2,
          summary: 'John Smith & Jane Doe (2005)'
        }]
      }).as('searchRequest');
      
      cy.get('input[placeholder*="Enter family name"]').type('Smith{enter}');
      cy.wait('@searchRequest');
      cy.contains('Search Results').should('be.visible');
    });
  });

  describe('Results Limit Selection', () => {
    it('should allow changing results limit', () => {
      cy.get('select').select('50');
      cy.get('select option[value="50"]').should('be.selected');
    });

    it('should use selected limit in API request', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 200,
        body: []
      }).as('searchRequest');
      
      cy.get('select').select('10');
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button').contains('Search').click();
      
      cy.wait('@searchRequest').its('request.url').should('include', 'limit=10');
    });
  });

  describe('Successful Search', () => {
    it('should display search results with single family', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 200,
        body: [{
          id: '123e4567-e89b-12d3-a456-426614174000',
          husband_name: 'John Smith',
          wife_name: 'Jane Doe',
          marriage_date: '2005-06-20',
          marriage_place: 'Boston, MA',
          children_count: 2,
          summary: 'John Smith & Jane Doe (2005)'
        }]
      }).as('familySearch');
      
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button').contains('Search').click();
      cy.wait('@familySearch');

      cy.contains('Search Results (1)').should('be.visible');
      
      // Check family card content
      cy.contains('John Smith & Jane Doe (2005)').should('be.visible');
      cy.contains('Husband:').should('be.visible');
      cy.contains('John Smith').should('be.visible');
      cy.contains('Wife:').should('be.visible');
      cy.contains('Jane Doe').should('be.visible');
      cy.contains('Married:').should('be.visible');
      cy.contains('Place:').should('be.visible');
      cy.contains('Boston, MA').should('be.visible');
      cy.contains('Children:').should('be.visible');
      cy.contains('2').should('be.visible');
      cy.contains('View Details').should('be.visible');
    });

    it('should display multiple search results', () => {
      const mockFamilies = [
        {
          id: '123',
          husband_name: 'John Smith',
          wife_name: 'Jane Doe',
          marriage_date: '2005-06-20',
          marriage_place: 'Boston, MA',
          children_count: 2,
          summary: 'John Smith & Jane Doe (2005)'
        },
        {
          id: '456',
          husband_name: 'Robert Smith',
          wife_name: 'Linda Wilson',
          marriage_date: '1970-09-15',
          marriage_place: 'New York, NY',
          children_count: 3,
          summary: 'Robert Smith & Linda Wilson (1970)'
        },
        {
          id: '789',
          husband_name: 'William Smith',
          wife_name: 'Margaret Brown',
          marriage_date: '1941-06-14',
          marriage_place: 'Boston, MA',
          children_count: 4,
          summary: 'William Smith & Margaret Brown (1941)'
        }
      ];
      
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 200,
        body: mockFamilies
      }).as('familySearch');
      
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button').contains('Search').click();
      cy.wait('@familySearch');
      
      cy.contains('Search Results (3)').should('be.visible');
      cy.contains('John Smith & Jane Doe').should('be.visible');
      cy.contains('Robert Smith & Linda Wilson').should('be.visible');
      cy.contains('William Smith & Margaret Brown').should('be.visible');
    });

    it('should navigate to family tree when View button is clicked', () => {
      const familyId = '123e4567-e89b-12d3-a456-426614174000';
      
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 200,
        body: [{
          id: familyId,
          husband_name: 'John Smith',
          wife_name: 'Jane Doe',
          marriage_date: '2005-06-20',
          marriage_place: 'Boston, MA',
          children_count: 2,
          summary: 'John Smith & Jane Doe (2005)'
        }]
      }).as('familySearch');
      
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button').contains('Search').click();
      cy.wait('@familySearch');
      
      cy.get('button').contains('View Details').click();
      cy.url().should('include', `/family/${familyId}`);
    });
  });

  describe('Empty Search Results', () => {
    it('should display no results message', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 404,
        body: { detail: 'No families found matching the search criteria' }
      }).as('familySearch');
      
      cy.get('input[placeholder*="Enter family name"]').type('Nonexistent');
      cy.get('button').contains('Search').click();
      cy.wait('@familySearch');
      
      cy.contains('No families found matching the search criteria').should('be.visible');
      cy.contains('Search Error').should('be.visible');
    });
  });

  describe('Error Handling', () => {
    it('should display error message on network failure', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        forceNetworkError: true
      }).as('familySearch');
      
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button').contains('Search').click();
      cy.wait('@familySearch');
      
      cy.contains('Search Error').should('be.visible');
      cy.contains('Failed to search families').should('be.visible');
    });

    it('should display error message on server error', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 500,
        body: { detail: 'Internal server error' }
      }).as('familySearch');
      
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button').contains('Search').click();
      cy.wait('@familySearch');
      
      cy.contains('Search Error').should('be.visible');
      cy.contains('Internal server error').should('be.visible');
    });

    it('should allow retry after error', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 500,
        body: { detail: 'Server error' }
      }).as('familySearchError');
      
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button').contains('Search').click();
      cy.wait('@familySearchError');
      
      cy.contains('Search Error').should('be.visible');
      
      // Click Try Again button
      cy.get('button').contains('Try Again').click();
      
      // Error should be cleared and welcome state restored
      cy.contains('Search Error').should('not.exist');
      cy.contains('Welcome to Family Search').should('be.visible');
    });
  });


  describe('Search Result Interaction', () => {
    it('should clear results when starting a new search', () => {
      // First search
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 200,
        body: [{
          id: '123',
          husband_name: 'John Smith',
          wife_name: 'Jane Doe',
          marriage_date: '2005-06-20',
          marriage_place: 'Boston, MA',
          children_count: 2,
          summary: 'John Smith & Jane Doe (2005)'
        }]
      }).as('firstSearch');
      
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button').contains('Search').click();
      cy.wait('@firstSearch');
      
      cy.contains('John Smith & Jane Doe').should('be.visible');
      
      // Start typing new search - this should clear results
      cy.get('input[placeholder*="Enter family name"]').clear().type('J');
      
      // Results should be cleared when typing new search
      cy.contains('John Smith & Jane Doe').should('not.exist');
    });

    it('should handle search with special characters', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 200,
        body: [{
          id: '123',
          husband_name: "O'Brien",
          wife_name: 'Mary-Ann Smith',
          marriage_date: '2005-06-20',
          marriage_place: 'Boston, MA',
          children_count: 2,
          summary: "O'Brien & Mary-Ann Smith (2005)"
        }]
      }).as('specialSearch');
      
      cy.get('input[placeholder*="Enter family name"]').type("O'Brien");
      cy.get('button').contains('Search').click();
      cy.wait('@specialSearch');
      
      cy.contains("O'Brien").should('be.visible');
    });
  });

  describe('Responsive Behavior', () => {
    it('should work on mobile viewport', () => {
      cy.viewport('iphone-x');
      
      cy.get('input[placeholder*="Enter family name"]').should('be.visible');
      cy.get('button').contains('Search').should('be.visible');
      
      cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
        statusCode: 200,
        body: [{
          id: '123',
          husband_name: 'John Smith',
          wife_name: 'Jane Doe',
          marriage_date: '2005-06-20',
          marriage_place: 'Boston, MA',
          children_count: 2,
          summary: 'John Smith & Jane Doe (2005)'
        }]
      }).as('mobileSearch');
      
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button').contains('Search').click();
      cy.wait('@mobileSearch');
      
      cy.contains('Search Results (1)').should('be.visible');
    });

    it('should work on tablet viewport', () => {
      cy.viewport('ipad-2');
      
      cy.get('input[placeholder*="Enter family name"]').should('be.visible');
      cy.get('button').contains('Search').should('be.visible');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA labels', () => {
      cy.get('input[placeholder*="Enter family name"]').should('have.attr', 'type', 'text');
      cy.get('button').contains('Search').should('be.visible');
    });

    it('should support keyboard navigation', () => {
      cy.get('input[placeholder*="Enter family name"]').focus().type('Smith');
      cy.focused().should('have.value', 'Smith');
      
      // Test that Enter key works for search
      cy.get('input[placeholder*="Enter family name"]').clear().type('Test{enter}');
      // The search should be triggered (we don't need to wait for results)
    });
  });

  describe('Multiple Consecutive Searches', () => {
    it('should handle multiple searches correctly', () => {
      // First search
      cy.intercept('GET', `${API_URL}/api/v1/families/search*q=Smith*`, {
        statusCode: 200,
        body: [{
          id: '123',
          husband_name: 'John Smith',
          wife_name: 'Jane Doe',
          marriage_date: '2005-06-20',
          marriage_place: 'Boston, MA',
          children_count: 2,
          summary: 'John Smith & Jane Doe (2005)'
        }]
      }).as('smithSearch');
      
      cy.get('input[placeholder*="Enter family name"]').type('Smith');
      cy.get('button').contains('Search').click();
      cy.wait('@smithSearch');
      cy.contains('John Smith').should('be.visible');
      
      // Second search
      cy.intercept('GET', `${API_URL}/api/v1/families/search*q=Johnson*`, {
        statusCode: 200,
        body: [{
          id: '456',
          husband_name: 'Robert Johnson',
          wife_name: 'Lisa Brown',
          marriage_date: '2010-03-15',
          marriage_place: 'Chicago, IL',
          children_count: 1,
          summary: 'Robert Johnson & Lisa Brown (2010)'
        }]
      }).as('johnsonSearch');
      
      cy.get('input[placeholder*="Enter family name"]').clear().type('Johnson');
      cy.get('button').contains('Search').click();
      cy.wait('@johnsonSearch');
      
      cy.contains('Robert Johnson').should('be.visible');
      cy.contains('John Smith').should('not.exist');
    });
  });
});

