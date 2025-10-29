import api from './api'
import type { AxiosResponse } from 'axios'
import type { FamilyRead } from '@/types/family'

export interface CreateFamily {
  husband_id?: string
  wife_id?: string
  marriage_date?: string
  marriage_place?: string
  notes?: string
}

export const familyService = {
  createFamily(data: CreateFamily): Promise<AxiosResponse<FamilyRead>> {
    return api.post<FamilyRead>('/api/v1/families', data)
  },

  getAllFamilies(params?: { skip?: number; limit?: number }): Promise<AxiosResponse<FamilyRead[]>> {
    return api.get<FamilyRead[]>('/api/v1/families', { params })
  },

  getFamilyById(id: string): Promise<AxiosResponse<FamilyRead>> {
    return api.get<FamilyRead>(`/api/v1/families/${id}`)
  },

  getFamiliesByHusband(husbandId: string): Promise<AxiosResponse<FamilyRead[]>> {
    return api.get<FamilyRead[]>(`/api/v1/families/by-husband/${husbandId}`)
  },

  getFamiliesByWife(wifeId: string): Promise<AxiosResponse<FamilyRead[]>> {
    return api.get<FamilyRead[]>(`/api/v1/families/by-wife/${wifeId}`)
  },

  getFamiliesBySpouse(spouseId: string): Promise<AxiosResponse<FamilyRead[]>> {
    return api.get<FamilyRead[]>(`/api/v1/families/by-spouse/${spouseId}`)
  },

  updateFamily(id: string, data: Partial<CreateFamily>): Promise<AxiosResponse<FamilyRead>> {
    return api.patch<FamilyRead>(`/api/v1/families/${id}`, data)
  },

  deleteFamily(id: string) {
    return api.delete(`/api/v1/families/${id}`)
  },
}


