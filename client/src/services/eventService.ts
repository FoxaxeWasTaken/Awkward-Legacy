import api from './api'

export interface CreateEvent {
  person_id?: string | null
  family_id?: string | null
  type: string
  date?: string | null
  place?: string | null
  description?: string | null
}

export const eventService = {
  createEvent(data: CreateEvent) {
    return api.post('/api/v1/events', data)
  },

  getEvents(params?: { skip?: number; limit?: number }) {
    return api.get('/api/v1/events', { params })
  },

  getEventTypes() {
    return api.get<string[]>('/api/v1/events/types')
  },

  getEventsByPerson(personId: string) {
    return api.get(`/api/v1/events/by-person/${personId}`)
  },

  getEventsByFamily(familyId: string) {
    return api.get(`/api/v1/events/by-family/${familyId}`)
  },

  getEventById(id: string) {
    return api.get(`/api/v1/events/${id}`)
  },

  updateEvent(id: string, data: Partial<CreateEvent>) {
    return api.put(`/api/v1/events/${id}`, data)
  },

  patchEvent(id: string, data: Partial<CreateEvent>) {
    return api.patch(`/api/v1/events/${id}`, data)
  },

  deleteEvent(id: string) {
    return api.delete(`/api/v1/events/${id}`)
  },
}




