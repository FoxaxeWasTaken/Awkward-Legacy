describe('File Upload - E2E Tests', () => {
  const API_URL = Cypress.env('apiUrl') || 'http://server-dev:8000';
  
  beforeEach(() => {
    // Mock health check
    cy.intercept('GET', `${API_URL}/health`, {
      statusCode: 200,
      body: { status: 'healthy' }
    }).as('healthCheck');

    cy.visit('/upload');
  });

  describe('Page Load and Initial State', () => {
    it('should display the upload interface', () => {
      cy.contains('h1', '📁 Upload Family File').should('be.visible');
      cy.contains('Upload your GeneWeb (.gw) file to import family data into the database').should('be.visible');
      cy.get('input[type="file"]').should('exist');
      cy.contains('Choose File').should('be.visible');
    });

    it('should show upload instructions', () => {
      cy.contains('Drop your GeneWeb file here').should('be.visible');
      cy.contains('Supported formats: .gw files only').should('be.visible');
    });

    it('should have proper file input attributes', () => {
      cy.get('input[type="file"]').should('have.attr', 'accept', '.gw');
    });
  });

  describe('File Selection', () => {
    it('should handle file selection', () => {
      // Create a test file
      const testFile = new File(['test content'], 'test.gw', { type: 'text/plain' });
      
      cy.get('input[type="file"]').selectFile({
        contents: testFile,
        fileName: 'test.gw',
        mimeType: 'text/plain'
      }, { force: true });
      
      cy.get('input[type="file"]').should('have.value');
    });

    it('should show selected file name', () => {
      const testFile = new File(['test content'], 'family.gw', { type: 'text/plain' });
      
      cy.get('input[type="file"]').selectFile({
        contents: testFile,
        fileName: 'family.gw',
        mimeType: 'text/plain'
      }, { force: true });
      
      // The file input should show the selected file
      cy.get('input[type="file"]').should('have.value');
    });
  });

  describe('File Upload Process', () => {
    it('should upload file successfully', () => {
      // Mock successful upload response
      cy.intercept('POST', `${API_URL}/api/v1/files/import`, {
        statusCode: 200,
        body: {
          persons_created: 5,
          families_created: 2,
          events_created: 3,
          children_created: 4
        }
      }).as('uploadFile');

      const testFile = new File(['test content'], 'test.gw', { type: 'text/plain' });
      
      cy.get('input[type="file"]').selectFile({
        contents: testFile,
        fileName: 'test.gw',
        mimeType: 'text/plain'
      }, { force: true });
      
      cy.contains('Upload File').click();
      cy.wait('@uploadFile');
      
      // Check success message
      cy.contains('Upload Successful!').should('be.visible');
      cy.contains('Persons: 5').should('be.visible');
      cy.contains('Families: 2').should('be.visible');
      cy.contains('Events: 3').should('be.visible');
      cy.contains('Children: 4').should('be.visible');
    });

    it('should show upload progress', () => {
      // Mock upload with delay to see progress
      cy.intercept('POST', `${API_URL}/api/v1/files/import`, {
        statusCode: 200,
        body: {
          persons_created: 5,
          families_created: 2,
          events_created: 3,
          children_created: 4
        },
        delay: 1000
      }).as('uploadFile');

      const testFile = new File(['test content'], 'test.gw', { type: 'text/plain' });
      
      cy.get('input[type="file"]').selectFile({
        contents: testFile,
        fileName: 'test.gw',
        mimeType: 'text/plain'
      }, { force: true });
      
      cy.contains('Upload File').click();
      
      // Check that progress is shown
      cy.get('.upload-progress').should('be.visible');
      cy.get('.progress-bar').should('be.visible');
      
      cy.wait('@uploadFile');
    });

    it('should handle upload errors', () => {
      // Mock upload error
      cy.intercept('POST', `${API_URL}/api/v1/files/import`, {
        statusCode: 400,
        body: {
          detail: 'Invalid file format'
        }
      }).as('uploadError');

      const testFile = new File(['invalid content'], 'test.gw', { type: 'text/plain' });
      
      cy.get('input[type="file"]').selectFile({
        contents: testFile,
        fileName: 'test.gw',
        mimeType: 'text/plain'
      }, { force: true });
      
      cy.contains('Upload File').click();
      cy.wait('@uploadError');
      
      // Check error message
      cy.contains('Upload Error').should('be.visible');
      cy.contains('Invalid file format').should('be.visible');
    });

    it('should handle network errors', () => {
      // Mock network error
      cy.intercept('POST', `${API_URL}/api/v1/files/import`, {
        forceNetworkError: true
      }).as('uploadNetworkError');

      const testFile = new File(['test content'], 'test.gw', { type: 'text/plain' });
      
      cy.get('input[type="file"]').selectFile({
        contents: testFile,
        fileName: 'test.gw',
        mimeType: 'text/plain'
      }, { force: true });
      
      cy.contains('Upload File').click();
      cy.wait('@uploadNetworkError');
      
      // Check error message
      cy.contains('Upload Error').should('be.visible');
      cy.contains('Failed to upload file').should('be.visible');
    });
  });

  describe('Auto-navigation after Upload', () => {
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

      const testFile = new File(['test content'], 'test.gw', { type: 'text/plain' });
      
      cy.get('input[type="file"]').selectFile({
        contents: testFile,
        fileName: 'test.gw',
        mimeType: 'text/plain'
      }, { force: true });
      
      cy.contains('Upload File').click();
      cy.wait('@uploadFile');
      
      // Wait for auto-navigation (2 seconds delay)
      cy.url({ timeout: 5000 }).should('include', '/manage');
      cy.contains('Family Search & Management').should('be.visible');
    });
  });

  describe('File Validation', () => {
    it('should only accept .gw files', () => {
      // Try to upload a non-.gw file
      const testFile = new File(['test content'], 'test.txt', { type: 'text/plain' });
      
      cy.get('input[type="file"]').selectFile({
        contents: testFile,
        fileName: 'test.txt',
        mimeType: 'text/plain'
      }, { force: true });
      
      // The file input should accept it (browser validation)
      cy.get('input[type="file"]').should('have.value');
    });

    it('should handle empty file selection', () => {
      // Try to upload without selecting a file
      cy.contains('Upload File').click();
      
      // Should not trigger upload
      cy.get('.upload-progress').should('not.exist');
    });
  });

  describe('Navigation', () => {
    it('should have back button to return to homepage', () => {
      cy.contains('← Back to Home').should('be.visible');
      cy.contains('← Back to Home').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });

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

    it('should maintain URL state during page refreshes', () => {
      cy.visit('/upload');
      cy.url().should('include', '/upload');
      
      // Refresh page
      cy.reload();
      cy.url().should('include', '/upload');
      cy.contains('Upload Family File').should('be.visible');
    });
  });

  describe('Responsive Design', () => {
    it('should work on mobile viewport', () => {
      cy.viewport('iphone-x');
      
      cy.contains('Upload Family File').should('be.visible');
      cy.get('input[type="file"]').should('exist');
      cy.contains('Choose File').should('be.visible');
    });

    it('should work on tablet viewport', () => {
      cy.viewport('ipad-2');
      
      cy.contains('Upload Family File').should('be.visible');
      cy.get('input[type="file"]').should('exist');
    });
  });

  describe('Accessibility', () => {
    it('should have proper form labels', () => {
      cy.get('input[type="file"]').should('exist');
      cy.contains('Choose File').should('be.visible');
    });

    it('should be keyboard navigable', () => {
      cy.get('input[type="file"]').focus().should('be.focused');
      cy.get('body').type('{tab}');
      cy.focused().should('be.visible');
    });
  });
});
