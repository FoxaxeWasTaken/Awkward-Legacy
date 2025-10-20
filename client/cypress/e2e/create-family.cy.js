describe('Create Family', () => {
  let johnId, janeId

  before(() => {
    // Nettoyer complètement la base de données avant la suite de tests
    cy.cleanDatabase()

    // Créer les personnes nécessaires une seule fois
    cy.createTestPerson({
      first_name: 'John',
      last_name: 'Doe',
      sex: 'M',
      birth_date: '1980-01-01'
    }).then((id) => {
      johnId = id
    })

    cy.createTestPerson({
      first_name: 'Jane',
      last_name: 'Smith',
      sex: 'F',
      birth_date: '1982-05-15'
    }).then((id) => {
      janeId = id
    })
  })

  beforeEach(() => {
    // Ouvrir la page
    cy.visit('/families/create')
  })

  afterEach(() => {
    // Nettoyer les familles après chaque test
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
    // Nettoyer complètement la base de données à la fin de la suite de tests
    cy.cleanDatabase()
  })

  it('should create a family with one parent', () => {
    // Rechercher et sélectionner un parent
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    // Sélectionner la première option non vide
    cy.get('[data-cy="select-husband"]').find('option').its('length').should('be.greaterThan', 1)
    cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
      const val = $opt.val()
      cy.get('[data-cy="select-husband"]').select(val)
    })

    // Remplir les informations de mariage
    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    cy.get('[data-cy="marriage-place"]').type('New York')
    cy.get('[data-cy="notes"]').type('Premier mariage')

    // Soumettre le formulaire
    cy.get('[data-cy="submit-family"]').click()

    // Vérifier le message de succès
    cy.contains('Famille créée.').should('be.visible')
  })

  it('should create a family with two parents', () => {
    // Sélectionner le premier parent
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="select-husband"]').find('option').its('length').should('be.greaterThan', 1)
    cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-husband"]').select($opt.val())
    })

    // Sélectionner le deuxième parent
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons2')
    cy.get('[data-cy="search-wife"]').type('Jane')
    cy.wait('@searchPersons2')
    cy.get('[data-cy="select-wife"]').find('option').its('length').should('be.greaterThan', 1)
    cy.get('[data-cy="select-wife"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-wife"]').select($opt.val())
    })

    // Remplir les informations
    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    cy.get('[data-cy="marriage-place"]').type('Paris')

    // Intercepter la création de famille
    cy.intercept('POST', '**/api/v1/families').as('createFamily')
    
    // Soumettre
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily')

    // Attendre un peu pour que la fonction submit s'exécute
    cy.wait(1000)
    
    // Debug: vérifier ce qui est affiché
    cy.get('body').then(($body) => {
      if ($body.find('.success').length > 0) {
        cy.get('.success').should('be.visible')
        cy.get('.success').should('contain.text', 'Famille créée.')
      } else if ($body.find('.error').length > 0) {
        cy.get('.error').then(($error) => {
          throw new Error(`Erreur affichée: ${$error.text()}`)
        })
      } else {
        throw new Error('Aucun message de succès ou d\'erreur trouvé')
      }
    })
  })

  it('should validate marriage date against parent birth dates', () => {
    // Sélectionner un parent avec une date de naissance connue
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-husband"]').select($opt.val())
    })

    // Essayer une date de mariage avant la naissance
    cy.get('[data-cy="marriage-date"]').type('1970-01-01')
    cy.get('[data-cy="marriage-date"]').blur() // Déclencher la validation

    // Vérifier l'erreur de validation
    cy.get('.field-error').should('be.visible')
    cy.get('.field-error').should('contain.text', 'avant la naissance')
  })

  it('should prevent future marriage dates', () => {
    // Sélectionner un parent
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-husband"]').select($opt.val())
    })

    // Essayer une date future
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const tomorrowStr = tomorrow.toISOString().split('T')[0]

    cy.get('[data-cy="marriage-date"]').type(tomorrowStr)
    cy.get('[data-cy="marriage-date"]').blur() // Déclencher la validation

    // Vérifier l'erreur
    cy.get('.field-error').should('be.visible')
    cy.get('.field-error').should('contain.text', 'dans le futur')
  })

  it('should require at least one parent', () => {
    // Ne pas sélectionner de parents
    cy.get('[data-cy="marriage-date"]').type('2005-06-20')

    // Essayer de soumettre
    cy.get('[data-cy="submit-family"]').click()

    // Vérifier l'erreur
    cy.contains('Au moins un parent est requis.').should('be.visible')
  })

  it('should handle duplicate family creation error', () => {
    // Créer des personnes uniques pour ce test
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

    // Créer une première famille via l'interface
    cy.get('[data-cy="search-husband"]').type(`Husband${timestamp}`)
    cy.wait(600)
    cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-husband"]').select($opt.val())
    })

    cy.get('[data-cy="search-wife"]').type(`Wife${timestamp}`)
    cy.wait(500)
    cy.get('[data-cy="select-wife"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-wife"]').select($opt.val())
    })

    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    
    // Intercepter la première création
    cy.intercept('POST', '**/api/v1/families').as('createFamily1')
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily1')
    
    // Vérifier le succès de la première création
    cy.get('.success').should('be.visible')
    cy.get('.success').should('contain.text', 'Famille créée.')

    // Maintenant essayer de créer la même famille à nouveau
    cy.get('[data-cy="search-husband"]').clear().type(`Husband${timestamp}`)
    cy.wait(600)
    cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-husband"]').select($opt.val())
    })

    cy.get('[data-cy="search-wife"]').clear().type(`Wife${timestamp}`)
    cy.wait(500)
    cy.get('[data-cy="select-wife"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-wife"]').select($opt.val())
    })

    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    
    // Intercepter la deuxième création (qui devrait échouer)
    cy.intercept('POST', '**/api/v1/families').as('createFamily2')
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily2')
    
    // Vérifier l'erreur de doublon
    cy.get('.error').should('be.visible')
    cy.get('.error').should('contain.text', 'already exists')
    
    // Nettoyer les personnes créées pour ce test
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
    // Créer une famille
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-husband"]').select($opt.val())
    })

    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    cy.get('[data-cy="marriage-place"]').type('Paris')
    cy.get('[data-cy="notes"]').type('Test family')

    cy.get('[data-cy="submit-family"]').click()
    cy.contains('Famille créée.').should('be.visible')

    // Vérifier que le formulaire est réinitialisé
    cy.get('[data-cy="search-husband"]').should('have.value', '')
    cy.get('[data-cy="search-wife"]').should('have.value', '')
    cy.get('[data-cy="marriage-date"]').should('have.value', '')
    cy.get('[data-cy="marriage-place"]').should('have.value', '')
    cy.get('[data-cy="notes"]').should('have.value', '')
  })

  it('should show only create person buttons', () => {
    cy.contains('Créer').should('be.visible')
    cy.get('[data-cy="search-husband"]').parent().contains('Créer').should('be.visible')
    cy.get('[data-cy="search-wife"]').parent().contains('Créer').should('be.visible')
    cy.contains('Lier').should('not.exist')
  })

  it('should open create person modal and create a new person', () => {
    // Ouvrir la modale de création de personne pour le husband
    cy.get('[data-cy="search-husband"]').parent().find('button').click()
    
    // Vérifier que la modale s'ouvre
    cy.get('.modal').should('be.visible')
    cy.get('.modal-header h3').should('contain.text', 'Créer une nouvelle personne')
    
    // Remplir le formulaire
    cy.get('[data-cy="new-person-first-name"]').type('Jean')
    cy.get('[data-cy="new-person-last-name"]').type('Dupont')
    cy.get('[data-cy="new-person-sex"]').select('M')
    cy.get('[data-cy="new-person-birth-date"]').type('1975-03-15')
    cy.get('[data-cy="new-person-birth-place"]').type('Paris')
    cy.get('[data-cy="new-person-notes"]').type('Personne créée via modale')
    
    // Intercepter la création de personne
    cy.intercept('POST', '**/api/v1/persons').as('createPerson')
    
    // Soumettre le formulaire
    cy.get('[data-cy="create-person-submit"]').click()
    cy.wait('@createPerson')
    
    // Vérifier que la modale se ferme
    cy.get('.modal').should('not.exist')
    
    // Vérifier que la personne a été sélectionnée automatiquement
    cy.get('[data-cy="select-husband"]').should('contain.text', 'Jean Dupont')
    cy.get('[data-cy="preview-husband"]').should('be.visible')
    cy.get('[data-cy="preview-husband"]').should('contain.text', 'Jean Dupont')
    cy.get('[data-cy="preview-husband"]').should('contain.text', 'Sexe: M')
    
    // Vérifier le message de succès
    cy.get('.success').should('be.visible')
    cy.get('.success').should('contain.text', 'Personne "Jean Dupont" créée avec succès')
  })

  it('should validate required fields in create person modal', () => {
    // Ouvrir la modale de création de personne
    cy.get('[data-cy="search-husband"]').parent().find('button').click()
    
    // Vérifier que les champs ont l'attribut 'required'
    cy.get('[data-cy="new-person-first-name"]').should('have.attr', 'required')
    cy.get('[data-cy="new-person-last-name"]').should('have.attr', 'required')
    
    // Essayer de remplir seulement le prénom (pas le nom)
    cy.get('[data-cy="new-person-first-name"]').type('Test')
    cy.get('[data-cy="create-person-submit"]').click()
    
    // Le navigateur devrait empêcher la soumission avec la validation HTML5
    // La modale devrait rester ouverte
    cy.get('.modal').should('be.visible')
    
    // Fermer la modale
    cy.get('.close-btn').click()
    cy.get('.modal').should('not.exist')
  })

  it('should add existing children to the family', () => {
    // Créer une personne qui sera un enfant
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
    
    cy.request('POST', `${apiUrl}/api/v1/persons`, {
      first_name: 'Charlie',
      last_name: 'TestChild',
      sex: 'U',
      birth_date: '2010-01-01'
    }).as('createChild').then((response) => {
      const childId = response.body.id

      // Sélectionner les parents
      cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
      cy.get('[data-cy="search-husband"]').type('John')
      cy.wait('@searchPersons')
      cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
        cy.get('[data-cy="select-husband"]').select($opt.val())
      })

      // Rechercher et ajouter l'enfant
      cy.get('[data-cy="search-child"]').type('Charlie')
      cy.wait('@searchPersons')
      cy.get('[data-cy="select-child"]').find('option').eq(1).then(($opt) => {
        cy.get('[data-cy="select-child"]').select($opt.val())
      })

      // Vérifier que l'enfant est ajouté à la liste
      cy.get('[data-cy="children-list"]').should('be.visible')
      cy.get('[data-cy="children-list"]').should('contain', 'Charlie TestChild')

      // Vérifier que le compteur d'enfants est mis à jour
      cy.contains('Enfants (1)').should('be.visible')

      // Créer la famille
      cy.intercept('POST', '**/api/v1/families').as('createFamily')
      cy.intercept('POST', '**/api/v1/children').as('createChildRelation')
      cy.get('[data-cy="submit-family"]').click()
      cy.wait('@createFamily')
      cy.wait('@createChildRelation', { timeout: 10000 })

      // Vérifier le message de succès
      cy.get('.success').should('be.visible')
      cy.get('.success').should('contain.text', 'Famille créée avec 1 enfant')

      // Nettoyer l'enfant créé
      cy.request('DELETE', `${apiUrl}/api/v1/persons/${childId}`, { failOnStatusCode: false })
    })
  })

  it('should add multiple children to the family', () => {
    // Créer deux enfants
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
    cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-husband"]').select($opt.val())
    })

    cy.get('[data-cy="search-wife"]').type('Jane')
    cy.wait('@searchPersons')
    cy.get('[data-cy="select-wife"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-wife"]').select($opt.val())
    })

    // Ajouter le premier enfant
    cy.get('[data-cy="search-child"]').type('Alice')
    cy.wait('@searchPersons')
    cy.get('[data-cy="select-child"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-child"]').select($opt.val())
    })

    // Ajouter le deuxième enfant
    cy.get('[data-cy="search-child"]').clear().type('Bob')
    cy.wait('@searchPersons')
    cy.get('[data-cy="select-child"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-child"]').select($opt.val())
    })

    // Vérifier que les deux enfants sont dans la liste
    cy.get('[data-cy="children-list"]').should('contain', 'Alice Child')
    cy.get('[data-cy="children-list"]').should('contain', 'Bob Child')
    cy.contains('Enfants (2)').should('be.visible')

    // Créer la famille
    cy.intercept('POST', '**/api/v1/families').as('createFamily')
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily')

    // Vérifier le message de succès
    cy.get('.success').should('contain.text', 'Famille créée avec 2 enfants')

    // Nettoyer les enfants créés
    cy.then(() => {
      childIds.forEach(id => {
        cy.request('DELETE', `${apiUrl}/api/v1/persons/${id}`, { failOnStatusCode: false })
      })
    })
  })

  it('should remove a child from the list before submission', () => {
    // Créer un enfant
    const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
    
    cy.request('POST', `${apiUrl}/api/v1/persons`, {
      first_name: 'ToRemove',
      last_name: 'Child',
      sex: 'U',
      birth_date: '2010-01-01'
    }).then((response) => {
      const childId = response.body.id

      // Sélectionner un parent
      cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
      cy.get('[data-cy="search-husband"]').type('John')
      cy.wait('@searchPersons')
      cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
        cy.get('[data-cy="select-husband"]').select($opt.val())
      })

      // Ajouter l'enfant
      cy.get('[data-cy="search-child"]').type('ToRemove')
      cy.wait('@searchPersons')
      cy.get('[data-cy="select-child"]').find('option').eq(1).then(($opt) => {
        cy.get('[data-cy="select-child"]').select($opt.val())
      })

      // Vérifier que l'enfant est ajouté
      cy.get('[data-cy="children-list"]').should('contain', 'ToRemove Child')
      cy.contains('Enfants (1)').should('be.visible')

      // Supprimer l'enfant
      cy.get(`[data-cy="remove-child-${childId}"]`).click()

      // Vérifier que l'enfant est supprimé
      cy.get('[data-cy="children-list"]').should('not.exist')
      cy.contains('Enfants (0)').should('be.visible')

      // Nettoyer l'enfant créé
      cy.request('DELETE', `${apiUrl}/api/v1/persons/${childId}`, { failOnStatusCode: false })
    })
  })

  it('should create a new child via modal and add to family', () => {
    // Sélectionner un parent
    cy.intercept('GET', '**/api/v1/persons/search*').as('searchPersons')
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait('@searchPersons')
    cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
      cy.get('[data-cy="select-husband"]').select($opt.val())
    })

    // Ouvrir la modale pour créer un enfant
    cy.get('[data-cy="create-child-button"]').click()
    cy.get('.modal').should('be.visible')

    // Remplir le formulaire
    cy.get('[data-cy="new-person-first-name"]').type('NewChild')
    cy.get('[data-cy="new-person-last-name"]').type('Created')
    cy.get('[data-cy="new-person-birth-date"]').type('2015-03-10')

    // Soumettre
    cy.intercept('POST', '**/api/v1/persons').as('createPerson')
    cy.get('[data-cy="create-person-submit"]').click()
    cy.wait('@createPerson')

    // Vérifier que la modale se ferme et que l'enfant est ajouté
    cy.get('.modal').should('not.exist')
    cy.get('[data-cy="children-list"]').should('contain', 'NewChild Created')
    cy.contains('Enfants (1)').should('be.visible')

    // Créer la famille
    cy.intercept('POST', '**/api/v1/families').as('createFamily')
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily')

    // Vérifier le message de succès
    cy.get('.success').should('contain.text', 'Famille créée avec 1 enfant')
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

      // Sélectionner le mari
      cy.intercept('GET', '**/api/v1/persons/search*').as('searchHusband')
      cy.get('[data-cy="search-husband"]').type('EventTest')
      cy.wait('@searchHusband')
      cy.get('[data-cy="select-husband"]').find('option').then(($options) => {
        // Trouver l'option contenant "Father"
        const fatherOption = $options.filter((i, opt) => opt.text.includes('Father'))
        if (fatherOption.length > 0) {
          cy.get('[data-cy="select-husband"]').select(fatherOption.val())
        }
      })

      // Sélectionner la femme
      cy.intercept('GET', '**/api/v1/persons/search*').as('searchWife')
      cy.get('[data-cy="search-wife"]').type('EventTest')
      cy.wait('@searchWife')
      cy.get('[data-cy="select-wife"]').find('option').then(($options) => {
        // Trouver l'option contenant "Mother"
        const motherOption = $options.filter((i, opt) => opt.text.includes('Mother'))
        if (motherOption.length > 0) {
          cy.get('[data-cy="select-wife"]').select(motherOption.val())
        }
      })
    })

    // Ajouter un événement de mariage
    cy.get('[data-cy="add-event-button"]').click()
    cy.get('[data-cy="event-0"]').should('exist')
    cy.get('[data-cy="event-type-0"]').select('Marriage')
    cy.get('[data-cy="event-date-0"]').type('2000-06-15')
    cy.get('[data-cy="event-place-0"]').type('Paris, France')
    cy.get('[data-cy="event-description-0"]').type('Cérémonie à l\'église Saint-Sulpice')

    // Ajouter un deuxième événement
    cy.get('[data-cy="add-event-button"]').click()
    cy.get('[data-cy="event-1"]').should('exist')
    cy.get('[data-cy="event-type-1"]').select('Engagement')
    cy.get('[data-cy="event-date-1"]').type('1999-12-25')
    cy.get('[data-cy="event-place-1"]').type('Lyon, France')

    // Vérifier le compteur d'événements
    cy.contains('Événements (2)').should('be.visible')

    // Créer la famille
    cy.intercept('POST', '**/api/v1/families').as('createFamily')
    cy.intercept('POST', '**/api/v1/events').as('createEvent')
    cy.get('[data-cy="submit-family"]').click()
    cy.wait('@createFamily')
    cy.wait('@createEvent')

    // Vérifier le message de succès
    cy.get('.success').should('contain.text', 'Famille créée avec 2 événements')

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

      // Sélectionner un parent
      cy.intercept('GET', '**/api/v1/persons/search*').as('searchPerson')
      cy.get('[data-cy="search-husband"]').type('RemoveEvent')
      cy.wait('@searchPerson')
      cy.get('[data-cy="select-husband"]').find('option').eq(1).then(($opt) => {
        cy.get('[data-cy="select-husband"]').select($opt.val())
      })
    })

    // Ajouter deux événements
    cy.get('[data-cy="add-event-button"]').click()
    cy.get('[data-cy="add-event-button"]').click()
    cy.contains('Événements (2)').should('be.visible')

    // Supprimer le premier événement
    cy.get('[data-cy="remove-event-0"]').click()
    cy.contains('Événements (1)').should('be.visible')
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
    cy.get('[data-cy="add-event-button"]').click()

    // Vérifier que tous les types d'événements sont disponibles
    const expectedEventTypes = [
      'Mariage',
      'Couple',
      'Fiançailles',
      'Divorce',
      'Séparation',
      'Ménage commun',
      'Annulation mariage'
    ]

    cy.get('[data-cy="event-type-0"]').then(($select) => {
      expectedEventTypes.forEach((eventType) => {
        cy.wrap($select).should('contain', eventType)
      })
    })
  })
})

