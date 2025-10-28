import api from './api'
import type { AxiosResponse } from 'axios'
import type { CreatePerson } from '@/types/person.ts'
import type { Person } from '@/types/family'

export const personService = {
  createPerson(data: CreatePerson): Promise<AxiosResponse<Person>> {
    return api.post<Person>('/api/v1/persons', data)
  },

  getAllPersons(params?: { page?: number; limit?: number }): Promise<AxiosResponse<Person[]>> {
    return api.get<Person[]>('/api/v1/persons', { params })
  },

  searchPersonsByName(name: string, params?: { page?: number; limit?: number }): Promise<AxiosResponse<Person[]>> {
    return api.get<Person[]>('/api/v1/persons/search', { params: { name, ...params } })
  },

  getPersonsByExactName(name: string): Promise<AxiosResponse<Person[]>> {
    return api.get<Person[]>('/api/v1/persons/by-name', { params: { name } })
  },

  getPersonById(id: string): Promise<AxiosResponse<Person>> {
    return api.get<Person>(`/api/v1/persons/${id}`)
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
