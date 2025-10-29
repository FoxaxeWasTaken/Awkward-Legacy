/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************

/**
 * Nettoie complètement la base de données en supprimant toutes les données
 * dans le bon ordre pour respecter les contraintes de clés étrangères.
 * 
 * Ordre de suppression :
 * 1. Children (relations enfants-familles)
 * 2. Events (événements liés aux personnes et familles)
 * 3. Families (familles)
 * 4. Persons (personnes)
 */
Cypress.Commands.add('cleanDatabase', () => {
  const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'

  // 1. Supprimer toutes les relations enfants
  cy.request('GET', `${apiUrl}/api/v1/children?limit=1000`).then((response) => {
    const children = response.body
    children.forEach((child: any) => {
      cy.request({
        method: 'DELETE',
        url: `${apiUrl}/api/v1/children/${child.family_id}/${child.child_id}`,
        failOnStatusCode: false
      })
    })
  })

  // 2. Delete all events
  cy.request('GET', `${apiUrl}/api/v1/events?limit=1000`).then((response) => {
    const events = response.body
    events.forEach((event: any) => {
      cy.request({
        method: 'DELETE',
        url: `${apiUrl}/api/v1/events/${event.id}`,
        failOnStatusCode: false
      })
    })
  })

  // 3. Supprimer toutes les familles
  cy.request('GET', `${apiUrl}/api/v1/families?limit=1000`).then((response) => {
    const families = response.body
    families.forEach((family: any) => {
      cy.request({
        method: 'DELETE',
        url: `${apiUrl}/api/v1/families/${family.id}`,
        failOnStatusCode: false
      })
    })
  })

  // 4. Supprimer toutes les personnes
  cy.request('GET', `${apiUrl}/api/v1/persons?limit=1000`).then((response) => {
    const persons = response.body
    persons.forEach((person: any) => {
      cy.request({
        method: 'DELETE',
        url: `${apiUrl}/api/v1/persons/${person.id}`,
        failOnStatusCode: false
      })
    })
  })
})

/**
 * Crée une personne de test et retourne son ID
 */
Cypress.Commands.add('createTestPerson', (personData: {
  first_name: string
  last_name: string
  sex?: 'M' | 'F' | 'U'
  birth_date?: string
  birth_place?: string
  death_date?: string
  death_place?: string
  notes?: string
}) => {
  const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
  
  return cy.request('POST', `${apiUrl}/api/v1/persons`, {
    sex: 'U',
    ...personData
  }).then((response) => {
    return response.body.id
  })
})

/**
 * Crée une famille de test et retourne son ID
 */
Cypress.Commands.add('createTestFamily', (familyData: {
  husband_id?: string
  wife_id?: string
  marriage_date?: string
  marriage_place?: string
  notes?: string
}) => {
  const apiUrl = Cypress.env('apiUrl') || 'http://server-dev:8000'
  
  return cy.request('POST', `${apiUrl}/api/v1/families`, familyData).then((response) => {
    return response.body.id
  })
})

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Nettoie complètement la base de données (children, events, families, persons)
       */
      cleanDatabase(): Chainable<void>
      
      /**
       * Crée une personne de test et retourne son ID
       */
      createTestPerson(personData: {
        first_name: string
        last_name: string
        sex?: 'M' | 'F' | 'U'
        birth_date?: string
        birth_place?: string
        death_date?: string
        death_place?: string
        notes?: string
      }): Chainable<string>
      
      /**
       * Crée une famille de test et retourne son ID
       */
      createTestFamily(familyData: {
        husband_id?: string
        wife_id?: string
        marriage_date?: string
        marriage_place?: string
        notes?: string
      }): Chainable<string>
    }
  }
}