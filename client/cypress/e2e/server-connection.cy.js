describe('Server Connection', () => {
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000';

    it('should test API connectivity first', () => {
      cy.request('GET', `${apiUrl}/health`).then((response) => {
        expect(response.status).to.equal(200);
        cy.log('API server is reachable:', response.body);
      });
    });
});