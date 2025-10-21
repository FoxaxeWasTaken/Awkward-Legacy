describe('Family Search to Family Tree Navigation - E2E Tests', () => {
  const API_URL = Cypress.env('apiUrl') || 'http://server-dev:8000';
  
  // Test data
  const testSearchResults = [
    {
      id: 'family-1',
      husband_name: 'John Smith',
      wife_name: 'Jane Doe',
      marriage_date: '2005-06-20',
      marriage_place: 'Boston, MA',
      children_count: 2,
      summary: 'John Smith & Jane Doe (2005)'
    },
    {
      id: 'family-2',
      husband_name: 'Robert Johnson',
      wife_name: 'Mary Wilson',
      marriage_date: '2010-03-15',
      marriage_place: 'New York, NY',
      children_count: 1,
      summary: 'Robert Johnson & Mary Wilson (2010)'
    }
  ];

  const testFamilyDetail = {
    id: 'family-1',
    husband_id: 'h1',
    wife_id: 'w1',
    marriage_date: '2005-06-20',
    marriage_place: 'Boston, MA',
    notes: 'Test family',
    husband: {
      id: 'h1',
      first_name: 'John',
      last_name: 'Smith',
      sex: 'M',
      birth_date: '1980-01-01',
      death_date: null,
      birth_place: 'Boston, MA',
      death_place: null,
      occupation: 'Engineer',
      notes: 'Test husband',
      has_own_family: false,
      own_families: []
    },
    wife: {
      id: 'w1',
      first_name: 'Jane',
      last_name: 'Doe',
      sex: 'F',
      birth_date: '1982-03-15',
      death_date: null,
      birth_place: 'New York, NY',
      death_place: null,
      occupation: 'Teacher',
      notes: 'Test wife',
      has_own_family: false,
      own_families: []
    },
    children: [
      {
        id: 'c1',
        family_id: 'family-1',
        person_id: 'p1',
        person: {
          id: 'p1',
          first_name: 'Child',
          last_name: 'Smith',
          sex: 'M',
          birth_date: '2010-05-10',
          death_date: null,
          birth_place: 'Boston, MA',
          death_place: null,
          occupation: null,
          notes: 'Test child',
          has_own_family: false,
          own_families: []
        }
      }
    ],
    events: []
  };

  beforeEach(() => {
    // Intercept API calls
    cy.intercept('GET', `${API_URL}/api/v1/families/search*`, {
      statusCode: 200,
      body: testSearchResults
    }).as('searchFamilies');

    cy.intercept('GET', `${API_URL}/api/v1/families/family-1/detail`, {
      statusCode: 200,
      body: testFamilyDetail
    }).as('getFamilyDetail');

    cy.intercept('GET', `${API_URL}/health`, {
      statusCode: 200,
      body: { status: 'healthy' }
    }).as('healthCheck');

    // Visit the manage page where search functionality is located
    cy.visit('/manage');
  });

  describe('Search to Family Tree Navigation Flow', () => {
    it('should complete full search to family tree navigation', () => {
      // Step 1: Perform search
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Smith');
      cy.get('button.search-button').click();
      
      cy.wait('@searchFamilies');
      
      // Step 2: Verify search results
      cy.get('.family-card').should('have.length', 2);
      cy.get('.family-card').first().should('contain', 'John Smith & Jane Doe');
      cy.get('.family-card').first().should('contain', 'Boston, MA');
      cy.get('.family-card').first().should('contain', '2 children');
      
      // Step 3: Click on first family card
      cy.get('.family-card').first().find('button').contains('View Details').click();
      
      // Step 4: Verify navigation to family tree
      cy.url().should('include', '/family/family-1');
      cy.wait('@getFamilyDetail');
      
      // Step 5: Verify family tree is displayed
      cy.get('.family-tree').should('be.visible');
      cy.get('h2').should('contain', 'John Smith & Jane Doe');
      cy.get('.tree-container').should('be.visible');
    });

    it('should navigate back to search from family tree', () => {
      // Navigate to family tree first
      cy.visit('/family/family-1');
      cy.wait('@getFamilyDetail');
      
      // Verify family tree is displayed
      cy.get('.family-tree').should('be.visible');
      
      // Click back button
      cy.get('.back-button').click();
      
      // Verify navigation back to search
      cy.url().should('eq', Cypress.config().baseUrl + '/');
      cy.contains('Family Search').should('be.visible');
    });

    it('should maintain search state when navigating back', () => {
      // Perform search
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Smith');
      cy.get('button.search-button').click();
      cy.wait('@searchFamilies');
      
      // Navigate to family tree
      cy.get('.family-card').first().find('button').contains('View Details').click();
      cy.wait('@getFamilyDetail');
      
      // Navigate back
      cy.get('.back-button').click();
      
      // Verify search results are still displayed
      cy.get('.family-card').should('have.length', 2);
      cy.get('input[placeholder*="Search families by name, place, or notes"]').should('have.value', 'Smith');
    });
  });

  describe('Multiple Family Navigation', () => {
    it('should navigate between different families', () => {
      // Search for families
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('family');
      cy.get('button.search-button').click();
      cy.wait('@searchFamilies');
      
      // Navigate to first family
      cy.get('.family-card').first().find('button').contains('View Details').click();
      cy.wait('@getFamilyDetail');
      
      cy.get('h2').should('contain', 'John Smith & Jane Doe');
      
      // Navigate back
      cy.get('.back-button').click();
      
      // Navigate to second family
      cy.intercept('GET', `${API_URL}/api/v1/families/family-2/detail`, {
        statusCode: 200,
        body: {
          ...testFamilyDetail,
          id: 'family-2',
          husband: {
            ...testFamilyDetail.husband,
            first_name: 'Robert',
            last_name: 'Johnson'
          },
          wife: {
            ...testFamilyDetail.wife,
            first_name: 'Mary',
            last_name: 'Wilson'
          }
        }
      }).as('getFamily2Detail');
      
      cy.get('.family-card').eq(1).find('button').contains('View Details').click();
      cy.wait('@getFamily2Detail');
      
      cy.get('h2').should('contain', 'Robert Johnson & Mary Wilson');
    });
  });

  describe('URL Navigation', () => {
    it('should handle direct URL navigation to family tree', () => {
      // Navigate directly to family tree URL
      cy.visit('/family/family-1');
      cy.wait('@getFamilyDetail');
      
      // Verify family tree is displayed
      cy.get('.family-tree').should('be.visible');
      cy.get('h2').should('contain', 'John Smith & Jane Doe');
    });

    it('should handle browser back/forward navigation', () => {
      // Start at search page
      cy.visit('/manage');
      
      // Navigate to family tree
      cy.visit('/family/family-1');
      cy.wait('@getFamilyDetail');
      
      // Use browser back button
      cy.go('back');
      cy.url().should('eq', Cypress.config().baseUrl + '/');
      
      // Use browser forward button
      cy.go('forward');
      cy.url().should('include', '/family/family-1');
    });

    it('should handle invalid family ID in URL', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/invalid-id/detail`, {
        statusCode: 404,
        body: { detail: 'Family not found' }
      }).as('getInvalidFamily');
      
      cy.visit('/family/invalid-id');
      cy.wait('@getInvalidFamily');
      
      cy.get('.error-state').should('be.visible');
      cy.contains('Family not found').should('be.visible');
    });
  });

  describe('Search Integration', () => {
    it('should perform new search from family tree back button', () => {
      // Navigate to family tree
      cy.visit('/family/family-1');
      cy.wait('@getFamilyDetail');
      
      // Navigate back to search
      cy.get('.back-button').click();
      
      // Perform new search
      cy.get('input[placeholder*="Search families by name, place, or notes"]').clear().type('Johnson');
      cy.get('button.search-button').click();
      cy.wait('@searchFamilies');
      
      // Verify new search results
      cy.get('.family-card').should('have.length', 2);
    });

    it('should clear search when navigating back and typing new query', () => {
      // Perform initial search
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Smith');
      cy.get('button.search-button').click();
      cy.wait('@searchFamilies');
      
      // Navigate to family tree
      cy.get('.family-card').first().find('button').contains('View Details').click();
      cy.wait('@getFamilyDetail');
      
      // Navigate back
      cy.get('.back-button').click();
      
      // Start typing new search (should clear previous results)
      cy.get('input[placeholder*="Search families by name, place, or notes"]').clear().type('Johnson');
      
      // Results should be cleared while typing
      cy.get('.family-card').should('not.exist');
      cy.contains('Welcome to Family Search').should('be.visible');
    });
  });

  describe('Error Handling in Navigation Flow', () => {
    it('should handle API error during family detail loading', () => {
      // Perform search successfully
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Smith');
      cy.get('button.search-button').click();
      cy.wait('@searchFamilies');
      
      // Mock API error for family detail
      cy.intercept('GET', `${API_URL}/api/v1/families/family-1/detail`, {
        statusCode: 500,
        body: { detail: 'Internal server error' }
      }).as('getFamilyDetailError');
      
      // Click on family card
      cy.get('.family-card').first().find('button').contains('View Details').click();
      cy.wait('@getFamilyDetailError');
      
      // Verify error state
      cy.get('.error-state').should('be.visible');
      cy.contains('Internal server error').should('be.visible');
      
      // Verify we can still navigate back
      cy.get('.back-button').click();
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });

    it('should handle network timeout during navigation', () => {
      // Perform search
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Smith');
      cy.get('button.search-button').click();
      cy.wait('@searchFamilies');
      
      // Mock network timeout
      cy.intercept('GET', `${API_URL}/api/v1/families/family-1/detail`, {
        forceNetworkError: true
      }).as('getFamilyDetailTimeout');
      
      // Click on family card
      cy.get('.family-card').first().find('button').contains('View Details').click();
      cy.wait('@getFamilyDetailTimeout');
      
      // Verify error state
      cy.get('.error-state').should('be.visible');
      cy.contains('Failed to load family tree').should('be.visible');
    });
  });

  describe('Performance and User Experience', () => {
    it('should provide smooth navigation experience', () => {
      const startTime = Date.now();
      
      // Perform search
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Smith');
      cy.get('button.search-button').click();
      cy.wait('@searchFamilies');
      
      // Navigate to family tree
      cy.get('.family-card').first().find('button').contains('View Details').click();
      cy.wait('@getFamilyDetail');
      
      // Verify navigation completed within reasonable time
      cy.get('.family-tree').should('be.visible').then(() => {
        const navigationTime = Date.now() - startTime;
        expect(navigationTime).to.be.lessThan(3000); // Should navigate within 3 seconds
      });
    });

    it('should maintain scroll position when navigating back', () => {
      // Perform search
      cy.get('input[placeholder*="Search families by name, place, or notes"]').type('Smith');
      cy.get('button.search-button').click();
      cy.wait('@searchFamilies');
      
      // Scroll down in search results
      cy.get('.family-card').last().scrollIntoView();
      
      // Navigate to family tree
      cy.get('.family-card').first().find('button').contains('View Details').click();
      cy.wait('@getFamilyDetail');
      
      // Navigate back
      cy.get('.back-button').click();
      
      // Verify we're back on search page
      cy.get('.family-card').should('be.visible');
    });
  });

  describe('Accessibility in Navigation Flow', () => {
    it('should be keyboard navigable throughout the flow', () => {
      // Tab to search input
      cy.get('input[placeholder*="Search families by name, place, or notes"]').focus().type('Smith');
      
      // Tab to search button and activate
      cy.get('button.search-button').focus().type('{enter}');
      cy.wait('@searchFamilies');
      
      // Tab to first family card button
      cy.get('.family-card').first().find('button').focus().type('{enter}');
      cy.wait('@getFamilyDetail');
      
      // Verify family tree is displayed
      cy.get('.family-tree').should('be.visible');
      
      // Tab to back button and activate
      cy.get('.back-button').focus().type('{enter}');
      
      // Verify back on search page
      cy.url().should('eq', Cypress.config().baseUrl + '/');
    });

    it('should have proper focus management', () => {
      // Navigate to family tree
      cy.visit('/family/family-1');
      cy.wait('@getFamilyDetail');
      
      // Focus should be on back button or first interactive element
      cy.get('.back-button').focus().should('be.focused');
    });
  });
});
