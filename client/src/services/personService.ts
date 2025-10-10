import api from './api'

export const personService = {
  createPerson(data: any) {
    return api.post('/persons', data)
  },

  getAllPersons(params?: { page?: number; limit?: number }) {
    return api.get('/persons', { params })
  },

  searchPersonsByName(name: string, params?: { page?: number; limit?: number }) {
    return api.get('/persons/search', { params: { name, ...params } })
  },

  getPersonsByExactName(name: string) {
    return api.get('/persons/by-name', { params: { name } })
  },

  getPersonById(id: string) {
    return api.get(`/persons/${id}`)
  },

  updatePerson(id: string, data: any) {
    return api.put(`/persons/${id}`, data)
  },

  patchPerson(id: string, data: Partial<any>) {
    return api.patch(`/persons/${id}`, data)
  },

  deletePerson(id: string) {
    return api.delete(`/persons/${id}`)
  }
}
