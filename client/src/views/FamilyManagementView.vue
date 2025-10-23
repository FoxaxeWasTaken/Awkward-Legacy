<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api'
import type { FamilySearchResult } from '../types/family'

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

const formatDate = (dateString?: string): string => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return dateString
  }
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

    <div class="management-controls">
      <div class="search-section">
        <div class="search-input-group">
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Search families by name, place, or notes..."
            class="search-input"
            @keyup.enter="handleSearch"
          />
          <button @click="handleSearch" class="search-button">Search</button>
          <button @click="clearSearch" class="clear-button">Clear</button>
        </div>
      </div>

      <div class="filter-section">
        <div class="filter-controls">
          <label class="filter-label">
            Sort by:
            <select v-model="sortBy" class="filter-select">
              <option value="summary">Family Name</option>
              <option value="marriage_date">Marriage Date</option>
              <option value="marriage_place">Marriage Place</option>
            </select>
          </label>
          <label class="filter-label">
            Order:
            <select v-model="sortOrder" class="filter-select">
              <option value="asc">Ascending</option>
              <option value="desc">Descending</option>
            </select>
          </label>
          <label class="filter-label">
            Items per page:
            <select v-model="itemsPerPage" class="filter-select">
              <option value="10">10</option>
              <option value="20">20</option>
              <option value="50">50</option>
              <option value="100">100</option>
            </select>
          </label>
        </div>
      </div>
    </div>

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
    <div v-else-if="families.length > 0" class="data-grid-container">
      <div class="grid-header">
        <h3>Families ({{ filteredFamilies.length }} of {{ totalItems }})</h3>
        <div class="grid-actions">
          <button @click="loadFamilies" class="refresh-button">Refresh</button>
        </div>
      </div>

      <div class="data-grid">
        <table class="families-table">
          <thead>
            <tr>
              <th @click="handleSort('summary')" class="sortable">
                Family Name
                <span v-if="sortBy === 'summary'" class="sort-indicator">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th>Husband</th>
              <th>Wife</th>
              <th @click="handleSort('marriage_date')" class="sortable">
                Marriage Date
                <span v-if="sortBy === 'marriage_date'" class="sort-indicator">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th @click="handleSort('marriage_place')" class="sortable">
                Marriage Place
                <span v-if="sortBy === 'marriage_place'" class="sort-indicator">
                  {{ sortOrder === 'asc' ? '↑' : '↓' }}
                </span>
              </th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="family in paginatedFamilies" :key="family.id" class="family-row">
              <td class="family-name">{{ family.summary || 'N/A' }}</td>
              <td>{{ family.husband_name || 'N/A' }}</td>
              <td>{{ family.wife_name || 'N/A' }}</td>
              <td>{{ formatDate(family.marriage_date) }}</td>
              <td>{{ family.marriage_place || 'N/A' }}</td>
              <td class="actions-cell">
                <div class="action-buttons">
                  <button 
                    @click="viewFamilyTree(family.id)" 
                    class="action-button view-button"
                    title="View Family Tree"
                  >
                    🌳 View Tree
                  </button>
                  <button 
                    @click="downloadFamilyFile(family.id)" 
                    class="action-button download-button"
                    title="Download Family File"
                  >
                    💾 Download
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      <div v-if="totalPages > 1" class="pagination">
        <button 
          @click="goToPage(currentPage - 1)"
          :disabled="currentPage === 1"
          class="pagination-button"
        >
          Previous
        </button>
        
        <div class="pagination-pages">
          <button
            v-for="page in Math.min(5, totalPages)"
            :key="page"
            @click="goToPage(page)"
            :class="{ active: page === currentPage }"
            class="pagination-page"
          >
            {{ page }}
          </button>
          <span v-if="totalPages > 5" class="pagination-ellipsis">...</span>
          <button
            v-if="totalPages > 5"
            @click="goToPage(totalPages)"
            :class="{ active: currentPage === totalPages }"
            class="pagination-page"
          >
            {{ totalPages }}
          </button>
        </div>
        
        <button 
          @click="goToPage(currentPage + 1)"
          :disabled="currentPage === totalPages"
          class="pagination-button"
        >
          Next
        </button>
      </div>
    </div>

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

.management-controls {
  max-width: 1200px;
  margin: 0 auto 2rem;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.search-section {
  margin-bottom: 2rem;
}

.search-input-group {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #3498db;
}

.search-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.search-button:hover {
  background: #2980b9;
}

.clear-button {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.clear-button:hover {
  background: #7f8c8d;
}

.filter-section {
  border-top: 1px solid #ecf0f1;
  padding-top: 2rem;
}

.filter-controls {
  display: flex;
  gap: 2rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.filter-select {
  padding: 0.5rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  font-size: 0.9rem;
}

.data-grid-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 2rem 1rem;
  border-bottom: 1px solid #ecf0f1;
}

.grid-header h3 {
  color: #2c3e50;
  margin: 0;
}

.refresh-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: background-color 0.2s;
}

.refresh-button:hover {
  background: #2980b9;
}

.data-grid {
  overflow-x: auto;
}

.families-table {
  width: 100%;
  border-collapse: collapse;
}

.families-table th {
  background: #f8f9fa;
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #2c3e50;
  border-bottom: 2px solid #ecf0f1;
}

.families-table th.sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color 0.2s;
}

.families-table th.sortable:hover {
  background: #e9ecef;
}

.sort-indicator {
  margin-left: 0.5rem;
  color: #3498db;
}

.families-table td {
  padding: 1rem;
  border-bottom: 1px solid #ecf0f1;
  vertical-align: middle;
}

.family-row:hover {
  background: #f8f9fa;
}

.family-name {
  font-weight: 500;
  color: #2c3e50;
}

.actions-cell {
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  gap: 0.5rem;
}

.action-button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.view-button {
  background: #2ecc71;
  color: white;
}

.view-button:hover {
  background: #27ae60;
  transform: translateY(-1px);
}

.download-button {
  background: #e74c3c;
  color: white;
}

.download-button:hover {
  background: #c0392b;
  transform: translateY(-1px);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  gap: 1rem;
}

.pagination-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background: #2980b9;
}

.pagination-button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.pagination-pages {
  display: flex;
  gap: 0.5rem;
}

.pagination-page {
  background: white;
  color: #2c3e50;
  border: 1px solid #e9ecef;
  padding: 0.5rem 0.75rem;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-page:hover {
  background: #f8f9fa;
}

.pagination-page.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.pagination-ellipsis {
  padding: 0.5rem;
  color: #7f8c8d;
}

.loading-state,
.error-state,
.no-data-state {
  text-align: center;
  padding: 4rem 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  max-width: 600px;
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

.error-icon,
.no-data-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-state h3,
.no-data-state h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.error-state p,
.no-data-state p {
  color: #7f8c8d;
  margin-bottom: 2rem;
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

.no-data-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.upload-button {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.upload-button:hover {
  background: #27ae60;
}

/* Responsive Design */
@media (max-width: 768px) {
  .management-title {
    font-size: 2rem;
  }

  .back-button {
    position: static;
    margin-bottom: 1rem;
  }

  .search-input-group {
    flex-direction: column;
  }

  .filter-controls {
    flex-direction: column;
    align-items: flex-start;
  }

  .data-grid-container {
    padding: 0 1rem;
  }

  .families-table {
    font-size: 0.9rem;
  }

  .families-table th,
  .families-table td {
    padding: 0.75rem 0.5rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .pagination {
    flex-direction: column;
    gap: 1rem;
  }
}

@media (max-width: 480px) {
  .families-table {
    font-size: 0.8rem;
  }

  .families-table th,
  .families-table td {
    padding: 0.5rem 0.25rem;
  }

  .action-button {
    padding: 0.25rem 0.5rem;
    font-size: 0.7rem;
  }
}
</style>
