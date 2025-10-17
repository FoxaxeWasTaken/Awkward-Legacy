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

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Searching families...</p>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Search Error</h3>
      <p>{{ error }}</p>
      <button @click="clearError" class="retry-button">Try Again</button>
    </div>

    <!-- Results -->
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

    <!-- No Results -->
    <div v-else-if="hasSearched && !isLoading" class="no-results">
      <div class="no-results-icon">🔍</div>
      <h3>No Families Found</h3>
      <p>No families match your search criteria. Try a different search term.</p>
    </div>

    <!-- Welcome State -->
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

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api'
import type { FamilySearchResult, FamilySearchParams } from '../types/family'
import FamilyCard from './FamilyCard.vue'

const router = useRouter()

// Reactive state
const searchQuery = ref('')
const searchLimit = ref(20)
const searchResults = ref<FamilySearchResult[]>([])
const isLoading = ref(false)
const error = ref('')
const hasSearched = ref(false)

// Methods
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
  // Clear results when user starts typing a new search
  if (hasSearched.value && searchResults.value.length > 0) {
    searchResults.value = []
    hasSearched.value = false
  }
}

const handleViewDetails = (familyId: string) => {
  router.push(`/family/${familyId}`)
}

const clearError = () => {
  error.value = ''
  hasSearched.value = false
}

// Check API health on mount
onMounted(async () => {
  const isHealthy = await apiService.healthCheck()
  if (!isHealthy) {
    error.value = 'Unable to connect to the server. Please check your connection.'
  }
})
</script>

<style scoped>
.family-search {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.search-header {
  text-align: center;
  margin-bottom: 2rem;
}

.search-header h2 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.search-header p {
  color: #7f8c8d;
  font-size: 1.1rem;
}

.search-form {
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.search-input-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
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
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.search-button:hover:not(:disabled) {
  background: #2980b9;
}

.search-button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.search-options {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.limit-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #7f8c8d;
}

.limit-select {
  padding: 0.25rem 0.5rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 3rem;
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
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* Error State */
.error-state {
  text-align: center;
  padding: 3rem;
  background: #fdf2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #dc2626;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Results */
.search-results h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

/* No Results */
.no-results {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
}

.no-results-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* Welcome State */
.welcome-state {
  text-align: center;
  padding: 3rem;
  color: #7f8c8d;
}

.welcome-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.search-examples {
  margin-top: 2rem;
  text-align: left;
  max-width: 400px;
  margin-left: auto;
  margin-right: auto;
}

.search-examples h4 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.search-examples ul {
  list-style: none;
  padding: 0;
}

.search-examples li {
  padding: 0.25rem 0;
  color: #7f8c8d;
}

/* Responsive */
@media (max-width: 768px) {
  .family-search {
    padding: 1rem;
  }

  .search-input-group {
    flex-direction: column;
  }

  .results-grid {
    grid-template-columns: 1fr;
  }
}
</style>
