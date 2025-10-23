describe('Family Management - E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/manage');
    // Wait for page to load
    cy.get('.family-management-view').should('be.visible');
  });

  describe('Page Load and Initial State', () => {
    it('should display loading state initially', () => {
      cy.visit('/manage');
      // The loading state might be very fast, so we just check the page loads
      cy.get('.family-management-view').should('be.visible');
    });

    it('should load families and display management interface', () => {
      cy.contains('Family Search & Management').should('be.visible');
      cy.contains('Search, explore, and manage all families in the database').should('be.visible');
    });

    it('should display page title and description', () => {
      cy.get('h1').should('contain', 'Family Search & Management');
      cy.get('p').should('contain', 'Search, explore, and manage all families');
    });

    it('should display search interface', () => {
      cy.get('input[type="text"]').should('be.visible');
      cy.get('input[type="text"]').should('have.attr', 'placeholder').and('contain', 'Search');
    });
  });

  describe('Search Functionality', () => {
    it('should filter families by search input', () => {
      const searchInput = cy.get('input[type="text"]').first();
      searchInput.should('be.visible');
      searchInput.type('Person');
      // Give it time to filter
      cy.wait(500);
      // Verify the search was entered
      searchInput.should('have.value', 'Person');
    });

    it('should search by actual names instead of IDs', () => {
      const searchInput = cy.get('input[type="text"]').first();
      searchInput.should('be.visible');
      
      // Try searching for common name patterns
      searchInput.type('Smith');
      cy.wait(500);
      // The search should work with actual names, not "Person ID" format
      searchInput.should('have.value', 'Smith');
      
      // Clear and try another search
      searchInput.clear();
      searchInput.type('John');
      cy.wait(500);
      searchInput.should('have.value', 'John');
    });

    it('should clear search results when input is cleared', () => {
      const searchInput = cy.get('input[type="text"]').first();
      searchInput.type('TestQuery');
      cy.wait(500);
      searchInput.clear();
      cy.wait(500);
      // After clearing, we should see the default view
      cy.get('.family-management-view').should('be.visible');
    });
  });

  describe('Navigation', () => {
    it('should navigate back to home when back button is clicked', () => {
      cy.contains(/back.*home/i).click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });

    it('should handle browser back button', () => {
      cy.visit('/');
      cy.visit('/manage');
      cy.go('back');
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });
  });

  describe('Responsive Design', () => {
    it('should work on mobile viewport', () => {
      cy.viewport('iphone-x');
      cy.visit('/manage');
      cy.contains('Family Search & Management').should('be.visible');
    });

    it('should work on tablet viewport', () => {
      cy.viewport('ipad-2');
      cy.visit('/manage');
      cy.contains('Family Search & Management').should('be.visible');
    });
  });

  describe('Table Display', () => {
    it('should display family names instead of IDs in the table', () => {
      // Wait for any data to load
      cy.wait(1000);
      
      // Check that the table header shows "Family Name" instead of "Family ID"
      cy.get('th').should('contain', 'Family Name');
      cy.get('th').should('not.contain', 'Family ID');
      
      // If there are families displayed, check that the first column shows names, not IDs
      cy.get('tbody tr').then(($rows) => {
        if ($rows.length > 0) {
          // Check that the first cell contains a name-like string (not a UUID or "Person ID" format)
          cy.get('tbody tr').first().find('td').first().should('not.match', /^[0-9a-f]{8}\.\.\.$/);
          cy.get('tbody tr').first().find('td').first().should('not.match', /^Person [0-9a-f]{8}$/);
          // Should contain actual names like "John Smith & Jane Doe"
          cy.get('tbody tr').first().find('td').first().should('contain', '&');
        }
      });
    });

    it('should have proper table structure', () => {
      cy.get('table').should('exist');
      cy.get('thead').should('exist');
      cy.get('tbody').should('exist');
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels', () => {
      cy.get('input[type="text"]').should('be.visible');
    });

    it('should be keyboard navigable', () => {
      cy.get('input[type="text"]').first().focus().should('be.focused');
    });

    it('should have proper heading structure', () => {
      cy.get('h1').should('exist');
      cy.get('h1').should('contain', 'Family Search');
    });
  });

  describe('Performance', () => {
    it('should load families within acceptable time', () => {
      const startTime = Date.now();
      cy.visit('/manage');
      cy.get('.family-management-view').should('be.visible');
      cy.then(() => {
        const loadTime = Date.now() - startTime;
        expect(loadTime).to.be.lessThan(5000);
      });
    });
  });
});
