<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api'
import type { FamilySearchResult } from '../types/family'
import FamilyFilters from '../components/family/FamilyFilters.vue'
import FamilyTable from '../components/family/FamilyTable.vue'
import FamilyPagination from '../components/family/FamilyPagination.vue'

const router = useRouter()

const families = ref<FamilySearchResult[]>([])
const isLoading = ref(false)
const error = ref('')
const searchQuery = ref('')
const sortBy = ref<'summary' | 'marriage_date' | 'marriage_place'>('summary')
const sortOrder = ref<'asc' | 'desc'>('asc')
const currentPage = ref(1)
const itemsPerPage = ref(20)
const totalItems = ref(0)

// Helper functions to reduce complexity
const matchesField = (field: string | undefined, query: string): boolean => {
  return field?.toLowerCase().includes(query) ?? false
}

const matchesSearchQuery = (family: FamilySearchResult, query: string): boolean => {
  return matchesField(family.summary, query) ||
         matchesField(family.marriage_place, query) ||
         matchesField(family.husband_name, query) ||
         matchesField(family.wife_name, query)
}

type SortConfig = {
  field: string
  order: 'asc' | 'desc'
}

const getSortValue = (family: FamilySearchResult, sortBy: string): string | number => {
  const value = family[sortBy as keyof FamilySearchResult]
  
  if (sortBy === 'marriage_date') {
    return value ? new Date(value as string).getTime() : 0
  }
  
  if (typeof value === 'string') {
    return value.toLowerCase()
  }
  
  return value || ''
}

const compareAscending = (aValue: string | number, bValue: string | number): number => {
  if (aValue < bValue) return -1
  if (aValue > bValue) return 1
  return 0
}

const compareDescending = (aValue: string | number, bValue: string | number): number => {
  if (aValue > bValue) return -1
  if (aValue < bValue) return 1
  return 0
}

const compareValues = (aValue: string | number, bValue: string | number, config: SortConfig): number => {
  if (config.order === 'asc') {
    return compareAscending(aValue, bValue)
  }
  return compareDescending(aValue, bValue)
}

const applySearchFilter = (families: FamilySearchResult[]): FamilySearchResult[] => {
  if (!searchQuery.value.trim()) {
    return families
  }
  
  const query = searchQuery.value.toLowerCase()
  return families.filter(family => matchesSearchQuery(family, query))
}

const applySorting = (families: FamilySearchResult[]): FamilySearchResult[] => {
  const config: SortConfig = {
    field: sortBy.value,
    order: sortOrder.value
  }
  
  return families.sort((a, b) => {
    const aValue = getSortValue(a, config.field)
    const bValue = getSortValue(b, config.field)
    return compareValues(aValue, bValue, config)
  })
}

// Computed properties
const filteredFamilies = computed(() => {
  const searchFiltered = applySearchFilter(families.value)
  return applySorting(searchFiltered)
})

const paginatedFamilies = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredFamilies.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredFamilies.value.length / itemsPerPage.value)
})

// Methods
const loadFamilies = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const data = await apiService.getAllFamiliesForManagement({
      skip: 0,
      limit: 100, // Server search endpoint has max limit of 100
    })
    families.value = data
    totalItems.value = data.length
  } catch (err: unknown) {
    console.error('Failed to load families:', err)
    const errorMessage = 
      err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : 'Failed to load families. Please try again.'
    error.value = errorMessage || 'Failed to load families. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const handleSort = (column: 'summary' | 'marriage_date' | 'marriage_place') => {
  if (sortBy.value === column) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortBy.value = column
    sortOrder.value = 'asc'
  }
}

const handleSearch = () => {
  currentPage.value = 1 // Reset to first page when searching
}

const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
}

const goToPage = (page: number) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const viewFamilyTree = (familyId: string) => {
  router.push(`/family/${familyId}`)
}

const downloadFamilyFile = async (familyId: string) => {
  try {
    const blob = await apiService.downloadFamilyFile(familyId)
    
    // Create download link
    const url = globalThis.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `family_${familyId}.gw`
    document.body.appendChild(link)
    link.click()
    link.remove()
    globalThis.URL.revokeObjectURL(url)
  } catch (err: unknown) {
    console.error('Failed to download family file:', err)
    error.value = 'Failed to download family file. Please try again.'
  }
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  loadFamilies()
})
</script>

<template>
  <div class="family-management-view">
    <div class="management-header">
      <button class="back-button" @click="goBack">← Back to Home</button>
      <h1 class="management-title">🔍 Family Search & Management</h1>
      <p class="management-subtitle">
        Search, explore, and manage all families in the database
      </p>
    </div>

    <!-- Filters Component -->
    <FamilyFilters
      v-model:search-query="searchQuery"
      v-model:sort-by="sortBy"
      v-model:sort-order="sortOrder"
      v-model:items-per-page="itemsPerPage"
      @search="handleSearch"
      @clear-search="clearSearch"
    />

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading families...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Error Loading Families</h3>
      <p>{{ error }}</p>
      <button @click="loadFamilies" class="retry-button">Try Again</button>
    </div>

    <!-- Data Grid -->
    <FamilyTable
      v-else-if="families.length > 0"
      :families="paginatedFamilies"
      :filtered-count="filteredFamilies.length"
      :total-count="totalItems"
      :sort-by="sortBy"
      :sort-order="sortOrder"
      @sort="handleSort"
      @refresh="loadFamilies"
      @view-tree="viewFamilyTree"
      @download="downloadFamilyFile"
    />

    <!-- Pagination -->
    <FamilyPagination
      v-if="families.length > 0"
      :current-page="currentPage"
      :total-pages="totalPages"
      @go-to-page="goToPage"
    />

    <!-- No Data State -->
    <div v-else class="no-data-state">
      <div class="no-data-icon">📊</div>
      <h3>No Families Found</h3>
      <p>There are no families in the database yet.</p>
      <div class="no-data-actions">
        <button @click="router.push('/upload')" class="upload-button">
          Upload Family File
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.family-management-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem 0;
}

.management-header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.back-button {
  position: absolute;
  left: 2rem;
  top: 0;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #2c3e50;
  transition: all 0.2s ease;
}

.back-button:hover {
  background: white;
  transform: translateY(-1px);
}

.management-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.management-subtitle {
  font-size: 1.2rem;
  color: #7f8c8d;
  max-width: 600px;
  margin: 0 auto;
}

.loading-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 1200px;
  margin: 0 auto;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 1200px;
  margin: 0 auto;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h3 {
  color: #e74c3c;
  margin-bottom: 1rem;
}

.retry-button {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.retry-button:hover {
  background: #c0392b;
}

.no-data-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 1200px;
  margin: 0 auto;
}

.no-data-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.no-data-state h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.no-data-actions {
  margin-top: 2rem;
}

.upload-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.upload-button:hover {
  background: #2980b9;
}

@media (max-width: 768px) {
  .family-management-view {
    padding: 1rem 0;
  }
  
  .management-header {
    margin-bottom: 2rem;
  }
  
  .back-button {
    position: static;
    margin-bottom: 1rem;
  }
  
  .management-title {
    font-size: 2rem;
  }
  
  .management-subtitle {
    font-size: 1rem;
  }
}
</style>