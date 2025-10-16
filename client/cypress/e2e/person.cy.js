describe('Person Creation UI', () => {
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000';

    it('should test API connectivity first', () => {
      // First, test if the API server is reachable
      cy.request('GET', `${apiUrl}/health`).then((response) => {
        expect(response.status).to.equal(200);
        cy.log('API server is reachable:', response.body);
      });
    });

    it('should create a person via the UI form', () => {
      cy.intercept('POST', `${apiUrl}/api/v1/persons/`).as('createPerson');

      cy.visit('/family'); // Use relative URL since baseUrl is set in config

      cy.get('[data-cy="first-name"]').type('John');
      cy.get('[data-cy="last-name"]').type('Doe');
      cy.get('[data-cy="sex"]').select('Male');
      cy.get('[data-cy="birth-place"]').type('New York');
      cy.get('[data-cy="notes"]').type('Test person');

      cy.get('[data-cy="submit"]').click();

      // Wait for the API call to complete
      cy.wait('@createPerson', { timeout: 10000 }).then((interception) => {
        if (interception.response) {
          expect(interception.response.statusCode).to.equal(201);
        } else {
          throw new Error('API request was not intercepted or no response received');
        }
      });

      // Check for success message
      cy.contains('Person created successfully!', { timeout: 10000 }).should('be.visible');
    });
});

describe('Person Creation UI - Failure Cases', () => {
  const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000';

  beforeEach(() => {
    cy.visit('/family');
  });

  it('should show error when required fields are missing', () => {
    // Try to submit without filling required fields
    cy.get('[data-cy="submit"]').click();

    // HTML5 validation should prevent submission
    cy.get('[data-cy="first-name"]:invalid').should('exist');
  });

  it('should show error when first name is missing', () => {
    cy.get('[data-cy="last-name"]').type('Doe');
    cy.get('[data-cy="sex"]').select('Male');

    cy.get('[data-cy="submit"]').click();

    cy.get('[data-cy="first-name"]:invalid').should('exist');
  });

  it('should show error when last name is missing', () => {
    cy.get('[data-cy="first-name"]').type('John');
    cy.get('[data-cy="sex"]').select('Male');

    cy.get('[data-cy="submit"]').click();

    cy.get('[data-cy="last-name"]:invalid').should('exist');
  });

  it('should show error when API returns 400 Bad Request', () => {
    cy.intercept('POST', `${apiUrl}/api/v1/persons/`, {
      statusCode: 400,
      body: { detail: 'Invalid data provided' }
    }).as('createPersonFail');

    cy.get('[data-cy="first-name"]').type('John');
    cy.get('[data-cy="last-name"]').type('Doe');
    cy.get('[data-cy="sex"]').select('Male');
    cy.get('[data-cy="submit"]').click();

    cy.wait('@createPersonFail');
    cy.contains('Invalid data provided').should('be.visible');
  });

  it('should show error when API returns 500 Server Error', () => {
    cy.intercept('POST', `${apiUrl}/api/v1/persons/`, {
      statusCode: 500,
      body: { detail: 'Internal server error' }
    }).as('createPersonError');

    cy.get('[data-cy="first-name"]').type('John');
    cy.get('[data-cy="last-name"]').type('Doe');
    cy.get('[data-cy="sex"]').select('Male');
    cy.get('[data-cy="submit"]').click();

    cy.wait('@createPersonError');
    cy.contains('Internal server error').should('be.visible');
  });

  it('should show error when network request fails', () => {
    cy.intercept('POST', `${apiUrl}/api/v1/persons/`, {
      forceNetworkError: true
    }).as('networkError');

    cy.get('[data-cy="first-name"]').type('John');
    cy.get('[data-cy="last-name"]').type('Doe');
    cy.get('[data-cy="sex"]').select('Male');
    cy.get('[data-cy="submit"]').click();

    cy.wait('@networkError');
    cy.contains('Failed to create person').should('be.visible');
  });

  it('should disable submit button while submitting', () => {
    cy.intercept('POST', `${apiUrl}/api/v1/persons/`, (req) => {
      req.reply((res) => {
        res.delay = 1000; // Add delay to simulate slow network
        res.send({ statusCode: 201, body: {} });
      });
    }).as('slowCreate');

    cy.get('[data-cy="first-name"]').type('John');
    cy.get('[data-cy="last-name"]').type('Doe');
    cy.get('[data-cy="sex"]').select('Male');
    cy.get('[data-cy="submit"]').click();

    // Button should be disabled during submission
    cy.get('[data-cy="submit"]').should('be.disabled');
  });
});
