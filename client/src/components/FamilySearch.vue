<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api'
import type { FamilySearchResult, FamilySearchParams } from '../types/family'
import FamilyCard from './FamilyCard.vue'

const router = useRouter()

const searchQuery = ref('')
const searchLimit = ref(20)
const searchResults = ref<FamilySearchResult[]>([])
const isLoading = ref(false)
const error = ref('')
const hasSearched = ref(false)
const restoreSearchState = () => {
  try {
    const savedQuery = sessionStorage.getItem('familySearchQuery')
    const savedResults = sessionStorage.getItem('familySearchResults')
    const savedHasSearched = sessionStorage.getItem('familySearchHasSearched')

    if (savedQuery) {
      searchQuery.value = savedQuery
    }
    if (savedResults) {
      searchResults.value = JSON.parse(savedResults)
    }
    if (savedHasSearched === 'true') {
      hasSearched.value = true
    }
  } catch (error) {
    console.warn('Failed to restore search state:', error)
  }
}

const saveSearchState = () => {
  try {
    sessionStorage.setItem('familySearchQuery', searchQuery.value)
    sessionStorage.setItem('familySearchResults', JSON.stringify(searchResults.value))
    sessionStorage.setItem('familySearchHasSearched', hasSearched.value.toString())
  } catch (error) {
    console.warn('Failed to save search state:', error)
  }
}
const clearSearchState = () => {
  try {
    sessionStorage.removeItem('familySearchQuery')
    sessionStorage.removeItem('familySearchResults')
    sessionStorage.removeItem('familySearchHasSearched')
  } catch (error) {
    console.warn('Failed to clear search state:', error)
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    return
  }

  isLoading.value = true
  error.value = ''
  hasSearched.value = true

  try {
    const params: FamilySearchParams = {
      q: searchQuery.value.trim(),
      limit: searchLimit.value,
    }

    const results = await apiService.searchFamilies(params)
    searchResults.value = results
    saveSearchState()
  } catch (err: unknown) {
    console.error('Search error:', err)
    const errorMessage =
      err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : 'Failed to search families. Please try again.'
    error.value = errorMessage || 'Failed to search families. Please try again.'
    searchResults.value = []
  } finally {
    isLoading.value = false
  }
}

const handleInputChange = () => {
  if (hasSearched.value && searchResults.value.length > 0) {
    searchResults.value = []
    hasSearched.value = false
    clearSearchState()
  }
}

const handleViewDetails = (familyId: string) => {
  router.push(`/family/${familyId}`)
}

const clearError = () => {
  error.value = ''
  hasSearched.value = false
  clearSearchState()
}

onMounted(async () => {
  restoreSearchState()
  const isHealthy = await apiService.healthCheck()
  if (!isHealthy) {
    error.value = 'Unable to connect to the server. Please check your connection.'
  }
})
</script>

<template>
  <div class="family-search">
    <div class="search-header">
      <h2>Family Search</h2>
      <p>Search for families by name or view family trees</p>
    </div>

    <div class="search-form">
      <div class="search-input-group">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Enter family name (e.g., John Doe, Smith, etc.)"
          class="search-input"
          @keyup.enter="handleSearch"
          @input="handleInputChange"
        />
        <button
          @click="handleSearch"
          :disabled="isLoading || !searchQuery.trim()"
          class="search-button"
        >
          <span v-if="isLoading">Searching...</span>
          <span v-else>Search</span>
        </button>
      </div>

      <div class="search-options">
        <label class="limit-label">
          Results limit:
          <select v-model="searchLimit" class="limit-select">
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </label>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Searching families...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Search Error</h3>
      <p>{{ error }}</p>
      <button @click="clearError" class="retry-button">Try Again</button>
    </div>

    <div v-else-if="searchResults.length > 0" class="search-results">
      <h3>Search Results ({{ searchResults.length }})</h3>
      <div class="results-grid">
        <FamilyCard
          v-for="family in searchResults"
          :key="family.id"
          :family="family"
          @view-details="handleViewDetails"
        />
      </div>
    </div>

    <div v-else-if="hasSearched && !isLoading" class="no-results">
      <div class="no-results-icon">🔍</div>
      <h3>No Families Found</h3>
      <p>No families match your search criteria. Try a different search term.</p>
    </div>

    <div v-else class="welcome-state">
      <div class="welcome-icon">👨‍👩‍👧‍👦</div>
      <h3>Welcome to Family Search</h3>
      <p>Enter a family name above to search for families in the Geneweb database.</p>
      <div class="search-examples">
        <h4>Search Examples:</h4>
        <ul>
          <li>Search by first name: "John"</li>
          <li>Search by last name: "Smith"</li>
          <li>Search by full name: "John Doe"</li>
        </ul>
      </div>
    </div>
  </div>
</template>
