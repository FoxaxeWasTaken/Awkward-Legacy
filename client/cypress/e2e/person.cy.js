describe('Person Creation UI', () => {
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000';

    it('should create a person via the UI form', () => {
      cy.intercept('POST', `http://localhost:8080/api/v1/persons`).as('createPerson');

      cy.visit('/family'); // Use relative URL since baseUrl is set in config

      cy.get('[data-cy="first-name"]').type('John');
      cy.get('[data-cy="last-name"]').type('Doe');
      cy.get('[data-cy="sex"]').select('Male');
      cy.get('[data-cy="birth-date"]').type('1980-05-15');
      cy.get('[data-cy="birth-place"]').type('New York');
      cy.get('[data-cy="notes"]').type('Test person');

      cy.get('[data-cy="submit"]').click();

      // Wait for the API call to complete
      cy.wait('@createPerson', { timeout: 10000 }).then((interception) => {
        if (interception.response) {
          expect(interception.response.statusCode).to.equal(200);
        } else {
          throw new Error('API request was not intercepted or no response received');
        }
      });

      // Check for success message
      cy.contains('Person created successfully!', { timeout: 10000 }).should('be.visible');
    });
});
