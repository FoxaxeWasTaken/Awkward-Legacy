describe('Welcome View - E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('Page Load and Initial State', () => {
    it('should display the main homepage interface', () => {
      // Check header
      cy.contains('h1', '🏛️ Geneweb').should('be.visible');
      cy.contains('Explore family trees and genealogical data').should('be.visible');
      
      // Check action cards
      cy.contains('Upload Family File').should('be.visible');
      cy.contains('Search & Manage Families').should('be.visible');
    });

    it('should display action cards with proper content', () => {
      // Upload Family File card
      cy.contains('Upload Family File').should('be.visible');
      cy.contains('Upload and import your GeneWeb (.gw) files to the database').should('be.visible');
      cy.contains('Upload File').should('be.visible');
      
      // Search & Manage Families card
      cy.contains('Search & Manage Families').should('be.visible');
      cy.contains('Search, explore, and manage all families in the database').should('be.visible');
      cy.contains('Explore Families').should('be.visible');
      
      // Create Family card
      cy.contains('Create a family').should('be.visible');
      cy.contains('Create a new family by adding parents, marriage information and more').should('be.visible');
      cy.contains('Create family').should('be.visible');
    });

    it('should have proper card layout and styling', () => {
      // Check that cards are displayed in a grid
      cy.get('.action-card').should('have.length', 3);
      cy.get('.action-card').each(($card) => {
        cy.wrap($card).should('be.visible');
        cy.wrap($card).should('have.class', 'action-card');
      });
    });
  });

  describe('Navigation from Homepage', () => {
    it('should navigate to upload page when clicking Upload File', () => {
      cy.contains('Upload File').click();
      cy.url().should('include', '/upload');
      cy.contains('Upload Family File').should('be.visible');
    });

    it('should navigate to manage page when clicking Explore Families', () => {
      cy.contains('Explore Families').click();
      cy.url().should('include', '/manage');
      cy.contains('Family Search & Management').should('be.visible');
    });

    it('should navigate to create family page when clicking Create Family', () => {
      cy.contains('Create family').click();
      cy.url().should('include', '/families/create');
      cy.contains('Create a Family').should('be.visible');
      cy.contains('Create a new family by adding parents and marriage information').should('be.visible');
    });

    it('should handle browser back button from upload page', () => {
      // Navigate to upload page
      cy.contains('Upload File').click();
      cy.url().should('include', '/upload');
      
      // Use browser back button
      cy.go('back');
      cy.url().should('eq', Cypress.config().baseUrl + '/');
      cy.contains('🏛️ Geneweb').should('be.visible');
    });

    it('should handle browser forward button', () => {
      // Navigate to upload page
      cy.contains('Upload File').click();
      cy.url().should('include', '/upload');
      
      // Use browser back button
      cy.go('back');
      cy.url().should('eq', Cypress.config().baseUrl + '/');
      
      // Use browser forward button
      cy.go('forward');
      cy.url().should('include', '/upload');
    });

    it('should handle rapid navigation between pages', () => {
      // Rapid navigation test
      cy.contains('Upload File').click();
      cy.url().should('include', '/upload');
      
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
      
      cy.contains('Explore Families').click();
      cy.url().should('include', '/manage');
      
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });
  });

  describe('Responsive Design', () => {
    it('should work on mobile viewport', () => {
      cy.viewport('iphone-x');
      
      cy.contains('🏛️ Geneweb').should('be.visible');
      cy.get('.action-card').should('have.length', 3);
      cy.contains('Upload File').should('be.visible');
      cy.contains('Explore Families').should('be.visible');
      cy.contains('Create a family').should('be.visible');
    });

    it('should work on tablet viewport', () => {
      cy.viewport('ipad-2');
      
      cy.contains('🏛️ Geneweb').should('be.visible');
      cy.get('.action-card').should('have.length', 3);
      cy.contains('Upload File').should('be.visible');
      cy.contains('Explore Families').should('be.visible');
      cy.contains('Create a family').should('be.visible');
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading structure', () => {
      cy.get('h1').should('contain', '🏛️ Geneweb');
    });

    it('should be keyboard navigable', () => {
      // Check that elements can be focused
      cy.contains('Upload File').should('be.visible').focus();
      cy.focused().should('exist');
    });

    it('should have proper button labels', () => {
      cy.contains('Upload File').should('be.visible');
      cy.contains('Explore Families').should('be.visible');
    });
  });
});
