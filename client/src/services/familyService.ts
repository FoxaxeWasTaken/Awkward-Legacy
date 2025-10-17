import api from './api'

export interface CreateFamily {
  husband_id?: string
  wife_id?: string
  marriage_date?: string
  marriage_place?: string
  notes?: string
}

export const familyService = {
  createFamily(data: CreateFamily) {
    return api.post('/api/v1/families', data)
  },

  getAllFamilies(params?: { skip?: number; limit?: number }) {
    return api.get('/api/v1/families', { params })
  },

  getFamilyById(id: string) {
    return api.get(`/api/v1/families/${id}`)
  },

  getFamiliesByHusband(husbandId: string) {
    return api.get(`/api/v1/families/by-husband/${husbandId}`)
  },

  getFamiliesByWife(wifeId: string) {
    return api.get(`/api/v1/families/by-wife/${wifeId}`)
  },

  getFamiliesBySpouse(spouseId: string) {
    return api.get(`/api/v1/families/by-spouse/${spouseId}`)
  },

  updateFamily(id: string, data: Partial<CreateFamily>) {
    return api.patch(`/api/v1/families/${id}`, data)
  },

  deleteFamily(id: string) {
    return api.delete(`/api/v1/families/${id}`)
  },
}


