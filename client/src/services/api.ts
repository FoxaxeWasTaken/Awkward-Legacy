import axios from 'axios';
import type { AxiosInstance, AxiosResponse } from 'axios';
import type { FamilySearchResult, FamilyDetailResult, FamilySearchParams } from '../types/family';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor for logging
    this.api.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Add response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  // Family search methods
  async searchFamilies(params: FamilySearchParams): Promise<FamilySearchResult[]> {
    const response: AxiosResponse<FamilySearchResult[]> = await this.api.get('/api/v1/families/search', {
      params,
    });
    return response.data;
  }

  async getFamilyDetail(familyId: string): Promise<FamilyDetailResult> {
    const response: AxiosResponse<FamilyDetailResult> = await this.api.get(
      `/api/v1/families/${familyId}/detail`
    );
    return response.data;
  }

  async getFamily(familyId: string): Promise<FamilyDetailResult> {
    const response: AxiosResponse<FamilyDetailResult> = await this.api.get(
      `/api/v1/families/${familyId}`
    );
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      await this.api.get('/health');
      return true;
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
