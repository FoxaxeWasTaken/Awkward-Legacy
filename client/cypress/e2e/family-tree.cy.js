describe('Family Tree - E2E Tests', () => {
  const API_URL = Cypress.env('apiUrl') || 'http://server-dev:8000';
  
  // Test data
  const testFamilyId = 'test-family-123';
  const testFamilyData = {
    id: testFamilyId,
    husband_id: 'h123',
    wife_id: 'w123',
    marriage_date: '2005-06-20',
    marriage_place: 'Boston, MA',
    notes: 'Test family notes',
    husband: {
      id: 'h123',
      first_name: 'John',
      last_name: 'Smith',
      sex: 'M',
      birth_date: '1980-01-01',
      death_date: '2020-01-01',
      birth_place: 'Boston, MA',
      death_place: 'Boston, MA',
      occupation: 'Engineer',
      notes: 'Test husband notes',
      has_own_family: false,
      own_families: []
    },
    wife: {
      id: 'w123',
      first_name: 'Jane',
      last_name: 'Doe',
      sex: 'F',
      birth_date: '1982-03-15',
      death_date: null,
      birth_place: 'New York, NY',
      death_place: null,
      occupation: 'Teacher',
      notes: 'Test wife notes',
      has_own_family: false,
      own_families: []
    },
    children: [
      {
        id: 'c1',
        family_id: testFamilyId,
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
          notes: 'Test child notes',
          has_own_family: false,
          own_families: []
        }
      }
    ],
    events: [
      {
        id: 'e1',
        family_id: testFamilyId,
        type: 'marriage',
        date: '2005-06-20',
        place: 'Boston, MA',
        notes: 'Wedding ceremony'
      }
    ]
  };

  beforeEach(() => {
    // Intercept API calls
    cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
      statusCode: 200,
      body: testFamilyData
    }).as('getFamilyDetail');

    cy.intercept('GET', `${API_URL}/health`, {
      statusCode: 200,
      body: { status: 'healthy' }
    }).as('healthCheck');

    // Visit the family tree page directly
    cy.visit(`/family/${testFamilyId}`);
  });

  describe('Page Load and Initial State', () => {
    it('should display loading state initially', () => {
      // Add delay to API call to ensure loading state is visible
      cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
        statusCode: 200,
        body: testFamilyData,
        delay: 1000
      }).as('getFamilyDetailDelayed');
      
      cy.visit(`/family/${testFamilyId}`);
      cy.get('.loading-state').should('be.visible');
      cy.get('.spinner').should('be.visible');
      cy.contains('Loading family tree...').should('be.visible');
    });

    it('should load family data and display tree', () => {
      cy.wait('@getFamilyDetail');
      
      // Wait for loading to complete
      cy.get('.loading-state').should('not.exist');
      cy.get('.tree-container').should('be.visible');
    });

    it('should display family title correctly', () => {
      cy.wait('@getFamilyDetail');
      
      cy.get('h2').should('contain', 'John Smith & Jane Doe');
    });

    it('should display tree controls', () => {
      cy.wait('@getFamilyDetail');
      
      cy.get('.tree-controls').should('be.visible');
      cy.get('button[title="Zoom Out"]').should('be.visible');
      cy.get('button[title="Zoom In"]').should('be.visible');
      cy.get('button[title="Reset View"]').should('be.visible');
      cy.get('.zoom-label').should('contain', '100%');
    });
  });

  describe('Family Tree Display', () => {
    beforeEach(() => {
      cy.wait('@getFamilyDetail');
    });

    it('should display family generations', () => {
      cy.get('.family-generation').should('be.visible');
      cy.get('.couples-row').should('be.visible');
    });

    it('should display husband and wife information', () => {
      cy.get('.person-node.husband').should('be.visible');
      cy.get('.person-node.wife').should('be.visible');
      
      // Check husband details
      cy.get('.person-node.husband').within(() => {
        cy.contains('John Smith').should('be.visible');
        cy.contains('1980').should('be.visible');
        cy.contains('2020').should('be.visible');
        cy.get('.gender-icon').should('contain', '👨');
      });

      // Check wife details
      cy.get('.person-node.wife').within(() => {
        cy.contains('Jane Doe').should('be.visible');
        cy.contains('1982').should('be.visible');
        cy.contains('Present').should('be.visible');
        cy.get('.gender-icon').should('contain', '👩');
      });
    });

    it('should display children information', () => {
      cy.get('.children-row').should('be.visible');
      cy.get('.person-node.child').should('be.visible');
      
      cy.get('.person-node.child').within(() => {
        cy.contains('Child Smith').should('be.visible');
        cy.contains('2010').should('be.visible');
        cy.get('.gender-icon').should('contain', '👦');
      });
    });

    it('should display marriage information', () => {
      cy.get('.marriage-info').should('be.visible');
      cy.contains('Jun 20, 2005').should('be.visible');
      cy.contains('Boston, MA').should('be.visible');
    });
  });

  describe('Tree Controls', () => {
    beforeEach(() => {
      cy.wait('@getFamilyDetail');
      // Wait for the tree to be fully loaded and fitted to view
      cy.get('.tree-content').should('be.visible');
      cy.wait(200); // Wait for fitTreeToView to complete
    });

    it('should zoom in when zoom in button is clicked', () => {
      // Get the initial zoom percentage
      cy.get('.zoom-label').then(($label) => {
        const initialZoom = parseInt($label.text().replace('%', ''));
        
        cy.get('button[title="Zoom In"]').click();
        
        // Check that zoom increased
        cy.get('.zoom-label').should(($newLabel) => {
          const newZoom = parseInt($newLabel.text().replace('%', ''));
          expect(newZoom).to.be.greaterThan(initialZoom);
        });
      });
    });

    it('should zoom out when zoom out button is clicked', () => {
      // Get initial zoom
      cy.get('.zoom-label').then(($label) => {
        const initialZoom = parseInt($label.text().replace('%', ''));
        
        // First zoom in
        cy.get('button[title="Zoom In"]').click();
        
        // Then zoom out
        cy.get('button[title="Zoom Out"]').click();
        
        // Should be back to approximately initial zoom (within 5% tolerance)
        cy.get('.zoom-label').should(($newLabel) => {
          const newZoom = parseInt($newLabel.text().replace('%', ''));
          expect(newZoom).to.be.closeTo(initialZoom, 5);
        });
      });
    });

    it('should reset zoom when reset button is clicked', () => {
      // Zoom in multiple times
      cy.get('button[title="Zoom In"]').click();
      cy.get('button[title="Zoom In"]').click();
      cy.get('.zoom-label').should('not.contain', '100%');
      
      // Reset zoom
      cy.get('button[title="Reset View"]').click();
      cy.get('.zoom-label').should('contain', '100%');
    });

    it('should update zoom percentage display correctly', () => {
      // Get initial zoom
      cy.get('.zoom-label').then(($label) => {
        const initialZoom = parseInt($label.text().replace('%', ''));
        
        // First zoom in
        cy.get('button[title="Zoom In"]').click();
        cy.get('.zoom-label').should(($newLabel) => {
          const newZoom = parseInt($newLabel.text().replace('%', ''));
          expect(newZoom).to.be.greaterThan(initialZoom);
        });
        
        // Second zoom in
        cy.get('button[title="Zoom In"]').click();
        cy.get('.zoom-label').should(($newLabel) => {
          const newZoom = parseInt($newLabel.text().replace('%', ''));
          expect(newZoom).to.be.greaterThan(initialZoom);
        });
      });
    });
  });

  describe('Navigation', () => {
    beforeEach(() => {
      cy.wait('@getFamilyDetail');
    });

    it('should navigate back to family management when back button is clicked', () => {
      cy.get('.back-button').click();
      
      cy.url().should('eq', Cypress.config().baseUrl + '/manage');
      cy.contains('Family Search & Management').should('be.visible');
    });

    it('should display back button with correct text and icon', () => {
      cy.get('.back-button').should('be.visible');
      cy.get('.back-button').should('contain', 'Back to Family Management');
      cy.get('.back-icon').should('contain', '←');
    });
  });

  describe('Error Handling', () => {
    it('should display error state when family not found', () => {
      const nonExistentFamilyId = 'non-existent-family';
      
      cy.intercept('GET', `${API_URL}/api/v1/families/${nonExistentFamilyId}/detail`, {
        statusCode: 404,
        body: { detail: 'Family not found' }
      }).as('getFamilyDetailError');

      cy.visit(`/family/${nonExistentFamilyId}`);
      cy.wait('@getFamilyDetailError');
      
      cy.get('.error-state').should('be.visible');
      cy.get('.error-icon').should('be.visible');
      cy.contains('Error Loading Family Tree').should('be.visible');
      cy.contains('Family not found').should('be.visible');
      cy.get('.retry-button').should('be.visible');
    });

    it('should display error state when server error occurs', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
        statusCode: 500,
        body: { detail: 'Internal server error' }
      }).as('getFamilyDetailServerError');

      cy.visit(`/family/${testFamilyId}`);
      cy.wait('@getFamilyDetailServerError');
      
      cy.get('.error-state').should('be.visible');
      cy.contains('Internal server error').should('be.visible');
    });

    it('should retry loading when retry button is clicked', () => {
      // First request fails
      cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
        statusCode: 500,
        body: { detail: 'Server error' }
      }).as('getFamilyDetailError');

      cy.visit(`/family/${testFamilyId}`);
      cy.wait('@getFamilyDetailError');
      
      cy.get('.error-state').should('be.visible');
      
      // Second request succeeds
      cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
        statusCode: 200,
        body: testFamilyData
      }).as('getFamilyDetailSuccess');

      cy.get('.retry-button').click();
      cy.wait('@getFamilyDetailSuccess');
      
      cy.get('.error-state').should('not.exist');
      cy.get('.tree-container').should('be.visible');
    });

    it('should handle network timeout gracefully', () => {
      cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
        forceNetworkError: true
      }).as('getFamilyDetailTimeout');

      cy.visit(`/family/${testFamilyId}`);
      cy.wait('@getFamilyDetailTimeout');
      
      cy.get('.error-state').should('be.visible');
      cy.contains('Failed to load family tree').should('be.visible');
    });
  });

  describe('Responsive Design', () => {
    beforeEach(() => {
      cy.wait('@getFamilyDetail');
    });

    it('should display correctly on mobile viewport', () => {
      cy.viewport(375, 667); // iPhone SE
      
      cy.get('.family-tree').should('be.visible');
      cy.get('.tree-header').should('be.visible');
      cy.get('.tree-controls').should('be.visible');
    });

    it('should display correctly on tablet viewport', () => {
      cy.viewport(768, 1024); // iPad
      
      cy.get('.family-tree').should('be.visible');
      cy.get('.tree-container').should('be.visible');
    });

    it('should display correctly on desktop viewport', () => {
      cy.viewport(1920, 1080); // Desktop
      
      cy.get('.family-tree').should('be.visible');
      cy.get('.tree-container').should('be.visible');
    });
  });

  describe('Accessibility', () => {
    beforeEach(() => {
      cy.wait('@getFamilyDetail');
    });

    it('should have proper button titles for screen readers', () => {
      cy.get('button[title="Zoom Out"]').should('have.attr', 'title', 'Zoom Out');
      cy.get('button[title="Zoom In"]').should('have.attr', 'title', 'Zoom In');
      cy.get('button[title="Reset View"]').should('have.attr', 'title', 'Reset View');
    });

    it('should have proper heading structure', () => {
      cy.get('h2').should('be.visible');
      cy.get('h2').should('contain', 'John Smith & Jane Doe');
    });

    it('should be keyboard navigable', () => {
      cy.get('.back-button').focus().should('be.focused');
      cy.get('button[title="Zoom In"]').focus().should('be.focused');
    });
  });

  describe('Data Validation', () => {
    it('should handle family with only husband', () => {
      const husbandOnlyFamily = {
        ...testFamilyData,
        wife: null,
        wife_id: null
      };

      cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
        statusCode: 200,
        body: husbandOnlyFamily
      }).as('getHusbandOnlyFamily');

      cy.visit(`/family/${testFamilyId}`);
      cy.wait('@getHusbandOnlyFamily');
      
      cy.get('h2').should('contain', 'John Smith');
      cy.get('.person-node.husband').should('be.visible');
      cy.get('.person-node.wife').should('not.exist');
    });

    it('should handle family with only wife', () => {
      const wifeOnlyFamily = {
        ...testFamilyData,
        husband: null,
        husband_id: null
      };

      cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
        statusCode: 200,
        body: wifeOnlyFamily
      }).as('getWifeOnlyFamily');

      cy.visit(`/family/${testFamilyId}`);
      cy.wait('@getWifeOnlyFamily');
      
      cy.get('h2').should('contain', 'Jane Doe');
      cy.get('.person-node.wife').should('be.visible');
      cy.get('.person-node.husband').should('not.exist');
    });

    it('should handle family with no children', () => {
      const noChildrenFamily = {
        ...testFamilyData,
        children: []
      };

      cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
        statusCode: 200,
        body: noChildrenFamily
      }).as('getNoChildrenFamily');

      cy.visit(`/family/${testFamilyId}`);
      cy.wait('@getNoChildrenFamily');
      
      cy.get('.children-row').should('not.exist');
      cy.get('.person-node.child').should('not.exist');
    });

    it('should handle family with multiple children', () => {
      const multipleChildrenFamily = {
        ...testFamilyData,
        children: [
          testFamilyData.children[0],
          {
            id: 'c2',
            family_id: testFamilyId,
            person_id: 'p2',
            person: {
              id: 'p2',
              first_name: 'Child2',
              last_name: 'Smith',
              sex: 'F',
              birth_date: '2012-08-15',
              death_date: null,
              birth_place: 'Boston, MA',
              death_place: null,
              occupation: null,
              notes: 'Second child',
              has_own_family: false,
              own_families: []
            }
          }
        ]
      };

      cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
        statusCode: 200,
        body: multipleChildrenFamily
      }).as('getMultipleChildrenFamily');

      cy.visit(`/family/${testFamilyId}`);
      cy.wait('@getMultipleChildrenFamily');
      
      cy.get('.person-node.child').should('have.length', 2);
      cy.contains('Child Smith').should('be.visible');
      cy.contains('Child2 Smith').should('be.visible');
    });
  });

  describe('Performance', () => {
    it('should load family tree within acceptable time', () => {
      const startTime = Date.now();
      
      cy.visit(`/family/${testFamilyId}`);
      cy.wait('@getFamilyDetail');
      
      cy.get('.tree-container').should('be.visible').then(() => {
        const loadTime = Date.now() - startTime;
        expect(loadTime).to.be.lessThan(5000); // Should load within 5 seconds
      });
    });

    it('should handle large family trees efficiently', () => {
      const largeFamilyData = {
        ...testFamilyData,
        children: Array.from({ length: 10 }, (_, i) => ({
          id: `c${i}`,
          family_id: testFamilyId,
          person_id: `p${i}`,
          person: {
            id: `p${i}`,
            first_name: `Child${i}`,
            last_name: 'Smith',
            sex: i % 2 === 0 ? 'M' : 'F',
            birth_date: `201${i}-01-01`,
            death_date: null,
            birth_place: 'Boston, MA',
            death_place: null,
            occupation: null,
            notes: `Child ${i} notes`,
            has_own_family: false,
            own_families: []
          }
        }))
      };

      cy.intercept('GET', `${API_URL}/api/v1/families/${testFamilyId}/detail`, {
        statusCode: 200,
        body: largeFamilyData
      }).as('getLargeFamily');

      cy.visit(`/family/${testFamilyId}`);
      cy.wait('@getLargeFamily');
      
      cy.get('.tree-container').should('be.visible');
      cy.get('.person-node.child').should('have.length', 10);
    });
  });
});