import api from './api'
import type { CreatePerson } from '@/types/person.ts'

export const personService = {
  createPerson(data: CreatePerson) {
    return api.post('/api/v1/persons', data)
  },

  getAllPersons(params?: { page?: number; limit?: number }) {
    return api.get('/api/v1/persons', { params })
  },

  searchPersonsByName(name: string, params?: { page?: number; limit?: number }) {
    return api.get('/api/v1/persons/search', { params: { name, ...params } })
  },

  getPersonsByExactName(name: string) {
    return api.get('/api/v1/persons/by-name', { params: { name } })
  },

  getPersonById(id: string) {
    return api.get(`/api/v1/persons/${id}`)
  },

  updatePerson(id: string, data: CreatePerson) {
    return api.put(`/api/v1/persons/${id}`, data)
  },

  patchPerson(id: string, data: Partial<CreatePerson>) {
    return api.patch(`/api/v1/persons/${id}`, data)
  },

  deletePerson(id: string) {
    return api.delete(`/api/v1/persons/${id}`)
  },
}
