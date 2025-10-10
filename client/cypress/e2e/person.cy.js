/*describe('Person Creation', () => {
  const baseUrl = Cypress.config('baseUrl') || 'http://localhost:8000';

/!*  beforeEach(() => {
    // Clear any existing data or reset database state if needed
    cy.request('POST', `${baseUrl}/test/reset-db`);
  });*!/

  it('should successfully create a person with all fields', () => {
    const personData = {
      first_name: 'John',
      last_name: 'Doe',
      sex: 'M',
      birth_date: '1980-05-15',
      death_date: null,
      birth_place: 'New York, USA',
      death_place: null,
      occupation: 'Software Engineer',
      notes: 'Test person with complete data'
    };

    cy.request({
      method: 'POST',
      url: `${baseUrl}/persons`,
      body: personData
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body).to.have.property('id');
      expect(response.body.id).to.match(/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i);
      expect(response.body.first_name).to.eq(personData.first_name);
      expect(response.body.last_name).to.eq(personData.last_name);
      expect(response.body.sex).to.eq(personData.sex);
      expect(response.body.birth_date).to.eq(personData.birth_date);
      expect(response.body.birth_place).to.eq(personData.birth_place);
      expect(response.body.occupation).to.eq(personData.occupation);
      expect(response.body.notes).to.eq(personData.notes);
    });
  });

  it('should successfully create a person with only required fields', () => {
    const personData = {
      first_name: 'Jane',
      last_name: 'Smith',
      sex: 'F'
    };

    cy.request({
      method: 'POST',
      url: `${baseUrl}/persons`,
      body: personData
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body).to.have.property('id');
      expect(response.body.first_name).to.eq(personData.first_name);
      expect(response.body.last_name).to.eq(personData.last_name);
      expect(response.body.sex).to.eq(personData.sex);
      expect(response.body.birth_date).to.be.null;
      expect(response.body.death_date).to.be.null;
      expect(response.body.birth_place).to.be.null;
      expect(response.body.death_place).to.be.null;
      expect(response.body.occupation).to.be.null;
      expect(response.body.notes).to.be.null;
    });
  });

  it('should successfully create a person with sex as Unknown', () => {
    const personData = {
      first_name: 'Alex',
      last_name: 'Johnson',
      sex: 'U'
    };

    cy.request({
      method: 'POST',
      url: `${baseUrl}/persons`,
      body: personData
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body.sex).to.eq('U');
    });
  });

  it('should successfully create a deceased person', () => {
    const personData = {
      first_name: 'Robert',
      last_name: 'Williams',
      sex: 'M',
      birth_date: '1920-03-10',
      death_date: '2000-12-25',
      birth_place: 'London, UK',
      death_place: 'Manchester, UK',
      occupation: 'Historian'
    };

    cy.request({
      method: 'POST',
      url: `${baseUrl}/persons`,
      body: personData
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body.death_date).to.eq(personData.death_date);
      expect(response.body.death_place).to.eq(personData.death_place);
    });
  });

  it('should successfully create multiple persons', () => {
    const persons = [
      { first_name: 'Alice', last_name: 'Brown', sex: 'F' },
      { first_name: 'Bob', last_name: 'Davis', sex: 'M' },
      { first_name: 'Charlie', last_name: 'Wilson', sex: 'U' }
    ];

    const personIds = [];

    cy.wrap(persons).each((personData) => {
      cy.request({
        method: 'POST',
        url: `${baseUrl}/persons`,
        body: personData
      }).then((response) => {
        expect(response.status).to.eq(201);
        expect(response.body).to.have.property('id');
        personIds.push(response.body.id);
      });
    }).then(() => {
      // Verify all IDs are unique
      const uniqueIds = [...new Set(personIds)];
      expect(uniqueIds.length).to.eq(persons.length);
    });
  });

  it('should successfully create a person with special characters in names', () => {
    const personData = {
      first_name: "O'Connor",
      last_name: 'López-García',
      sex: 'M',
      occupation: 'Artist & Designer'
    };

    cy.request({
      method: 'POST',
      url: `${baseUrl}/persons`,
      body: personData
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body.first_name).to.eq(personData.first_name);
      expect(response.body.last_name).to.eq(personData.last_name);
    });
  });

  it('should successfully create a person with long notes', () => {
    const longNotes = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. '.repeat(20);
    const personData = {
      first_name: 'Emma',
      last_name: 'Taylor',
      sex: 'F',
      notes: longNotes
    };

    cy.request({
      method: 'POST',
      url: `${baseUrl}/persons`,
      body: personData
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body.notes).to.eq(longNotes);
    });
  });

  it('should persist the created person and be retrievable', () => {
    const personData = {
      first_name: 'David',
      last_name: 'Anderson',
      sex: 'M',
      birth_date: '1985-07-22',
      occupation: 'Teacher'
    };

    let createdId;

    cy.request({
      method: 'POST',
      url: `${baseUrl}/persons`,
      body: personData
    }).then((response) => {
      expect(response.status).to.eq(201);
      createdId = response.body.id;
    }).then(() => {
      // Attempt to retrieve the created person
      cy.request({
        method: 'GET',
        url: `${baseUrl}/persons/${createdId}`
      }).then((response) => {
        expect(response.status).to.eq(200);
        expect(response.body.id).to.eq(createdId);
        expect(response.body.first_name).to.eq(personData.first_name);
        expect(response.body.last_name).to.eq(personData.last_name);
      });
    });
  });

  it('should handle empty optional fields correctly', () => {
    const personData = {
      first_name: 'Sarah',
      last_name: 'Miller',
      sex: 'F',
      birth_date: null,
      death_date: null,
      birth_place: null,
      death_place: null,
      occupation: null,
      notes: null
    };

    cy.request({
      method: 'POST',
      url: `${baseUrl}/persons`,
      body: personData
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body.birth_date).to.be.null;
      expect(response.body.occupation).to.be.null;
    });
  });

  it('should create person with birth date but no death date (living person)', () => {
    const personData = {
      first_name: 'Michael',
      last_name: 'Thompson',
      sex: 'M',
      birth_date: '1995-11-08',
      death_date: null,
      occupation: 'Doctor'
    };

    cy.request({
      method: 'POST',
      url: `${baseUrl}/persons`,
      body: personData
    }).then((response) => {
      expect(response.status).to.eq(201);
      expect(response.body.birth_date).to.eq(personData.birth_date);
      expect(response.body.death_date).to.be.null;
    });
  });
});*/

describe('Person Creation UI', () => {
     const baseUrl = Cypress.config('baseUrl') || 'http://localhost:8000';
    it('should create a person via the UI form', () => {
        cy.visit('/family'); // Adjust route if needed

        cy.get('input[v-model="form.first_name"]').type('John');
        cy.get('input[v-model="form.last_name"]').type('Doe');
        cy.get('select[v-model="form.sex"]').select('Male');
        cy.get('input[v-model="form.birth_date"]').type('1980-05-15');
        cy.get('input[v-model="form.birth_place"]').type('New York');
        cy.get('textarea[v-model="form.notes"]').type('Test person');

        cy.get('button[type="submit"]').click();

        cy.contains('Person created successfully!').should('be.visible');
    });
});
