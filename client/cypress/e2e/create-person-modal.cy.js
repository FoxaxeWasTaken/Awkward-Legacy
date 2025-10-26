describe('Create Person Modal', () => {
  before(() => {
    // Clean the database completely before the test suite
    cy.cleanDatabase()
  })

  beforeEach(() => {
    // Visit the family creation page to access the modal
    cy.visit('/families/create')
  })

  after(() => {
    // Clean the database completely at the end of the test suite
    cy.cleanDatabase()
  })

  describe('Modal Opening and Closing', () => {
    it('should open modal when clicking "Créer" button for husband', () => {
      // The modal should not be visible initially
      cy.get('.modal-overlay').should('not.exist')

      // Click "Create" button for parent 1
      cy.get('[data-cy="create-husband-btn"]').click()

      // La modale doit s'ouvrir
      cy.get('.modal-overlay').should('be.visible')
      cy.get('.modal').should('be.visible')
      cy.get('.modal-header h3').should('contain.text', 'Create a New Person')
    })

    it('should open modal when clicking "Créer" button for wife', () => {
      cy.get('.modal-overlay').should('not.exist')

      // Click "Create" button for parent 2
      cy.get('[data-cy="create-wife-btn"]').click()

      cy.get('.modal-overlay').should('be.visible')
      cy.get('.modal').should('be.visible')
    })

    it('should close modal when clicking close button', () => {
      cy.get('[data-cy="create-husband-btn"]').click()
      cy.get('.modal').should('be.visible')

      cy.get('.close-btn').click()

      cy.get('.modal-overlay').should('not.exist')
    })

    it('should close modal when clicking overlay', () => {
      cy.get('[data-cy="create-husband-btn"]').click()
      cy.get('.modal').should('be.visible')

      // Cliquer sur l'overlay (en dehors de la modale)
      cy.get('.modal-overlay').click({ force: true })

      cy.get('.modal-overlay').should('not.exist')
    })

    it('should close modal when clicking cancel button', () => {
      cy.get('[data-cy="create-husband-btn"]').click()
      cy.get('.modal').should('be.visible')

      cy.get('[data-cy="cancel-person-creation"]').click()

      cy.get('.modal-overlay').should('not.exist')
    })

    it('should not close modal when clicking inside modal content', () => {
      cy.get('[data-cy="create-husband-btn"]').click()
      cy.get('.modal').should('be.visible')

      // Click inside the modal
      cy.get('.modal').click()

      // La modale doit rester ouverte
      cy.get('.modal').should('be.visible')
    })
  })

  describe('Form Fields', () => {
    beforeEach(() => {
      cy.get('[data-cy="create-husband-btn"]').click()
    })

    it('should display all form fields', () => {
      cy.get('[data-cy="new-person-first-name"]').should('be.visible')
      cy.get('[data-cy="new-person-last-name"]').should('be.visible')
      cy.get('[data-cy="new-person-sex"]').should('be.visible')
      cy.get('[data-cy="new-person-birth-date"]').should('be.visible')
      cy.get('[data-cy="new-person-birth-place"]').should('be.visible')
      cy.get('[data-cy="new-person-death-date"]').should('exist')
      cy.get('[data-cy="new-person-death-place"]').should('exist')
      cy.get('[data-cy="new-person-occupation"]').should('exist')
      cy.get('[data-cy="new-person-notes"]').should('exist')
    })

    it('should have required attribute on first name and last name', () => {
      cy.get('[data-cy="new-person-first-name"]').should('have.attr', 'required')
      cy.get('[data-cy="new-person-last-name"]').should('have.attr', 'required')
    })

    it('should have correct options in sex select', () => {
      cy.get('[data-cy="new-person-sex"]').find('option').should('have.length', 3)
      cy.get('[data-cy="new-person-sex"]').find('option').eq(0).should('have.text', 'Undefined')
      cy.get('[data-cy="new-person-sex"]').find('option').eq(1).should('have.text', 'Male')
      cy.get('[data-cy="new-person-sex"]').find('option').eq(2).should('have.text', 'Female')
    })

    it('should accept input in all text fields', () => {
      cy.get('[data-cy="new-person-first-name"]').type('Marie')
      cy.get('[data-cy="new-person-last-name"]').type('Curie')
      cy.get('[data-cy="new-person-birth-place"]').type('Varsovie')
      cy.get('[data-cy="new-person-death-place"]').type('Paris')
      cy.get('[data-cy="new-person-occupation"]').scrollIntoView().type('Physicienne')
      cy.get('[data-cy="new-person-notes"]').scrollIntoView().type('Pionnière en radioactivité')

      cy.get('[data-cy="new-person-first-name"]').should('have.value', 'Marie')
      cy.get('[data-cy="new-person-last-name"]').should('have.value', 'Curie')
      cy.get('[data-cy="new-person-birth-place"]').should('have.value', 'Varsovie')
      cy.get('[data-cy="new-person-death-place"]').should('have.value', 'Paris')
      cy.get('[data-cy="new-person-occupation"]').should('have.value', 'Physicienne')
      cy.get('[data-cy="new-person-notes"]').should('have.value', 'Pionnière en radioactivité')
    })

    it('should accept dates in date fields', () => {
      cy.get('[data-cy="new-person-birth-date"]').type('1867-11-07')
      cy.get('[data-cy="new-person-death-date"]').type('1934-07-04')

      cy.get('[data-cy="new-person-birth-date"]').should('have.value', '1867-11-07')
      cy.get('[data-cy="new-person-death-date"]').should('have.value', '1934-07-04')
    })

    it('should allow selecting sex', () => {
      cy.get('[data-cy="new-person-sex"]').select('F')
      cy.get('[data-cy="new-person-sex"]').should('have.value', 'F')

      cy.get('[data-cy="new-person-sex"]').select('M')
      cy.get('[data-cy="new-person-sex"]').should('have.value', 'M')

      cy.get('[data-cy="new-person-sex"]').select('U')
      cy.get('[data-cy="new-person-sex"]').should('have.value', 'U')
    })
  })

  describe('Form Validation', () => {
    beforeEach(() => {
      cy.get('[data-cy="create-husband-btn"]').click()
    })

    it('should prevent submission with empty required fields', () => {
      cy.get('[data-cy="create-person-submit"]').click()

      // La modale doit rester ouverte (validation HTML5)
      cy.get('.modal').should('be.visible')
    })

    it('should prevent submission with only first name', () => {
      cy.get('[data-cy="new-person-first-name"]').type('Pierre')
      cy.get('[data-cy="create-person-submit"]').click()

      cy.get('.modal').should('be.visible')
    })

    it('should prevent submission with only last name', () => {
      cy.get('[data-cy="new-person-last-name"]').type('Dupont')
      cy.get('[data-cy="create-person-submit"]').click()

      cy.get('.modal').should('be.visible')
    })
  })

  describe('Person Creation', () => {
    beforeEach(() => {
      cy.get('[data-cy="create-husband-btn"]').click()
    })

    it('should create person with minimal required fields', () => {
      cy.intercept('POST', '**/api/v1/persons', {
        statusCode: 201,
        body: {
          id: '123e4567-e89b-12d3-a456-426614174000',
          first_name: 'Albert',
          last_name: 'Einstein',
          sex: 'U',
          birth_date: null,
          birth_place: null,
          death_date: null,
          death_place: null,
          occupation: null,
          notes: null
        }
      }).as('createPerson')

      cy.get('[data-cy="new-person-first-name"]').type('Albert')
      cy.get('[data-cy="new-person-last-name"]').type('Einstein')

      cy.get('[data-cy="create-person-submit"]').click()
      cy.wait('@createPerson')

      // La modale doit se fermer
      cy.get('.modal-overlay').should('not.exist')

      // The person must be automatically selected
      cy.get('[data-cy="search-husband"]').should('have.value', 'Albert Einstein')

      // A success message must be displayed
      cy.get('.success-message').should('be.visible')
      cy.get('.success-message').should('contain.text', 'Person "Albert Einstein" created successfully')
    })

    it('should create person with all fields filled', () => {
      cy.intercept('POST', '**/api/v1/persons', {
        statusCode: 201,
        body: {
          id: '123e4567-e89b-12d3-a456-426614174001',
          first_name: 'Ada',
          last_name: 'Lovelace',
          sex: 'F',
          birth_date: '1815-12-10',
          birth_place: 'Londres',
          death_date: '1852-11-27',
          death_place: 'Londres',
          occupation: 'Mathématicienne',
          notes: 'Première programmeuse'
        }
      }).as('createPerson')

      cy.get('[data-cy="new-person-first-name"]').type('Ada')
      cy.get('[data-cy="new-person-last-name"]').type('Lovelace')
      cy.get('[data-cy="new-person-sex"]').select('F')
      cy.get('[data-cy="new-person-birth-date"]').type('1815-12-10')
      cy.get('[data-cy="new-person-birth-place"]').type('Londres')
      cy.get('[data-cy="new-person-death-date"]').type('1852-11-27')
      cy.get('[data-cy="new-person-death-place"]').type('Londres')
      cy.get('[data-cy="new-person-occupation"]').scrollIntoView().type('Mathématicienne')
      cy.get('[data-cy="new-person-notes"]').scrollIntoView().type('Première programmeuse')

      cy.get('[data-cy="create-person-submit"]').scrollIntoView().click()
      cy.wait('@createPerson')

      cy.get('.modal-overlay').should('not.exist')
      cy.get('[data-cy="search-husband"]').should('have.value', 'Ada Lovelace')
    })

    it('should create person for wife when modal opened from wife button', () => {
      // Fermer la modale actuelle
      cy.get('.close-btn').click()

      // Ouvrir la modale pour le parent 2 (wife)
      cy.get('[data-cy="create-wife-btn"]').click()

      cy.intercept('POST', '**/api/v1/persons', {
        statusCode: 201,
        body: {
          id: '123e4567-e89b-12d3-a456-426614174002',
          first_name: 'Grace',
          last_name: 'Hopper',
          sex: 'F',
          birth_date: null,
          birth_place: null,
          death_date: null,
          death_place: null,
          occupation: null,
          notes: null
        }
      }).as('createPerson')

      cy.get('[data-cy="new-person-first-name"]').type('Grace')
      cy.get('[data-cy="new-person-last-name"]').type('Hopper')
      cy.get('[data-cy="new-person-sex"]').select('F')

      cy.get('[data-cy="create-person-submit"]').click()
      cy.wait('@createPerson')

      cy.get('.modal-overlay').should('not.exist')

      // The person must be selected as wife
      cy.get('[data-cy="search-wife"]').should('have.value', 'Grace Hopper')
    })

    it('should handle API errors gracefully', () => {
      cy.intercept('POST', '**/api/v1/persons', {
        statusCode: 400,
        body: {
          detail: 'Validation error'
        }
      }).as('createPersonError')

      cy.get('[data-cy="new-person-first-name"]').type('Test')
      cy.get('[data-cy="new-person-last-name"]').type('Error')

      cy.get('[data-cy="create-person-submit"]').click()
      cy.wait('@createPersonError')

      // La modale doit rester ouverte
      cy.get('.modal').should('be.visible')

      // Un message d'erreur doit s'afficher
      cy.get('.field-error').should('be.visible')
      cy.get('.field-error').should('contain.text', 'Validation error')
    })
  })

  describe('Form Reset', () => {
    it('should reset form when closing and reopening modal', () => {
      cy.get('[data-cy="create-husband-btn"]').click()

      // Remplir le formulaire
      cy.get('[data-cy="new-person-first-name"]').type('Test')
      cy.get('[data-cy="new-person-last-name"]').type('User')
      cy.get('[data-cy="new-person-sex"]').select('M')
      cy.get('[data-cy="new-person-birth-place"]').type('Paris')

      // Fermer la modale
      cy.get('.close-btn').click()

      // Rouvrir la modale
      cy.get('[data-cy="create-husband-btn"]').click()

      // Fields must be empty
      cy.get('[data-cy="new-person-first-name"]').should('have.value', '')
      cy.get('[data-cy="new-person-last-name"]').should('have.value', '')
      cy.get('[data-cy="new-person-sex"]').should('have.value', 'U')
      cy.get('[data-cy="new-person-birth-place"]').should('have.value', '')
    })

    it('should reset form after successful creation', () => {
      cy.intercept('POST', '**/api/v1/persons', {
        statusCode: 201,
        body: {
          id: '123',
          first_name: 'John',
          last_name: 'Doe',
          sex: 'M'
        }
      }).as('createPerson')

      cy.get('[data-cy="create-husband-btn"]').click()

      cy.get('[data-cy="new-person-first-name"]').type('John')
      cy.get('[data-cy="new-person-last-name"]').type('Doe')

      cy.get('[data-cy="create-person-submit"]').click()
      cy.wait('@createPerson')

      // Rouvrir la modale
      cy.get('[data-cy="create-wife-btn"]').click()

      // Fields must be empty
      cy.get('[data-cy="new-person-first-name"]').should('have.value', '')
      cy.get('[data-cy="new-person-last-name"]').should('have.value', '')
    })
  })

  describe('Integration with Family Form', () => {
    it('should automatically select created person in parent select', () => {
      cy.intercept('POST', '**/api/v1/persons', {
        statusCode: 201,
        body: {
          id: '123e4567-e89b-12d3-a456-426614174003',
          first_name: 'Isaac',
          last_name: 'Newton',
          sex: 'U',
          birth_date: null,
          birth_place: null,
          death_date: null,
          death_place: null,
          occupation: null,
          notes: null
        }
      }).as('createPerson')

      cy.get('[data-cy="create-husband-btn"]').click()

      cy.get('[data-cy="new-person-first-name"]').type('Isaac')
      cy.get('[data-cy="new-person-last-name"]').type('Newton')

      cy.get('[data-cy="create-person-submit"]').click()
      cy.wait('@createPerson')

      // Check that the person is selected
      cy.get('[data-cy="search-husband"]').should('have.value', 'Isaac Newton')
    })

    it('should display person preview after creation', () => {
      cy.intercept('POST', '**/api/v1/persons', {
        statusCode: 201,
        body: {
          id: '456',
          first_name: 'Charles',
          last_name: 'Darwin',
          sex: 'M',
          birth_date: '1809-02-12',
          birth_place: 'Shrewsbury',
          death_date: null,
          death_place: null,
          notes: 'Naturaliste'
        }
      }).as('createPerson')

      cy.get('[data-cy="create-husband-btn"]').click()

      cy.get('[data-cy="new-person-first-name"]').type('Charles')
      cy.get('[data-cy="new-person-last-name"]').type('Darwin')

      cy.get('[data-cy="create-person-submit"]').click()
      cy.wait('@createPerson')

      // Check that the person preview is displayed
      cy.get('[data-cy="preview-husband"]').should('be.visible')
      cy.get('[data-cy="preview-husband"]').should('contain.text', 'Charles Darwin')
      cy.get('[data-cy="preview-husband"]').should('contain.text', '♂')
    })

    it('should allow creating multiple persons for different parents', () => {
      // Create the husband
      cy.get('[data-cy="create-husband-btn"]').click()
      
      cy.intercept('POST', '**/api/v1/persons', {
        statusCode: 201,
        body: {
          id: '123e4567-e89b-12d3-a456-426614174004',
          first_name: 'Romeo',
          last_name: 'Montague',
          sex: 'U',
          birth_date: null,
          birth_place: null,
          death_date: null,
          death_place: null,
          occupation: null,
          notes: null
        }
      }).as('createPerson1')

      cy.get('[data-cy="new-person-first-name"]').type('Romeo')
      cy.get('[data-cy="new-person-last-name"]').type('Montague')
      cy.get('[data-cy="create-person-submit"]').click()
      cy.wait('@createPerson1')

      // Create the wife
      cy.get('[data-cy="create-wife-btn"]').click()
      
      cy.intercept('POST', '**/api/v1/persons', {
        statusCode: 201,
        body: {
          id: '123e4567-e89b-12d3-a456-426614174005',
          first_name: 'Juliette',
          last_name: 'Capulet',
          sex: 'U',
          birth_date: null,
          birth_place: null,
          death_date: null,
          death_place: null,
          occupation: null,
          notes: null
        }
      }).as('createPerson2')

      cy.get('[data-cy="new-person-first-name"]').type('Juliette')
      cy.get('[data-cy="new-person-last-name"]').type('Capulet')
      cy.get('[data-cy="create-person-submit"]').click()
      cy.wait('@createPerson2')

      // Check that both persons are selected
      cy.get('[data-cy="search-husband"]').should('have.value', 'Romeo Montague')
      cy.get('[data-cy="search-wife"]').should('have.value', 'Juliette Capulet')
    })
  })

  describe('Loading States', () => {
    it('should disable submit button while creating person', () => {
      cy.intercept('POST', '**/api/v1/persons', (req) => {
        req.reply({
          delay: 1000, // Simulate network delay
          statusCode: 201,
          body: {
            id: '789',
            first_name: 'Test',
            last_name: 'User',
            sex: 'U'
          }
        })
      }).as('createPerson')

      cy.get('[data-cy="create-husband-btn"]').click()

      cy.get('[data-cy="new-person-first-name"]').type('Test')
      cy.get('[data-cy="new-person-last-name"]').type('User')

      cy.get('[data-cy="create-person-submit"]').click()

      // The button must be disabled during creation
      cy.get('[data-cy="create-person-submit"]').should('be.disabled')
      cy.get('[data-cy="create-person-submit"]').should('contain.text', 'Creating...')

      cy.wait('@createPerson')
    })
  })
})

