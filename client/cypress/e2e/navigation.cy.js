describe('Navigation - E2E Tests', () => {
  const API_URL = Cypress.env('apiUrl') || 'http://server-dev:8000';
  
  beforeEach(() => {
    // Mock API calls
    cy.intercept('GET', `${API_URL}/api/v1/families`, {
      statusCode: 200,
      body: [
        {
          id: '123e4567-e89b-12d3-a456-426614174000',
          husband_id: 'h1',
          wife_id: 'w1',
          marriage_date: '2005-06-20',
          marriage_place: 'Boston, MA'
        }
      ]
    }).as('getFamilies');

    cy.intercept('GET', `${API_URL}/health`, {
      statusCode: 200,
      body: { status: 'healthy' }
    }).as('healthCheck');
  });

  describe('Homepage Navigation', () => {
    it('should navigate from homepage to upload page', () => {
      cy.visit('/');
      
      cy.contains('Upload File').click();
      cy.url().should('include', '/upload');
      cy.contains('Upload Family File').should('be.visible');
    });

    it('should navigate from homepage to manage page', () => {
      cy.visit('/');
      
      cy.contains('Explore Families').click();
      cy.url().should('include', '/manage');
      cy.contains('Family Search & Management').should('be.visible');
    });
  });

  describe('Upload Page Navigation', () => {
    it('should navigate back to homepage from upload page', () => {
      cy.visit('/upload');
      
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
      cy.contains('🏛️ Geneweb').should('be.visible');
    });

    it('should navigate to manage page after successful upload', () => {
      // Mock successful upload
      cy.intercept('POST', `${API_URL}/api/v1/files/import`, {
        statusCode: 200,
        body: {
          persons_created: 5,
          families_created: 2,
          events_created: 3,
          children_created: 4
        }
      }).as('uploadFile');

      cy.visit('/upload');
      
      // Upload a file
      const testFile = new File(['test content'], 'test.gw', { type: 'text/plain' });
      cy.get('input[type="file"]').selectFile({
        contents: testFile,
        fileName: 'test.gw',
        mimeType: 'text/plain'
      });
      
      cy.contains('Upload File').click();
      cy.wait('@uploadFile');
      
      // Should auto-navigate to manage page
      cy.url({ timeout: 5000 }).should('include', '/manage');
      cy.contains('Family Search & Management').should('be.visible');
    });
  });

  describe('Manage Page Navigation', () => {
    it('should navigate back to homepage from manage page', () => {
      cy.visit('/manage');
      cy.wait('@getFamilies');
      
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
      cy.contains('🏛️ Geneweb').should('be.visible');
    });

    it('should refresh data when refresh button is clicked', () => {
      cy.visit('/manage');
      cy.wait('@getFamilies');
      
      cy.contains('Refresh').click();
      cy.wait('@getFamilies');
      
      // Should still be on manage page
      cy.url().should('include', '/manage');
      cy.contains('Family Search & Management').should('be.visible');
    });
  });

  describe('Direct URL Navigation', () => {
    it('should handle direct navigation to upload page', () => {
      cy.visit('/upload');
      cy.contains('Upload Family File').should('be.visible');
    });

    it('should handle direct navigation to manage page', () => {
      cy.visit('/manage');
      cy.wait('@getFamilies');
      cy.contains('Family Search & Management').should('be.visible');
    });

    it('should handle invalid routes', () => {
      cy.visit('/invalid-route');
      // Should redirect to homepage or show 404
      cy.url().should('not.include', '/invalid-route');
    });
  });

  describe('Browser Navigation', () => {
    it('should handle browser back button', () => {
      // Start at homepage
      cy.visit('/');
      
      // Navigate to upload page
      cy.contains('Upload File').click();
      cy.url().should('include', '/upload');
      
      // Use browser back button
      cy.go('back');
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });

    it('should handle browser forward button', () => {
      // Start at homepage
      cy.visit('/');
      
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

    it('should maintain state during navigation', () => {
      // Start at homepage
      cy.visit('/');
      
      // Navigate to manage page
      cy.contains('Explore Families').click();
      cy.wait('@getFamilies');
      
      // Perform a search
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Boston');
      cy.contains('Search').click();
      
      // Navigate back to homepage
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
      
      // Navigate back to manage page
      cy.contains('Explore Families').click();
      cy.wait('@getFamilies');
      
      // Search should be cleared (new page load)
      cy.get('input[placeholder*="Search families by name, place, or notes"]').should('have.value', '');
    });
  });

  describe('Navigation Flow', () => {
    it('should complete full workflow: homepage -> upload -> manage', () => {
      // Start at homepage
      cy.visit('/');
      cy.contains('🏛️ Geneweb').should('be.visible');
      
      // Navigate to upload
      cy.contains('Upload File').click();
      cy.url().should('include', '/upload');
      cy.contains('Upload Family File').should('be.visible');
      
      // Navigate back to homepage
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
      
      // Navigate to manage
      cy.contains('Explore Families').click();
      cy.url().should('include', '/manage');
      cy.wait('@getFamilies');
      cy.contains('Family Search & Management').should('be.visible');
    });

    it('should handle rapid navigation between pages', () => {
      // Rapid navigation test
      cy.visit('/');
      cy.contains('Upload File').click();
      cy.url().should('include', '/upload');
      
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
      
      cy.contains('Explore Families').click();
      cy.url().should('include', '/manage');
      cy.wait('@getFamilies');
      
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });
  });

  describe('URL State Management', () => {
    it('should maintain URL state during page refreshes', () => {
      cy.visit('/upload');
      cy.url().should('include', '/upload');
      
      // Refresh page
      cy.reload();
      cy.url().should('include', '/upload');
      cy.contains('Upload Family File').should('be.visible');
    });

    it('should handle deep linking to manage page', () => {
      cy.visit('/manage');
      cy.wait('@getFamilies');
      cy.contains('Family Search & Management').should('be.visible');
      
      // Refresh page
      cy.reload();
      cy.wait('@getFamilies');
      cy.url().should('include', '/manage');
      cy.contains('Family Search & Management').should('be.visible');
    });
  });

  describe('Navigation Accessibility', () => {
    it('should be keyboard navigable', () => {
      cy.visit('/');
      
      // Tab through navigation elements
      cy.get('body').tab();
      cy.focused().should('be.visible');
      
      // Navigate to upload page
      cy.contains('Upload File').focus().type('{enter}');
      cy.url().should('include', '/upload');
    });

    it('should have proper focus management', () => {
      cy.visit('/upload');
      
      // Focus should be on first interactive element
      cy.get('input[type="file"]').focus().should('be.focused');
    });
  });

  describe('Error Handling in Navigation', () => {
    it('should handle API errors during navigation', () => {
      // Mock API error
      cy.intercept('GET', `${API_URL}/api/v1/families`, {
        statusCode: 500,
        body: { detail: 'Internal server error' }
      }).as('getFamiliesError');

      cy.visit('/manage');
      cy.wait('@getFamiliesError');
      
      // Should still be on manage page but show error
      cy.url().should('include', '/manage');
      cy.contains('Error Loading Families').should('be.visible');
      
      // Should still be able to navigate back
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });

    it('should handle network errors during navigation', () => {
      // Mock network error
      cy.intercept('GET', `${API_URL}/api/v1/families`, {
        forceNetworkError: true
      }).as('getFamiliesNetworkError');

      cy.visit('/manage');
      cy.wait('@getFamiliesNetworkError');
      
      // Should still be on manage page but show error
      cy.url().should('include', '/manage');
      cy.contains('Error Loading Families').should('be.visible');
    });
  });
});
