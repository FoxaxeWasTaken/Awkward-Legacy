import { describe, it, expect, vi, beforeEach } from 'vitest'
import { personService } from '../services/personService'
import api from '../services/api'

vi.mock('../services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  }
}))

describe('Person Service - createPerson', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Helper function to test error scenarios
  type CreatePersonParam = Parameters<typeof personService.createPerson>[0]

  const testErrorScenario = async (
    personData: CreatePersonParam,
    errorResponse: unknown,
    _description: string
  ) => {
    vi.mocked(api.post).mockRejectedValue(errorResponse)
    await expect(personService.createPerson(personData)).rejects.toEqual(errorResponse)
  }

  it('should create a person with all fields', async () => {
    const personData: CreatePersonParam = {
      first_name: 'John',
      last_name: 'Doe',
      sex: 'M',
      birth_date: '1980-01-01',
      birth_place: 'New York',
      death_date: null,
      death_place: null,
      notes: 'Sample person',
      occupation: 'Engineer'
    } as CreatePersonParam

    const expectedResponse = {
      data: {
        id: '123e4567-e89b-12d3-a456-426614174000',
        ...personData
      }
    }

    vi.mocked(api.post).mockResolvedValue(expectedResponse)

    const result = await personService.createPerson(personData)

    expect(api.post).toHaveBeenCalledWith('/api/v1/persons', personData)
    expect(result).toEqual(expectedResponse)
  })

  it('should create a person with only required fields', async () => {
    const personData: CreatePersonParam = {
      first_name: 'Jane',
      last_name: 'Smith',
      sex: 'F'
    } as CreatePersonParam

    const expectedResponse = {
      data: {
        id: '123e4567-e89b-12d3-a456-426614174001',
        ...personData,
        birth_date: null,
        birth_place: null,
        death_date: null,
        death_place: null,
        notes: null,
        occupation: null
      }
    }

    vi.mocked(api.post).mockResolvedValue(expectedResponse)

    const result = await personService.createPerson(personData)

    expect(api.post).toHaveBeenCalledWith('/api/v1/persons', personData)
    expect(result).toEqual(expectedResponse)
  })

  // Test cases for error scenarios
  const errorTestCases = [
    {
      name: 'validation errors',
      personData: {
        first_name: '',
        last_name: 'Doe',
        sex: 'M'
      } as CreatePersonParam,
      errorResponse: {
        response: {
          status: 422,
          data: {
            detail: 'first_name cannot be empty'
          }
        }
      }
    },
    {
      name: 'invalid sex value',
      personData: {
        first_name: 'John',
        last_name: 'Doe',
        sex: 'X'
      } as CreatePersonParam,
      errorResponse: {
        response: {
          status: 422,
          data: {
            detail: 'sex must be M, F, or U'
          }
        }
      }
    },
    {
      name: 'future birth date error',
      personData: {
        first_name: 'John',
        last_name: 'Doe',
        sex: 'M',
        birth_date: '2099-01-01'
      } as CreatePersonParam,
      errorResponse: {
        response: {
          status: 422,
          data: {
            detail: 'birth_date cannot be in the future'
          }
        }
      }
    },
    {
      name: 'death date before birth date error',
      personData: {
        first_name: 'John',
        last_name: 'Doe',
        sex: 'M',
        birth_date: '1980-01-01',
        death_date: '1979-01-01'
      } as CreatePersonParam,
      errorResponse: {
        response: {
          status: 422,
          data: {
            detail: 'death_date cannot be before birth_date'
          }
        }
      }
    },
    {
      name: 'network errors',
      personData: {
        first_name: 'John',
        last_name: 'Doe',
        sex: 'M'
      } as CreatePersonParam,
      errorResponse: {
        message: 'Network Error',
        code: 'ERR_NETWORK'
      }
    },
    {
      name: 'server errors',
      personData: {
        first_name: 'John',
        last_name: 'Doe',
        sex: 'M'
      } as CreatePersonParam,
      errorResponse: {
        response: {
          status: 500,
          data: {
            detail: 'Internal server error'
          }
        }
      }
    }
  ]

  // Parameterized tests for error scenarios
  describe.each(errorTestCases)('should handle $name', ({ name, personData, errorResponse }) => {
    it(`should handle ${name}`, async () => {
      expect.hasAssertions()
      await testErrorScenario(personData, errorResponse, name)
    })
  })
})
