describe('Create Family', () => {
  let johnId, janeId

  before(() => {
    // Clean the database completely before the test suite
    cy.cleanDatabase()

    // Create necessary persons once (chained to guarantee order)
    cy.createTestPerson({
      first_name: 'John',
      last_name: 'Doe',
      sex: 'M',
      birth_date: '1980-01-01'
    }).then((id) => {
      johnId = id
      return cy.createTestPerson({
        first_name: 'Jane',
        last_name: 'Smith',
        sex: 'F',
        birth_date: '1982-05-15'
      })
    }).then((id) => {
      janeId = id
    })
  })

  beforeEach(() => {
    // Ouvrir la page
    cy.visit('/families/create')
  })

  afterEach(() => {
    // Clean families after each test
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
    cy.request('GET', `${apiUrl}/api/v1/families?limit=1000`).then((response) => {
      const families = response.body
      families.forEach((family) => {
        cy.request({
          method: 'DELETE',
          url: `${apiUrl}/api/v1/families/${family.id}`,
          failOnStatusCode: false
        })
      })
    })
  })

  after(() => {
    // Clean the database completely at the end of the test suite
    cy.cleanDatabase()
  })

  it('should create a family with one parent', () => {
    // Check that elements exist
    cy.get('[data-cy="search-husband"]').should('be.visible')
    
    // Mocker la recherche de personnes
    cy.intercept('GET', '**/api/v1/persons/search*', {
      statusCode: 200,
      body: [
        {
          id: '123e4567-e89b-12d3-a456-426614174000',
          first_name: 'John',
          last_name: 'Doe',
          sex: 'M',
          birth_date: '1980-01-01',
          birth_place: 'New York',
          death_date: null,
          death_place: null,
          notes: 'Test person'
        }
      ]
    }).as('searchPersons')
    
    // Mock family creation
    cy.intercept('POST', '**/api/v1/families', {
      statusCode: 201,
      body: {
        id: 'family-123',
        husband_id: '123e4567-e89b-12d3-a456-426614174000',
        wife_id: null,
        marriage_date: null,
        marriage_place: null,
        notes: null
      }
    }).as('createFamily')
    
    // Search and select a parent via autocomplete
    cy.get('[data-cy="search-husband"]').clear().type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

    // Remplir les informations de mariage
    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    cy.get('[data-cy="marriage-place"]').type('New York')
    cy.get('[data-cy="family-notes"]').type('Premier mariage')

    // Soumettre le formulaire
    cy.get('[data-cy="submit-family"]').click()
    
    // Wait for family creation
    cy.wait('@createFamily')

    // Check success message
    cy.contains('Family created.').should('be.visible')
  })

  it('should create a family with two parents', () => {
    // Select the first parent
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

    // Select the second parent
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons2')
    cy.get('[data-cy="search-wife"]').type('Jane')
    cy.wait('@searchPersons2')
    cy.get('[data-cy="wife-suggestions"] .suggestion-item').first().click()

    // Remplir les informations
    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    cy.get('[data-cy="marriage-place"]').type('Paris')

    // Intercept family creation
    cy.intercept('POST', '**/api/v1/families').as('createFamily')
    
    // Soumettre
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily')

    // Wait a bit for the submit function to execute
    cy.wait(1000)
    
    // Debug: check what is displayed
    cy.get('body').then(($body) => {
      if ($body.find('.success-message').length > 0) {
        cy.get('.success-message').should('be.visible')
        cy.get('.success-message').should('contain.text', 'Family created.')
      } else if ($body.find('.error-message').length > 0) {
        cy.get('.error-message').then(($error) => {
          throw new Error(`Erreur affichée: ${$error.text()}`)
        })
      } else {
        throw new Error('Aucun message de succès ou d\'erreur trouvé')
      }
    })
  })

  it('should validate marriage date against parent birth dates', () => {
    // Select a parent with a known birth date
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

    // Essayer une date de mariage avant la naissance
    cy.get('[data-cy="marriage-date"]').type('1970-01-01')
    cy.get('[data-cy="marriage-date"]').blur() // Trigger validation

    // Check validation error
    cy.get('.field-error').should('be.visible')
    cy.get('.field-error').should('contain.text', "before the husband's birth")
  })

  it('should prevent future marriage dates', () => {
    // Select a parent
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

    // Essayer une date future
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const tomorrowStr = tomorrow.toISOString().split('T')[0]

    cy.get('[data-cy="marriage-date"]').type(tomorrowStr)
    cy.get('[data-cy="marriage-date"]').blur() // Trigger validation

    // Check error
    cy.get('.field-error').should('be.visible')
    cy.get('.field-error').should('contain.text', 'in the future')
  })

  it('should require at least one parent', () => {
    // Don't select any parents
    cy.get('[data-cy="marriage-date"]').type('2005-06-20')

    // Essayer de soumettre
    cy.get('[data-cy="submit-family"]').click()

    // Check error
    cy.contains('At least one parent is required.').should('be.visible')
  })

  it('should handle duplicate family creation error', () => {
    // Create unique persons for this test
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
    const timestamp = Date.now()
    let husbandId, wifeId
    
    cy.request('POST', `${apiUrl}/api/v1/persons`, {
      first_name: `Husband${timestamp}`, last_name: 'Test', sex: 'M', birth_date: '1980-01-01'
    }).then((response) => {
      husbandId = response.body.id
    })
    
    cy.request('POST', `${apiUrl}/api/v1/persons`, {
      first_name: `Wife${timestamp}`, last_name: 'Test', sex: 'F', birth_date: '1982-05-15'
    }).then((response) => {
      wifeId = response.body.id
    })

    // Create a first family via the interface
    cy.get('[data-cy="search-husband"]').type(`Husband${timestamp}`)
    cy.wait(600)
    cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

    cy.get('[data-cy="search-wife"]').type(`Wife${timestamp}`)
    cy.wait(500)
    cy.get('[data-cy="wife-suggestions"] .suggestion-item').first().click()

    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    
    // Intercept the first creation
    cy.intercept('POST', '**/api/v1/families').as('createFamily1')
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily1')
    
    // Check success of the first creation
    cy.get('.success-message').should('be.visible')
    cy.get('.success-message').should('contain.text', 'Family created.')

    // Now try to create the same family again
    cy.get('[data-cy="search-husband"]').clear().type(`Husband${timestamp}`)
    cy.wait(600)
    cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

    cy.get('[data-cy="search-wife"]').clear().type(`Wife${timestamp}`)
    cy.wait(500)
    cy.get('[data-cy="wife-suggestions"] .suggestion-item').first().click()

    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    
    // Intercept the second creation (which should fail)
    cy.intercept('POST', '**/api/v1/families').as('createFamily2')
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily2')
    
    // Check duplicate error
    cy.get('.error-message').should('be.visible')
    cy.get('.error-message').should('contain.text', 'already exists')
    
    // Clean up persons created for this test
    cy.then(() => {
      if (husbandId) {
        cy.request('DELETE', `${apiUrl}/api/v1/persons/${husbandId}`, { failOnStatusCode: false })
      }
      if (wifeId) {
        cy.request('DELETE', `${apiUrl}/api/v1/persons/${wifeId}`, { failOnStatusCode: false })
      }
    })
  })

  it('should reset form after successful creation', () => {
    // Create a family
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    cy.get('[data-cy="marriage-place"]').type('Paris')
    cy.get('[data-cy="family-notes"]').type('Test family')

    cy.get('[data-cy="submit-family"]').click()
    cy.contains('Family created.').should('be.visible')

    // Check that the form is reset
    cy.get('[data-cy="search-husband"]').should('have.value', '')
    cy.get('[data-cy="search-wife"]').should('have.value', '')
    cy.get('[data-cy="marriage-date"]').should('have.value', '')
    cy.get('[data-cy="marriage-place"]').should('have.value', '')
    cy.get('[data-cy="family-notes"]').should('have.value', '')
  })

  it('should show only create person buttons', () => {
    cy.get('[data-cy="create-husband-btn"]').should('be.visible').and('contain.text', 'Create')
    cy.get('[data-cy="create-wife-btn"]').should('be.visible').and('contain.text', 'Create')
  })

  it('should open create person modal and create a new person', () => {
    // Open person creation modal for husband
    cy.get('[data-cy="create-husband-btn"]').click()
    
    // Check that the modal opens
    cy.get('.modal').should('be.visible')
    cy.get('.modal-header h3').should('contain.text', 'Create a New Person')
    
    // Fill the form
    cy.get('[data-cy="new-person-first-name"]').type('Jean')
    cy.get('[data-cy="new-person-last-name"]').type('Dupont')
    cy.get('[data-cy="new-person-sex"]').select('M')
    cy.get('[data-cy="new-person-birth-date"]').type('1975-03-15')
    cy.get('[data-cy="new-person-birth-place"]').type('Paris')
    cy.get('[data-cy="new-person-notes"]').type('Personne créée via modale')
    
    // Intercept person creation
    cy.intercept('POST', '**/api/v1/persons').as('createPerson')
    
    // Soumettre le formulaire
    cy.get('[data-cy="create-person-submit"]').click()
    cy.wait('@createPerson')
    
    // Check that the modal closes
    cy.get('.modal').should('not.exist')
    
    // Check that the person was automatically selected (input filled)
    cy.get('[data-cy="search-husband"]').should('have.value', 'Jean Dupont')
    cy.get('[data-cy="preview-husband"]').should('be.visible')
    cy.get('[data-cy="preview-husband"]').should('contain.text', 'Jean Dupont')
    cy.get('[data-cy="preview-husband"]').should('contain.text', '♂')
    
    // Check success message
    cy.get('.success-message').should('be.visible')
    cy.get('.success-message').should('contain.text', 'Person "Jean Dupont" created successfully')
  })

  it('should validate required fields in create person modal', () => {
    // Open person creation modal
    cy.get('[data-cy="create-husband-btn"]').click()
    
    // Check that fields have the 'required' attribute
    cy.get('[data-cy="new-person-first-name"]').should('have.attr', 'required')
    cy.get('[data-cy="new-person-last-name"]').should('have.attr', 'required')
    
    // Try to fill only the first name (not the last name)
    cy.get('[data-cy="new-person-first-name"]').type('Test')
    cy.get('[data-cy="create-person-submit"]').click()
    
    // The browser should prevent submission with HTML5 validation
    // The modal should remain open
    cy.get('.modal').should('be.visible')
    
    // Close the modal
    cy.get('.close-btn').click()
    cy.get('.modal').should('not.exist')
  })

  it('should add existing children to the family', () => {
    // Create a person who will be a child
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
    
    cy.request('POST', `${apiUrl}/api/v1/persons`, {
      first_name: 'Charlie',
      last_name: 'TestChild',
      sex: 'U',
      birth_date: '2010-01-01'
    }).as('createChild').then((response) => {
      const childId = response.body.id

      // Select parents
      cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
      cy.get('[data-cy="search-husband"]').type('John')
      cy.wait('@searchPersons')
      cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

      // Scroll vers le haut pour s'assurer que la section enfants est visible
      cy.scrollTo('top')
      
      // Click "Add child" button to make elements visible
      cy.get('[data-cy="add-child-button"]').should('be.visible').click()
      
      // Check that the children section now exists
      cy.get('[data-cy="search-child"]').should('exist')
      
      // Search and add the child via autocomplete
      cy.get('[data-cy="search-child"]').scrollIntoView().should('be.visible')
      cy.get('[data-cy="search-child"]').type('Charlie')
      cy.wait('@searchPersons')
      cy.get('[data-cy="child-suggestions"] .suggestion-item').first().click()

      // Check that the child input contains the selected child name (label may include extra info)
      cy.get('[data-cy="search-child"]').should('contain.value', 'Charlie TestChild')

      // Create the family
      cy.intercept('POST', '**/api/v1/families').as('createFamily')
      cy.intercept('POST', '**/api/v1/children').as('createChildRelation')
      cy.get('[data-cy="submit-family"]').click()
      cy.wait('@createFamily')
      cy.wait('@createChildRelation', { timeout: 10000 })

      // Check success message
      cy.get('.success-message').should('be.visible')
      cy.get('.success-message').should('contain.text', 'Family created with 1 child')

      // Clean up created child
      cy.request('DELETE', `${apiUrl}/api/v1/persons/${childId}`, { failOnStatusCode: false })
    })
  })

  it('should add multiple children to the family', () => {
    // Create two children
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
    const childIds = []
    
    cy.request('POST', `${apiUrl}/api/v1/persons`, {
      first_name: 'Alice',
      last_name: 'Child',
      sex: 'F',
      birth_date: '2008-05-15'
    }).then((response) => {
      childIds.push(response.body.id)
    })

    cy.request('POST', `${apiUrl}/api/v1/persons`, {
      first_name: 'Bob',
      last_name: 'Child',
      sex: 'M',
      birth_date: '2012-08-20'
    }).then((response) => {
      childIds.push(response.body.id)
    })

    // Sélectionner les parents
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

    cy.get('[data-cy="search-wife"]').type('Jane')
    cy.wait('@searchPersons')
    cy.get('[data-cy="wife-suggestions"] .suggestion-item').first().click()

    // Scroll vers le haut pour s'assurer que la section enfants est visible
    cy.scrollTo('top')
    
    // Cliquer sur le bouton "Ajouter un enfant" pour rendre les éléments visibles
    cy.get('[data-cy="add-child-button"]').should('be.visible').click()
    
    // Ajouter le premier enfant (utiliser John Doe)
    cy.get('[data-cy="search-child"]').scrollIntoView().should('be.visible')
    cy.get('[data-cy="search-child"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="child-suggestions"] .suggestion-item').contains('John Doe').click({ force: true })

    // Add the second child (use Jane Smith)
    cy.get('[data-cy="add-child-button"]').click()
    cy.get('[data-cy="children-list"]').eq(1).find('[data-cy="search-child"]').clear().type('Jane')
    cy.wait('@searchPersons')
    cy.get('[data-cy="children-list"]').eq(1).find('[data-cy="child-suggestions"] .suggestion-item').contains('Jane Smith').click({ force: true })

    // Check that two children have been added
    cy.get('[data-cy="children-list"]').should('have.length', 2)

    // Create the family
    cy.intercept('POST', '**/api/v1/families').as('createFamily')
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily')

    // Check success message
    cy.get('.success-message').should('contain.text', 'Family created with 2 children')

    // Clean up created children
    cy.then(() => {
      childIds.forEach(id => {
        cy.request('DELETE', `${apiUrl}/api/v1/persons/${id}`, { failOnStatusCode: false })
      })
    })
  })

  it('should remove a child from the list before submission', () => {
    // Create a child
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
    
    cy.request('POST', `${apiUrl}/api/v1/persons`, {
      first_name: 'ToRemove',
      last_name: 'Child',
      sex: 'U',
      birth_date: '2010-01-01'
    }).then((response) => {
      const childId = response.body.id

      // Select a parent via autocomplete
      cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
      cy.get('[data-cy="search-husband"]').type('John')
      cy.wait('@searchPersons')
      cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

      // Scroll vers le haut pour s'assurer que la section enfants est visible
      cy.scrollTo('top')
      
      // Click "Add child" button to make elements visible
      cy.get('[data-cy="add-child-button"]').should('be.visible').click()
      
      // Ajouter l'enfant
      cy.get('[data-cy="search-child"]').scrollIntoView().should('be.visible')
      cy.get('[data-cy="search-child"]').type('ToRemove')
      cy.wait('@searchPersons')
      cy.get('[data-cy=\"child-suggestions\"] .suggestion-item').first().click()

      // Check that the child input contains the selected child name
      cy.get('[data-cy="search-child"]').should('contain.value', 'ToRemove')

      // Remove the child
      cy.get('[data-cy="remove-child-btn"]').click()

      // Check that the child is removed
      cy.get('[data-cy="children-list"]').should('not.exist')

      // Clean up created child
      cy.request('DELETE', `${apiUrl}/api/v1/persons/${childId}`, { failOnStatusCode: false })
    })
  })

  it('should create a new child via modal and add to family', () => {
    // Select a parent
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()

    // Scroll vers le haut pour s'assurer que la section enfants est visible
    cy.scrollTo('top')
    
    // Cliquer sur le bouton "Ajouter un enfant" pour rendre les éléments visibles
    cy.get('[data-cy="add-child-button"]').should('be.visible').click()
    
    // Open modal to create a child
    cy.get('[data-cy="create-child-button"]').scrollIntoView().should('be.visible')
    cy.get('[data-cy="create-child-button"]').click()
    cy.get('.modal').should('be.visible')

    // Fill the form
    cy.get('[data-cy="new-person-first-name"]').type('NewChild')
    cy.get('[data-cy="new-person-last-name"]').type('Created')
    cy.get('[data-cy="new-person-birth-date"]').type('2015-03-10')

    // Soumettre
    cy.intercept('POST', '**/api/v1/persons').as('createPerson')
    cy.get('[data-cy="create-person-submit"]').click()
    cy.wait('@createPerson')

    // Check that the modal closes and the child is added
    cy.get('.modal').should('not.exist')
      // Check that the created child name is filled in the input
    cy.get('[data-cy="search-child"]').should('contain.value', 'NewChild Created')

    // Create the family
    cy.intercept('POST', '**/api/v1/families').as('createFamily')
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily')

    // Check success message
    cy.get('.success-message').should('contain.text', 'Family created with 1 child')
  })

  it('should create a family with events', () => {
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
    let createdPersonIds = []
    let husbandId, wifeId

    // Créer deux personnes via API pour les parents
    cy.createTestPerson({
      first_name: 'EventTest',
      last_name: 'Father',
      sex: 'M',
      birth_date: '1970-01-01'
    }).then((id) => {
      husbandId = id
      createdPersonIds.push(id)
    })

    cy.createTestPerson({
      first_name: 'EventTest',
      last_name: 'Mother',
      sex: 'F',
      birth_date: '1972-05-15'
    }).then((id) => {
      wifeId = id
      createdPersonIds.push(id)
    }).then(() => {
      // Attendre que les deux personnes soient créées avant de visiter la page
      cy.visit('/families/create')

      // Sélectionner le mari (via suggestions, contenant "Father")
      cy.intercept('GET', '**/api/v1/persons/search*').as('searchHusband')
      cy.get('[data-cy="search-husband"]').type('EventTest')
      cy.wait('@searchHusband')
      cy.get('[data-cy="husband-suggestions"] .suggestion-item').contains('Father').first().click()

      // Sélectionner la femme (via suggestions, contenant "Mother")
      cy.intercept('GET', '**/api/v1/persons/search*').as('searchWife')
      cy.get('[data-cy="search-wife"]').type('EventTest')
      cy.wait('@searchWife')
      cy.get('[data-cy="wife-suggestions"] .suggestion-item').contains('Mother').first().click()
    })

    // Ajouter un événement de mariage
    cy.get('[data-cy="add-event-btn"]').scrollIntoView().should('be.visible')
    cy.get('[data-cy="add-event-btn"]').click()
    cy.get('[data-cy="event-0"]').should('exist')
    cy.get('[data-cy="event-type-0"]').should('be.visible')
    cy.get('[data-cy="event-type-0"]').select('Marriage')
    cy.get('[data-cy="event-date-0"]').type('2000-06-15')
    cy.get('[data-cy="event-place-0"]').type('Paris, France')
    cy.get('[data-cy="event-description-0"]').type('Cérémonie à l\'église Saint-Sulpice')

    // Ajouter un deuxième événement
    cy.get('[data-cy="add-event-btn"]').click()
    cy.get('[data-cy="event-1"]').should('exist')
    cy.get('[data-cy="event-type-1"]').select('Engagement')
    cy.get('[data-cy="event-date-1"]').type('1999-12-25')
    cy.get('[data-cy="event-place-1"]').type('Lyon, France')

    // Vérifier que les deux événements sont présents
    cy.get('[data-cy="event-0"]').should('be.visible')
    cy.get('[data-cy="event-1"]').should('be.visible')

    // Create the family
    cy.intercept('POST', '**/api/v1/families').as('createFamily')
    cy.intercept('POST', '**/api/v1/events').as('createEvent')
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily')
    cy.wait('@createEvent')

    // Check success message
    cy.get('.success-message').should('contain.text', 'Family created with 2 events')

    // Nettoyer les personnes créées
    cy.then(() => {
      createdPersonIds.forEach((personId) => {
        cy.request({
          method: 'DELETE',
          url: `${apiUrl}/api/v1/persons/${personId}`,
          failOnStatusCode: false
        })
      })
    })
  })

  it('should allow removing events before submission', () => {
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
    let createdPersonIds = []

    // Créer une personne pour le test
    cy.createTestPerson({
      first_name: 'RemoveEvent',
      last_name: 'Test',
      sex: 'M',
      birth_date: '1980-01-01'
    }).then((id) => {
      createdPersonIds.push(id)
    }).then(() => {
      cy.visit('/families/create')

      // Select a parent
      cy.intercept('GET', '**/api/v1/persons/search*').as('searchPerson')
      cy.get('[data-cy="search-husband"]').type('RemoveEvent')
      cy.wait('@searchPerson')
      cy.get('[data-cy="husband-suggestions"] .suggestion-item').first().click()
    })

    // Ajouter deux événements
    cy.get('[data-cy="add-event-btn"]').scrollIntoView().should('be.visible')
    cy.get('[data-cy="add-event-btn"]').click()
    cy.get('[data-cy="add-event-btn"]').click()
    // Vérifier que les deux événements sont présents
    cy.get('[data-cy="event-0"]').should('be.visible')
    cy.get('[data-cy="event-1"]').should('be.visible')

    // Supprimer le premier événement
    cy.get('[data-cy="remove-event-0"]').click()
    cy.get('[data-cy="event-0"]').should('exist')
    cy.get('[data-cy="event-1"]').should('not.exist')

    // Nettoyer les personnes créées
    cy.then(() => {
      createdPersonIds.forEach((personId) => {
        cy.request({
          method: 'DELETE',
          url: `${apiUrl}/api/v1/persons/${personId}`,
          failOnStatusCode: false
        })
      })
    })
  })

  it('should validate event types are available', () => {
    cy.visit('/families/create')

    // Ajouter un événement
    cy.get('[data-cy="add-event-btn"]').scrollIntoView().should('be.visible')
    cy.get('[data-cy="add-event-btn"]').click()

    // Vérifier que tous les types d'événements sont disponibles
    const expectedEventTypes = [
      'Marriage',
      'Couple',
      'Engagement',
      'Divorce',
      'Separation',
      'Cohabitation',
      'Marriage Annulment'
    ]

    cy.get('[data-cy="event-type-0"]').should('be.visible')
    cy.get('[data-cy="event-type-0"]').then(($select) => {
      expectedEventTypes.forEach((eventType) => {
        cy.wrap($select).should('contain', eventType)
      })
    })
  })

  it('should navigate back to home when clicking back to home button', () => {
    // Vérifier que le bouton "Retour à l'accueil" est présent
    cy.get('[data-cy="back-to-home"]').should('be.visible')
    cy.get('[data-cy="back-to-home"]').should('contain', 'Go back to home')
    
    // Cliquer sur le bouton
    cy.get('[data-cy="back-to-home"]').click()
    
    // Vérifier que nous sommes redirigés vers la page d'accueil
    cy.url().should('eq', Cypress.config().baseUrl + '/')
    
    // Vérifier que la page d'accueil est chargée avec les cartes d'action
    cy.get('.action-cards').should('be.visible')
    cy.get('.action-card').should('have.length.at.least', 2)
  })
})

