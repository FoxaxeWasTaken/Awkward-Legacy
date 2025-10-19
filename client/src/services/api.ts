import axios from 'axios'
import type { AxiosInstance, AxiosResponse } from 'axios'
import type { 
  FamilySearchResult, 
  FamilyDetailResult, 
  FamilySearchParams,
  UploadResult,
  FamilyRead,
  FamilyManagementParams
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

  // Family management methods
  async getAllFamiliesForManagement(
    params: FamilyManagementParams = {}
  ): Promise<FamilySearchResult[]> {
    try {
      // Get basic families first
      const response: AxiosResponse<FamilyRead[]> = await this.api.get(
        '/api/v1/families',
        {
          params: {
            skip: params.skip || 0,
            limit: Math.min(params.limit || 100, 1000),
          },
        }
      )
      
      // For each family, get the detailed information to extract names
      const familiesWithNames: FamilySearchResult[] = []
      
      for (const family of response.data) {
        try {
          // Get family detail to get actual names
          const detailResponse: AxiosResponse<any> = await this.api.get(
            `/api/v1/families/${family.id}/detail`
          )
          
          const familyDetail = detailResponse.data
          const husbandName = familyDetail.husband 
            ? `${familyDetail.husband.first_name || ''} ${familyDetail.husband.last_name || ''}`.trim() || 'Unknown'
            : 'Unknown'
          const wifeName = familyDetail.wife 
            ? `${familyDetail.wife.first_name || ''} ${familyDetail.wife.last_name || ''}`.trim() || 'Unknown'
            : 'Unknown'
          
          familiesWithNames.push({
            id: family.id,
            husband_name: husbandName,
            wife_name: wifeName,
            marriage_date: family.marriage_date,
            marriage_place: family.marriage_place,
            children_count: familyDetail.children?.length || 0,
            summary: `${husbandName} & ${wifeName}`
          })
        } catch (detailError) {
          // If detail fetch fails, fall back to ID-based names
          familiesWithNames.push({
            id: family.id,
            husband_name: family.husband_id ? `Person ${family.husband_id.slice(0, 8)}` : 'Unknown',
            wife_name: family.wife_id ? `Person ${family.wife_id.slice(0, 8)}` : 'Unknown',
            marriage_date: family.marriage_date,
            marriage_place: family.marriage_place,
            children_count: 0,
            summary: `${family.husband_id ? `Person ${family.husband_id.slice(0, 8)}` : 'Unknown'} & ${family.wife_id ? `Person ${family.wife_id.slice(0, 8)}` : 'Unknown'}`
          })
        }
      }
      
      return familiesWithNames
    } catch (error) {
      console.error('Error fetching families for management:', error)
      throw error
    }
  }
}

// Export singleton instance
export const apiService = new ApiService()
export default apiService
