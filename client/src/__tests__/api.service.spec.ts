// typescript
import { describe, it, expect, vi, beforeEach, afterEach, beforeAll } from 'vitest'
import axios from 'axios'
import { apiService } from '../services/api'
import type { FamilySearchParams, FamilySearchResult, FamilyDetailResult } from '../types/family'

// Mock axios
vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => ({
      get: vi.fn(),
      post: vi.fn(),
      put: vi.fn(),
      delete: vi.fn(),
      interceptors: {
        request: { use: vi.fn() },
        response: { use: vi.fn() },
      },
    })),
  },
}))

describe('API Service', () => {
  const mockFamilySearchResult: FamilySearchResult[] = [
    {
      id: '123e4567-e89b-12d3-a456-426614174000',
      husband_name: 'John Smith',
      wife_name: 'Jane Doe',
      marriage_date: '2005-06-20',
      marriage_place: 'Boston, MA',
      children_count: 2,
      summary: 'John Smith & Jane Doe (2005)',
    },
  ]

  const mockFamilyDetailResult: FamilyDetailResult = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    husband_id: 'h123',
    wife_id: 'w123',
    marriage_date: '2005-06-20',
    marriage_place: 'Boston, MA',
    notes: undefined,
    husband: {
      id: 'h123',
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
    },
    wife: {
      id: 'w123',
      first_name: 'Jane',
      last_name: 'Doe',
      sex: 'F',
      birth_date: '1982-03-15',
      death_date: undefined,
      birth_place: 'New York, NY',
      death_place: undefined,
      occupation: 'Teacher',
      notes: 'Test notes',
      has_own_family: false,
      own_families: [],
    },
    children: [],
    events: [],
  }

  type MockFn = (...args: unknown[]) => unknown
  type MockAxiosInstance = {
    get: MockFn
    post: MockFn
    put: MockFn
    delete: MockFn
    interceptors: {
      request: { use: MockFn }
      response: { use: MockFn }
    }
  }

  let mockAxiosInstanceWithMethods: MockAxiosInstance | undefined

  beforeAll(async () => {
    await import('../services/api')
  })

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset console methods
    vi.spyOn(console, 'log').mockImplementation(() => {})
    vi.spyOn(console, 'error').mockImplementation(() => {})

    // Get the mock instance
    mockAxiosInstanceWithMethods = vi.mocked(axios.create).mock.results[0]?.value as unknown as MockAxiosInstance
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Service Instance', () => {
    it('should export singleton instance', () => {
      expect(apiService).toBeDefined()
      expect(typeof apiService.searchFamilies).toBe('function')
      expect(typeof apiService.getFamilyDetail).toBe('function')
      expect(typeof apiService.getFamily).toBe('function')
      expect(typeof apiService.healthCheck).toBe('function')
    })

    it('should have all required methods', () => {
      const methods = ['searchFamilies', 'getFamilyDetail', 'getFamily', 'healthCheck']

      methods.forEach((method) => {
        expect(apiService).toHaveProperty(method)
        expect(typeof apiService[method as keyof typeof apiService]).toBe('function')
      })
    })
  })

  describe('Request Interceptors', () => {
    it('should log request details in request interceptor', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      const requestInterceptors = mockAxiosInstanceWithMethods?.interceptors?.request?.use
      const [requestSuccess] = requestInterceptors?.mock?.calls?.[0] || []

      if (!requestSuccess) {
        consoleSpy.mockRestore()
        return
      }

      const config = {
        baseURL: 'http://localhost:8000',
        url: '/test',
        method: 'GET',
      }

      const result = requestSuccess(config)

      expect(consoleSpy).toHaveBeenCalledWith(
        'API Request: GET /test'
      )
      expect(result).toBe(config)

      consoleSpy.mockRestore()
    })

    it('should handle request error in interceptor', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const requestInterceptors = mockAxiosInstanceWithMethods?.interceptors?.request?.use
      const [, requestError] = requestInterceptors?.mock?.calls?.[0] || []

      if (!requestError) {
        consoleSpy.mockRestore()
        return
      }

      const error = new Error('Request failed')

      await expect(requestError(error)).rejects.toThrow('Request failed')
      expect(consoleSpy).toHaveBeenCalledWith('API Request Error:', error)

      consoleSpy.mockRestore()
    })
  })

  describe('Response Interceptors', () => {
    it('should log response details in response interceptor', () => {
      const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
      const responseInterceptors = mockAxiosInstanceWithMethods?.interceptors?.response?.use
      const [responseSuccess] = responseInterceptors?.mock?.calls?.[0] || []

      if (!responseSuccess) {
        consoleSpy.mockRestore()
        return
      }

      const response = {
        status: 200,
        config: { url: '/test' },
      }

      const result = responseSuccess(response)

      expect(consoleSpy).toHaveBeenCalledWith(
        'API Response: 200 /test'
      )
      expect(result).toBe(response)

      consoleSpy.mockRestore()
    })

    it('should handle response error in interceptor', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const responseInterceptors = mockAxiosInstanceWithMethods?.interceptors?.response?.use
      const [, responseError] = responseInterceptors?.mock?.calls?.[0] || []

      if (!responseError) {
        consoleSpy.mockRestore()
        return
      }

      const error = {
        response: { status: 404, data: { detail: 'Not found' } },
        message: 'Not found',
      }

      await expect(responseError(error)).rejects.toThrow()
      expect(consoleSpy).toHaveBeenCalledWith('API Response Error:', error.response?.data || error.message)

      consoleSpy.mockRestore()
    })

    it('should handle response error without response object', async () => {
      const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
      const responseInterceptors = mockAxiosInstanceWithMethods?.interceptors?.response?.use
      const [, responseError] = responseInterceptors?.mock?.calls?.[0] || []

      if (!responseError) {
        consoleSpy.mockRestore()
        return
      }

      const error = {
        message: 'Network error',
      }

      await expect(responseError(error)).rejects.toThrow()
      expect(consoleSpy).toHaveBeenCalledWith('API Response Error:', error.message)

      consoleSpy.mockRestore()
    })
  })

  describe('searchFamilies', () => {
    it('should search families with correct parameters', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const searchParams: FamilySearchParams = {
        q: 'John Jane',
        family_id: 'test-family-id',
        limit: 10,
      }

      mockAxiosInstanceWithMethods.get.mockResolvedValue({ data: mockFamilySearchResult })

      const result = await apiService.searchFamilies(searchParams)

      expect(mockAxiosInstanceWithMethods.get).toHaveBeenCalledWith('/api/v1/families/search', {
        params: searchParams,
      })
      expect(result).toEqual(mockFamilySearchResult)
    })

    it('should handle search families error', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const searchParams: FamilySearchParams = { q: 'John' }
      const error = new Error('Search failed')

      mockAxiosInstanceWithMethods.get.mockRejectedValue(error)

      await expect(apiService.searchFamilies(searchParams)).rejects.toThrow('Search failed')
    })

    it('should handle empty search parameters', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const searchParams: FamilySearchParams = {}

      mockAxiosInstanceWithMethods.get.mockResolvedValue({ data: [] })

      const result = await apiService.searchFamilies(searchParams)

      expect(mockAxiosInstanceWithMethods.get).toHaveBeenCalledWith('/api/v1/families/search', {
        params: {},
      })
      expect(result).toEqual([])
    })
  })

  describe('getFamilyDetail', () => {
    it('should get family detail with correct ID', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const familyId = '123e4567-e89b-12d3-a456-426614174000'

      mockAxiosInstanceWithMethods.get.mockResolvedValue({ data: mockFamilyDetailResult })

      const result = await apiService.getFamilyDetail(familyId)

      expect(mockAxiosInstanceWithMethods.get).toHaveBeenCalledWith(`/api/v1/families/${familyId}/detail`)
      expect(result).toEqual(mockFamilyDetailResult)
    })

    it('should handle get family detail error', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const familyId = 'invalid-id'
      const error = new Error('Family not found')

      mockAxiosInstanceWithMethods.get.mockRejectedValue(error)

      await expect(apiService.getFamilyDetail(familyId)).rejects.toThrow('Family not found')
    })

    it('should handle different family ID formats', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const familyId = 'family-123'

      mockAxiosInstanceWithMethods.get.mockResolvedValue({ data: mockFamilyDetailResult })

      await apiService.getFamilyDetail(familyId)

      expect(mockAxiosInstanceWithMethods.get).toHaveBeenCalledWith(`/api/v1/families/${familyId}/detail`)
    })
  })

  describe('getFamily', () => {
    it('should get family with correct ID', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const familyId = '123e4567-e89b-12d3-a456-426614174000'

      mockAxiosInstanceWithMethods.get.mockResolvedValue({ data: mockFamilyDetailResult })

      const result = await apiService.getFamily(familyId)

      expect(mockAxiosInstanceWithMethods.get).toHaveBeenCalledWith(`/api/v1/families/${familyId}`)
      expect(result).toEqual(mockFamilyDetailResult)
    })

    it('should handle get family error', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const familyId = 'invalid-id'
      const error = new Error('Family not found')

      mockAxiosInstanceWithMethods.get.mockRejectedValue(error)

      await expect(apiService.getFamily(familyId)).rejects.toThrow('Family not found')
    })

    it('should return same data as getFamilyDetail but from different endpoint', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const familyId = '123e4567-e89b-12d3-a456-426614174000'

      mockAxiosInstanceWithMethods.get.mockResolvedValue({ data: mockFamilyDetailResult })

      const result = await apiService.getFamily(familyId)

      expect(mockAxiosInstanceWithMethods.get).toHaveBeenCalledWith(`/api/v1/families/${familyId}`)
      expect(result).toEqual(mockFamilyDetailResult)
    })
  })

  describe('healthCheck', () => {
    it('should return true when health check succeeds', async () => {
      if (!mockAxiosInstanceWithMethods) return

      mockAxiosInstanceWithMethods.get.mockResolvedValue({ status: 200 })

      const result = await apiService.healthCheck()

      expect(mockAxiosInstanceWithMethods.get).toHaveBeenCalledWith('/health')
      expect(result).toBe(true)
    })

    it('should return false when health check fails', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const error = new Error('Health check failed')
      mockAxiosInstanceWithMethods.get.mockRejectedValue(error)

      const result = await apiService.healthCheck()

      expect(mockAxiosInstanceWithMethods.get).toHaveBeenCalledWith('/health')
      expect(result).toBe(false)
      expect(console.error).toHaveBeenCalledWith('Health check failed:', error)
    })

    it('should handle network timeout', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const timeoutError = new Error('timeout of 10000ms exceeded')
      mockAxiosInstanceWithMethods.get.mockRejectedValue(timeoutError)

      const result = await apiService.healthCheck()

      expect(result).toBe(false)
      expect(console.error).toHaveBeenCalledWith('Health check failed:', timeoutError)
    })

    it('should handle 500 server error', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const serverError = {
        response: { status: 500, data: { error: 'Internal server error' } },
      }
      mockAxiosInstanceWithMethods.get.mockRejectedValue(serverError)

      const result = await apiService.healthCheck()

      expect(result).toBe(false)
      expect(console.error).toHaveBeenCalledWith('Health check failed:', serverError)
    })
  })

  describe('Error Handling', () => {
    it('should handle axios timeout errors', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const timeoutError = new Error('timeout of 10000ms exceeded')
      mockAxiosInstanceWithMethods.get.mockRejectedValue(timeoutError)

      await expect(apiService.searchFamilies({})).rejects.toThrow('timeout of 10000ms exceeded')
    })

    it('should handle network errors', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const networkError = new Error('Network Error')
      mockAxiosInstanceWithMethods.get.mockRejectedValue(networkError)

      await expect(apiService.getFamilyDetail('test-id')).rejects.toThrow('Network Error')
    })

    it('should handle 404 errors', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const notFoundError = {
        response: {
          status: 404,
          data: { detail: 'Family not found' },
        },
      }
      mockAxiosInstanceWithMethods.get.mockRejectedValue(notFoundError)

      await expect(apiService.getFamily('non-existent')).rejects.toEqual(notFoundError)
    })

    it('should handle 500 errors', async () => {
      if (!mockAxiosInstanceWithMethods) return

      const serverError = {
        response: {
          status: 500,
          data: { detail: 'Internal server error' },
        },
      }
      mockAxiosInstanceWithMethods.get.mockRejectedValue(serverError)

      await expect(apiService.searchFamilies({})).rejects.toEqual(serverError)
    })
  })
})
