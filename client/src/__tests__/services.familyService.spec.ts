import api from '../services/api'
import { familyService } from '../services/familyService'
import { vi, beforeEach, expect, describe, it } from 'vitest'

vi.mock('../services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
    put: vi.fn(),
    patch: vi.fn(),
    delete: vi.fn(),
  }
}))

describe('Family Service', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('creates a family', async () => {
    const payload = { husband_id: 'h1', wife_id: 'w1', marriage_date: '2005-06-20' }
    const response = { data: { id: 'f1', ...payload } }
    vi.mocked(api.post).mockResolvedValue(response)

    const result = await familyService.createFamily(payload)
    expect(api.post).toHaveBeenCalledWith('/api/v1/families', payload)
    expect(result).toEqual(response)
  })

  it('rejects on duplicate couple with 409', async () => {
    const payload = { husband_id: 'h1', wife_id: 'w1' }
    const error = { response: { status: 409, data: { detail: 'dup' } } }
    vi.mocked(api.post).mockRejectedValue(error)

    await expect(familyService.createFamily(payload)).rejects.toEqual(error)
  })
})


