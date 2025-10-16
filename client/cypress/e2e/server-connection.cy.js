describe('Server Connection & CORS', () => {
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000';

    it('should test API connectivity', () => {
      cy.request('GET', `${apiUrl}/health`).then((response) => {
        expect(response.status).to.equal(200);
        cy.log('API server is reachable:', response.body);
      });
    });

    it('should allow cross-origin requests with proper CORS headers', () => {
      cy.request({
        method: 'GET',
        url: `${apiUrl}/`,
        headers: {
          'Origin': 'http://client-dev:5173'
        }
      }).then((response) => {
        expect(response.status).to.equal(200);
        expect(response.headers).to.have.property('access-control-allow-origin');
        expect(response.headers['access-control-allow-origin']).to.match(
          /http:\/\/client-dev:5173|http:\/\/localhost:5173/
        );
      });
    });

    it('should handle preflight OPTIONS request', () => {
      cy.request({
        method: 'OPTIONS',
        url: `${apiUrl}/api/persons`,
        headers: {
          'Origin': 'http://client-dev:5173',
          'Access-Control-Request-Method': 'POST',
          'Access-Control-Request-Headers': 'Content-Type'
        },
        failOnStatusCode: false
      }).then((response) => {
        expect(response.status).to.be.oneOf([200, 204]);
        expect(response.headers).to.have.property('access-control-allow-origin');
        expect(response.headers).to.have.property('access-control-allow-methods');
      });
    });
});