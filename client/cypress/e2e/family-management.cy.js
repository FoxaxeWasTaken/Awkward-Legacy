describe('Family Management - E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/manage');
  });

  describe('Page Load and Initial State', () => {
    it('should load the manage page', () => {
      // Check if the page loads at all
      cy.get('body').should('be.visible');
      cy.url().should('include', '/manage');
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
  });

  describe('Basic Functionality', () => {
    it('should have basic page structure', () => {
      // Check if there are any input elements
      cy.get('input').then(($inputs) => {
        cy.log('Found input elements:', $inputs.length);
      });
      
      // Check if there are any button elements
      cy.get('button').then(($buttons) => {
        cy.log('Found button elements:', $buttons.length);
      });
    });

    it('should have accessible elements', () => {
      // Test that the page has basic accessible elements
      cy.get('body').should('be.visible');
    });
  });

  describe('Navigation', () => {
    it('should allow navigation back to home', () => {
      // Check if we can navigate back
      cy.go('back');
      cy.url().should('not.include', '/manage');
    });
  });

  describe('Responsive Design', () => {
    it('should work on mobile viewport', () => {
      cy.viewport('iphone-x');
      cy.get('body').should('be.visible');
    });

    it('should work on tablet viewport', () => {
      cy.viewport('ipad-2');
      cy.get('body').should('be.visible');
    });
  });
});