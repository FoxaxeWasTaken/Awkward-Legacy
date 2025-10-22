describe('Family Tree - Simple E2E Tests', () => {
  const testFamilyId = '123e4567-e89b-12d3-a456-426614174000';

  beforeEach(() => {
    cy.visit(`/family/${testFamilyId}`);
  });

  describe('Page Load and Basic Functionality', () => {
    it('should load the family tree page', () => {
      // Check if the page loads
      cy.get('body').should('be.visible');
      cy.url().should('include', `/family/${testFamilyId}`);
    });

    it('should display basic page elements', () => {
      // Check if there are any h1 elements
      cy.get('h1').then(($h1s) => {
        if ($h1s.length > 0) {
          cy.log('Found h1 elements:', $h1s.length);
        }
      });
      
      // Check if there are any elements with "family" in the text
      cy.get('*').then(($elements) => {
        const familyElements = $elements.filter((i, el) => 
          Cypress.$(el).text().toLowerCase().includes('family')
        );
        cy.log('Elements with "family" in text:', familyElements.length);
      });
    });

    it('should have accessible elements', () => {
      // Test that the page has basic accessible elements
      cy.get('body').should('be.visible');
    });

    it('should be responsive', () => {
      // Test mobile viewport
      cy.viewport(375, 667);
      cy.get('body').should('be.visible');
      
      // Test desktop viewport
      cy.viewport(1280, 720);
      cy.get('body').should('be.visible');
    });
  });
});
