describe('Create Family', () => {
  beforeEach(() => {
    // Visiter la page de création de famille
    cy.visit('/families/create')
  })

  it('should create a family with one parent', () => {
    // Rechercher et sélectionner un parent
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait(500) // Attendre le debounce
    
    // Sélectionner le premier résultat
    cy.get('[data-cy="select-husband"]').select(1)
    
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
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait(500)
    cy.get('[data-cy="select-husband"]').select(1)
    
    // Sélectionner le deuxième parent
    cy.get('[data-cy="search-wife"]').type('Jane')
    cy.wait(500)
    cy.get('[data-cy="select-wife"]').select(1)
    
    // Remplir les informations
    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    cy.get('[data-cy="marriage-place"]').type('Paris')
    
    // Soumettre
    cy.get('[data-cy="submit-family"]').click()
    
    // Vérifier le succès
    cy.contains('Famille créée.').should('be.visible')
  })

  it('should validate marriage date against parent birth dates', () => {
    // Sélectionner un parent avec une date de naissance connue
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait(500)
    cy.get('[data-cy="select-husband"]').select(1)
    
    // Essayer une date de mariage avant la naissance
    cy.get('[data-cy="marriage-date"]').type('1970-01-01')
    
    // Vérifier l'erreur de validation
    cy.contains('La date de mariage ne peut pas être avant la naissance').should('be.visible')
  })

  it('should prevent future marriage dates', () => {
    // Sélectionner un parent
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait(500)
    cy.get('[data-cy="select-husband"]').select(1)
    
    // Essayer une date future
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const tomorrowStr = tomorrow.toISOString().split('T')[0]
    
    cy.get('[data-cy="marriage-date"]').type(tomorrowStr)
    
    // Vérifier l'erreur
    cy.contains('La date de mariage ne peut pas être dans le futur').should('be.visible')
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
    // Créer une première famille
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait(500)
    cy.get('[data-cy="select-husband"]').select(1)
    
    cy.get('[data-cy="search-wife"]').type('Jane')
    cy.wait(500)
    cy.get('[data-cy="select-wife"]').select(1)
    
    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    cy.get('[data-cy="submit-family"]').click()
    cy.contains('Famille créée.').should('be.visible')
    
    // Essayer de créer la même famille à nouveau
    cy.get('[data-cy="search-husband"]').clear().type('John')
    cy.wait(500)
    cy.get('[data-cy="select-husband"]').select(1)
    
    cy.get('[data-cy="search-wife"]').clear().type('Jane')
    cy.wait(500)
    cy.get('[data-cy="select-wife"]').select(1)
    
    cy.get('[data-cy="marriage-date"]').type('2005-06-20')
    cy.get('[data-cy="submit-family"]').click()
    
    // Vérifier l'erreur de doublon
    cy.contains('Family with same spouses already exists').should('be.visible')
  })

  it('should reset form after successful creation', () => {
    // Créer une famille
    cy.get('[data-cy="search-husband"]').type('John')
    cy.wait(500)
    cy.get('[data-cy="select-husband"]').select(1)
    
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

  it('should show parent creation and linking buttons', () => {
    // Vérifier que les boutons existent
    cy.contains('Créer').should('be.visible')
    cy.contains('Lier').should('be.visible')
    
    // Vérifier qu'il y a des boutons pour chaque parent
    cy.get('[data-cy="search-husband"]').parent().contains('Créer').should('be.visible')
    cy.get('[data-cy="search-husband"]').parent().contains('Lier').should('be.visible')
    cy.get('[data-cy="search-wife"]').parent().contains('Créer').should('be.visible')
    cy.get('[data-cy="search-wife"]').parent().contains('Lier').should('be.visible')
  })
})
