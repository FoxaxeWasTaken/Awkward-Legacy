import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import type { 
  FamilySearchResult, 
  FamilyDetailResult, 
  FamilySearchParams,
  UploadResult,
  FamilyRead,
  FamilyManagementParams,
  FamilyDetail
} from '../types/family'

class ApiService {
  private readonly api: AxiosInstance

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Add request interceptor for logging
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
        return config
      },
      (error) => {
        console.error('API Request Error:', error)
        return Promise.reject(error instanceof Error ? error : new Error(String(error)))
      },
    )

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`)
        return response
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message)
        return Promise.reject(error instanceof Error ? error : new Error(String(error)))
      },
    )
  }

  // Family search methods
  async searchFamilies(params: FamilySearchParams): Promise<FamilySearchResult[]> {
    const response: AxiosResponse<FamilySearchResult[]> = await this.api.get(
      '/api/v1/families/search',
      {
        params,
      },
    )
    return response.data
  }

  async getFamilyDetail(familyId: string): Promise<FamilyDetailResult> {
    const response: AxiosResponse<FamilyDetailResult> = await this.api.get(
      `/api/v1/families/${familyId}/detail`,
    )
    return response.data
  }

  async getFamily(familyId: string): Promise<FamilyDetailResult> {
    const response: AxiosResponse<FamilyDetailResult> = await this.api.get(
      `/api/v1/families/${familyId}`,
    )
    return response.data
  }

  // Generic HTTP methods for backward compatibility
  get(url: string, config?: any) {
    return this.api.get(url, config)
  }

  post(url: string, data?: any, config?: any) {
    return this.api.post(url, data, config)
  }

  put(url: string, data?: any, config?: any) {
    return this.api.put(url, data, config)
  }

  patch(url: string, data?: any, config?: any) {
    return this.api.patch(url, data, config)
  }

  delete(url: string, config?: any) {
    return this.api.delete(url, config)
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      await this.api.get('/health')
      return true
    } catch (error) {
      console.error('Health check failed:', error)
      return false
    }
  }

  // File upload methods
  async uploadFamilyFile(file: File): Promise<UploadResult> {
    const formData = new FormData()
    formData.append('file', file)

    const response: AxiosResponse<UploadResult> = await this.api.post(
      '/api/v1/files/import',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  }

  // File download methods
  async downloadFamilyFile(familyId: string): Promise<Blob> {
    const response: AxiosResponse<Blob> = await this.api.get(
      `/api/v1/files/export/family/${familyId}`,
      {
        responseType: 'blob',
      }
    )
    return response.data
  }

  // Helper methods for family management
  private async fetchFamilyDetails(familyId: string): Promise<FamilyDetail> {
    const detailResponse: AxiosResponse<FamilyDetail> = await this.api.get(
      `/api/v1/families/${familyId}/detail`
    )
    return detailResponse.data
  }

  private buildPersonName(person: { first_name?: string; last_name?: string } | null): string {
    if (!person) return 'Unknown'
    const fullName = `${person.first_name || ''} ${person.last_name || ''}`.trim()
    return fullName || 'Unknown'
  }


  private async processFamilyWithDetails(family: FamilyRead): Promise<FamilySearchResult> {
    try {
      const familyDetail = await this.fetchFamilyDetails(family.id)
      const husbandName = this.buildPersonName(familyDetail.husband || null)
      const wifeName = this.buildPersonName(familyDetail.wife || null)
      
      return {
        id: family.id,
        husband_name: husbandName,
        wife_name: wifeName,
        marriage_date: family.marriage_date,
        marriage_place: family.marriage_place,
        children_count: familyDetail.children?.length || 0,
        summary: `${husbandName} & ${wifeName}`
      }
    } catch (detailError) {
      console.warn(`Failed to fetch details for family ${family.id}:`, detailError)
      // Fallback to unknown names when detail fetch fails
      const husbandDisplayName = 'Unknown Husband'
      const wifeDisplayName = 'Unknown Wife'
      
      return {
        id: family.id,
        husband_name: husbandDisplayName,
        wife_name: wifeDisplayName,
        marriage_date: family.marriage_date,
        marriage_place: family.marriage_place,
        children_count: 0,
        summary: `${husbandDisplayName} & ${wifeDisplayName}`
      }
    }
  }

  // Family management methods
  async getAllFamiliesForManagement(
    params: FamilyManagementParams = {}
  ): Promise<FamilySearchResult[]> {
    try {
      // Use the search endpoint which returns FamilySearchResult with proper names
      // Note: Server has a max limit of 100 for search endpoint
      // Use a wildcard search to get all families
      const response: AxiosResponse<FamilySearchResult[]> = await this.api.get(
        '/api/v1/families/search',
        {
          params: {
            q: '%', // Wildcard search to get all families
            limit: Math.min(params.limit || 100, 100),
          },
        }
      )
      
      return response.data
    } catch (error) {
      console.error('Error fetching families for management:', error)
      throw error
    }
  }
}

// Export singleton instance
export const apiService = new ApiService()
export default apiService
