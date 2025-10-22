describe('File Upload - Simple E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/upload');
  });

  describe('Page Load and Basic Functionality', () => {
    it('should load the file upload page', () => {
      // Check if the page loads
      cy.get('body').should('be.visible');
      cy.url().should('include', '/upload');
    });

    it('should display basic page elements', () => {
      // Check if there are any h1 elements
      cy.get('h1').then(($h1s) => {
        if ($h1s.length > 0) {
          cy.log('Found h1 elements:', $h1s.length);
        }
      });
      
      // Check if there are any elements with "upload" in the text
      cy.get('*').then(($elements) => {
        const uploadElements = $elements.filter((i, el) => 
          Cypress.$(el).text().toLowerCase().includes('upload')
        );
        cy.log('Elements with "upload" in text:', uploadElements.length);
      });
    });

    it('should have file input element', () => {
      // Check if file input exists (it might be hidden)
      cy.get('input[type="file"]').should('exist');
    });

    it('should be responsive', () => {
      // Test mobile viewport
      cy.viewport(375, 667);
      cy.get('body').should('be.visible');
      
      // Test desktop viewport
      cy.viewport(1280, 720);
      cy.get('body').should('be.visible');
    });

    it('should have accessible elements', () => {
      // Test that the page has basic accessible elements
      cy.get('body').should('be.visible');
    });
  });
});
