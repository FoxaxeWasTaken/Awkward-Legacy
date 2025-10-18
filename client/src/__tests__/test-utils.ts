import { createRouter, createMemoryHistory } from 'vue-router'
import type { FamilySearchResult, FamilyDetailResult, Person } from '../types/family'

/**
 * Create a mock router for testing
 */
export function createMockRouter() {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
      {
        path: '/family/:id',
        name: 'family-tree',
        component: { template: '<div>Family Tree</div>' },
      },
    ],
  })
}

/**
 * Create a mock family search result
 */
export function createMockFamilyResult(
  overrides?: Partial<FamilySearchResult>,
): FamilySearchResult {
  return {
    id: '123e4567-e89b-12d3-a456-426614174000',
    husband_name: 'John Smith',
    wife_name: 'Jane Doe',
    marriage_date: '2005-06-20',
    marriage_place: 'Boston, MA',
    children_count: 2,
    summary: 'John Smith & Jane Doe (2005)',
    ...overrides,
  }
}

/**
 * Create a mock person
 */
export function createMockPerson(overrides?: Partial<Person>): Person {
  return {
    id: 'p123',
    first_name: 'John',
    last_name: 'Smith',
    sex: 'M',
    birth_date: '1980-01-01',
    death_date: undefined,
    birth_place: 'Boston, MA',
    death_place: undefined,
    occupation: 'Engineer',
    notes: 'Test notes',
    has_own_family: false,
    own_families: [],
    ...overrides,
  }
}

/**
 * Create a mock family detail result
 */
export function createMockFamilyDetail(
  overrides?: Partial<FamilyDetailResult>,
): FamilyDetailResult {
  return {
    id: '123',
    husband_id: 'h123',
    wife_id: 'w123',
    marriage_date: '2005-06-20',
    marriage_place: 'Boston, MA',
    notes: undefined,
    husband: createMockPerson({
      id: 'h123',
      first_name: 'John',
      last_name: 'Smith',
      sex: 'M',
    }),
    wife: createMockPerson({
      id: 'w123',
      first_name: 'Jane',
      last_name: 'Doe',
      sex: 'F',
    }),
    children: [],
    events: [],
    ...overrides,
  }
}

/**
 * Wait for all promises to resolve
 */
export async function waitForPromises() {
  return new Promise((resolve) => setTimeout(resolve, 0))
}

/**
 * Create mock search results with multiple families
 */
export function createMockSearchResults(count: number): FamilySearchResult[] {
  return Array.from({ length: count }, (_, index) =>
    createMockFamilyResult({
      id: `family-${index}`,
      husband_name: `Husband ${index}`,
      wife_name: `Wife ${index}`,
      summary: `Husband ${index} & Wife ${index} (2005)`,
    }),
  )
}

/**
 * Mock API error response
 */
export function createMockApiError(message: string, statusCode: number = 500) {
  return {
    response: {
      status: statusCode,
      data: {
        detail: message,
      },
    },
  }
}

/**
 * Sleep helper for async tests
 */
export function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms))
}
