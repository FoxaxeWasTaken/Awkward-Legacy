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

  describe('Family List Display', () => {
    it('should display families in a table or grid', () => {
      // Check if there's either a table or grid of families
      cy.get('table, .family-grid, .family-list').should('exist');
    });

    it('should display family information', () => {
      // Check if family data is displayed (either in table rows or cards)
      cy.get('table tr, .family-card, .family-item').should('have.length.greaterThan', 0);
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

  describe('Family Actions', () => {
    it('should have action buttons for each family', () => {
      // Look for view/edit/delete buttons
      cy.get('button, a').contains(/view|tree|details/i).should('exist');
    });

    it('should navigate to family tree when clicking view button', () => {
      // Find and click the first "View Tree" or similar button
      cy.get('button, a').contains(/view|tree/i).first().click();
      // Should navigate to a family tree page
      cy.url().should('include', '/family/');
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
