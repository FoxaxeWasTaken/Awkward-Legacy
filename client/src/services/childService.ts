import api from './api'

export interface CreateChild {
  family_id: string
  child_id: string
}

export const childService = {
  createChild(data: CreateChild) {
    return api.post('/api/v1/children', data)
  },

  getChildren(params?: { skip?: number; limit?: number }) {
    return api.get('/api/v1/children', { params })
  },

  getChildrenByFamily(familyId: string) {
    return api.get(`/api/v1/children/by-family/${familyId}`)
  },

  getFamiliesByChild(childId: string) {
    return api.get(`/api/v1/children/by-child/${childId}`)
  },

  getChildRelation(familyId: string, childId: string) {
    return api.get(`/api/v1/children/${familyId}/${childId}`)
  },

  deleteChildrenByFamily(familyId: string) {
    return api.delete(`/api/v1/children/by-family/${familyId}`)
  },

  deleteFamiliesByChild(childId: string) {
    return api.delete(`/api/v1/children/by-child/${childId}`)
  },

  deleteChildRelation(familyId: string, childId: string) {
    return api.delete(`/api/v1/children/${familyId}/${childId}`)
  },
}


