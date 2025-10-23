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

  it('should create a person with all fields', async () => {
    const personData = {
      first_name: 'John',
      last_name: 'Doe',
      sex: 'M',
      birth_date: '1980-01-01',
      birth_place: 'New York',
      death_date: null,
      death_place: null,
      notes: 'Sample person',
      occupation: 'Engineer'
    }

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
    const personData = {
      first_name: 'Jane',
      last_name: 'Smith',
      sex: 'F'
    }

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

  it('should handle validation errors', async () => {
    const personData = {
      first_name: '',
      last_name: 'Doe',
      sex: 'M'
    }

    const errorResponse = {
      response: {
        status: 422,
        data: {
          detail: 'first_name cannot be empty'
        }
      }
    }

    vi.mocked(api.post).mockRejectedValue(errorResponse)

    await expect(personService.createPerson(personData)).rejects.toEqual(errorResponse)
    expect(api.post).toHaveBeenCalledWith('/api/v1/persons', personData)
  })

  it('should handle invalid sex value', async () => {
    const personData = {
      first_name: 'John',
      last_name: 'Doe',
      sex: 'X'
    }

    const errorResponse = {
      response: {
        status: 422,
        data: {
          detail: 'sex must be M, F, or U'
        }
      }
    }

    vi.mocked(api.post).mockRejectedValue(errorResponse)

    await expect(personService.createPerson(personData)).rejects.toEqual(errorResponse)
  })

  it('should handle future birth date error', async () => {
    const personData = {
      first_name: 'John',
      last_name: 'Doe',
      sex: 'M',
      birth_date: '2099-01-01'
    }

    const errorResponse = {
      response: {
        status: 422,
        data: {
          detail: 'birth_date cannot be in the future'
        }
      }
    }

    vi.mocked(api.post).mockRejectedValue(errorResponse)

    await expect(personService.createPerson(personData)).rejects.toEqual(errorResponse)
  })

  it('should handle death date before birth date error', async () => {
    const personData = {
      first_name: 'John',
      last_name: 'Doe',
      sex: 'M',
      birth_date: '1980-01-01',
      death_date: '1979-01-01'
    }

    const errorResponse = {
      response: {
        status: 422,
        data: {
          detail: 'death_date cannot be before birth_date'
        }
      }
    }

    vi.mocked(api.post).mockRejectedValue(errorResponse)

    await expect(personService.createPerson(personData)).rejects.toEqual(errorResponse)
  })

  it('should handle network errors', async () => {
    const personData = {
      first_name: 'John',
      last_name: 'Doe',
      sex: 'M'
    }

    const networkError = {
      message: 'Network Error',
      code: 'ERR_NETWORK'
    }

    vi.mocked(api.post).mockRejectedValue(networkError)

    await expect(personService.createPerson(personData)).rejects.toEqual(networkError)
  })

  it('should handle server errors', async () => {
    const personData = {
      first_name: 'John',
      last_name: 'Doe',
      sex: 'M'
    }

    const serverError = {
      response: {
        status: 500,
        data: {
          detail: 'Internal server error'
        }
      }
    }

    vi.mocked(api.post).mockRejectedValue(serverError)

    await expect(personService.createPerson(personData)).rejects.toEqual(serverError)
  })
})
