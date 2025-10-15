import { describe, it, expect, vi, beforeAll } from 'vitest'
import type { AxiosInstance } from 'axios'

const mockInterceptors = {
  request: { use: vi.fn() },
  response: { use: vi.fn() },
}

const mockAxiosInstance: Partial<AxiosInstance> = {
  interceptors: mockInterceptors as any,
}

vi.mock('axios', () => ({
  default: {
    create: vi.fn(() => mockAxiosInstance),
  },
}))

describe('API Service', () => {
  beforeAll(async () => {
    await import('../services/api')
  })

  it('should create axios instance with default config', async () => {
    const axios = await import('axios')

    expect(axios.default.create).toHaveBeenCalledWith({
      baseURL: 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  })

  it('should register request interceptor', () => {
    expect(mockInterceptors.request.use).toHaveBeenCalledWith(
      expect.any(Function),
      expect.any(Function)
    )
  })

  it('should register response interceptor', () => {
    expect(mockInterceptors.response.use).toHaveBeenCalledWith(
      expect.any(Function),
      expect.any(Function)
    )
  })

  it('should log request details in request interceptor', () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    const [requestSuccess] = mockInterceptors.request.use.mock.calls[0]

    const config = {
      baseURL: 'http://localhost:8000',
      url: '/test',
    }

    const result = requestSuccess(config)

    expect(consoleSpy).toHaveBeenCalledWith(
      'Making request to:',
      'http://localhost:8000/test'
    )
    expect(result).toBe(config)

    consoleSpy.mockRestore()
  })

  it('should handle request error in interceptor', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const [, requestError] = mockInterceptors.request.use.mock.calls[0]

    const error = new Error('Request failed')

    await expect(requestError(error)).rejects.toThrow('Request failed')
    expect(consoleSpy).toHaveBeenCalledWith('Request error:', error)

    consoleSpy.mockRestore()
  })

  it('should log response details in response interceptor', () => {
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    const [responseSuccess] = mockInterceptors.response.use.mock.calls[0]

    const response = {
      status: 200,
      config: { url: '/test' },
    }

    const result = responseSuccess(response)

    expect(consoleSpy).toHaveBeenCalledWith(
      'Response received:',
      200,
      '/test'
    )
    expect(result).toBe(response)

    consoleSpy.mockRestore()
  })

  it('should handle response error in interceptor', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const [, responseError] = mockInterceptors.response.use.mock.calls[0]

    const error = {
      response: { status: 404 },
      message: 'Not found',
    }

    await expect(responseError(error)).rejects.toEqual(error)
    expect(consoleSpy).toHaveBeenCalledWith('Response error:', 404, 'Not found')

    consoleSpy.mockRestore()
  })

  it('should handle response error without response object', async () => {
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    const [, responseError] = mockInterceptors.response.use.mock.calls[0]

    const error = {
      message: 'Network error',
    }

    await expect(responseError(error)).rejects.toEqual(error)
    expect(consoleSpy).toHaveBeenCalledWith('Response error:', undefined, 'Network error')

    consoleSpy.mockRestore()
  })
})
