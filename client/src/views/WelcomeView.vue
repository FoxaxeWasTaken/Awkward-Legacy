<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api'
import type { FamilySearchResult } from '../types/family'

const router = useRouter()

const navigateToUpload = () => {
  router.push('/upload')
}

const navigateToManage = () => {
  router.push('/manage')
}

// Search functionality
const searchQuery = ref('')
const searchResults = ref<FamilySearchResult[]>([])
const isSearching = ref(false)
const searchError = ref('')
const resultsLimit = ref(20)

const handleSearch = async () => {
  if (!searchQuery.value.trim()) return
  
  isSearching.value = true
  searchError.value = ''
  
  try {
    const results = await apiService.getAllFamiliesForManagement({
      limit: resultsLimit.value
    })
    
    // Filter results based on search query
    const query = searchQuery.value.toLowerCase()
    searchResults.value = results.filter(family => 
      family.husband_name?.toLowerCase().includes(query) ||
      family.wife_name?.toLowerCase().includes(query) ||
      family.marriage_place?.toLowerCase().includes(query) ||
      family.summary?.toLowerCase().includes(query)
    )
  } catch (error) {
    console.error('Search error:', error)
    searchError.value = 'Failed to search families. Please try again.'
  } finally {
    isSearching.value = false
  }
}

const clearSearch = () => {
  searchQuery.value = ''
  searchResults.value = []
  searchError.value = ''
}

const navigateToFamily = (familyId: string) => {
  router.push(`/family/${familyId}`)
}

// Health check on mount
onMounted(async () => {
  try {
    await apiService.checkHealth()
  } catch (error) {
    console.warn('Health check failed:', error)
  }
})
</script>

<template>
  <div class="welcome-view">
    <!-- Header -->
    <div class="welcome-header">
      <h1>Geneweb Family Search</h1>
      <p>Explore family trees and genealogical data</p>
    </div>

    <!-- Family Search Section -->
    <div class="search-section">
      <h2>Family Search</h2>
      <div class="search-input-group">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Enter family name"
          class="search-input"
          @keyup.enter="handleSearch"
        />
        <button 
          @click="handleSearch" 
          class="search-button"
          :disabled="!searchQuery.trim() || isSearching"
        >
          Search
        </button>
      </div>
      
      <!-- Results limit selector -->
      <div class="results-limit">
        <label for="results-limit">Results limit:</label>
        <select id="results-limit" v-model="resultsLimit">
          <option value="10">10</option>
          <option value="20" selected>20</option>
          <option value="50">50</option>
          <option value="100">100</option>
        </select>
      </div>

      <!-- Welcome state -->
      <div v-if="!searchResults.length && !searchQuery" class="welcome-state">
        <h3>Welcome to Family Search</h3>
        <p>Enter a family name above to search</p>
        <div class="search-examples">
          <h4>Search Examples:</h4>
          <ul>
            <li>Search by first name</li>
            <li>Search by last name</li>
            <li>Search by full name</li>
          </ul>
        </div>
      </div>

      <!-- Search results -->
      <div v-if="searchResults.length > 0" class="search-results">
        <h3>Search Results ({{ searchResults.length }})</h3>
        <div class="results-list">
          <div 
            v-for="family in searchResults" 
            :key="family.id"
            class="result-item"
            @click="navigateToFamily(family.id)"
          >
            <h4>{{ family.summary }}</h4>
            <p>Marriage: {{ family.marriage_date || 'Unknown' }}</p>
            <p>Place: {{ family.marriage_place || 'Unknown' }}</p>
            <p>Children: {{ family.children_count }}</p>
          </div>
        </div>
      </div>

      <!-- Error state -->
      <div v-if="searchError" class="error-message">
        {{ searchError }}
      </div>

      <!-- Loading state -->
      <div v-if="isSearching" class="loading-message">
        Searching families...
      </div>
    </div>

    <div class="welcome-actions">
      <div class="action-cards">
        <div class="action-card upload-card" @click="navigateToUpload">
          <div class="card-icon">📁</div>
          <h3 class="card-title">Upload Family File</h3>
          <p class="card-description">
            Upload and import your GeneWeb (.gw) files to the database
          </p>
          <div class="card-features">
            <span class="feature">• Drag & drop upload</span>
            <span class="feature">• Automatic parsing</span>
            <span class="feature">• Instant preview</span>
          </div>
          <button class="card-button">Upload File</button>
        </div>

        <div class="action-card manage-card" @click="navigateToManage">
          <div class="card-icon">🔍</div>
          <h3 class="card-title">Search & Manage Families</h3>
          <p class="card-description">
            Search, explore, and manage all families in the database
          </p>
          <div class="card-features">
            <span class="feature">• Browse family trees</span>
            <span class="feature">• Advanced filtering</span>
            <span class="feature">• Interactive visualization</span>
            <span class="feature">• Data export</span>
          </div>
          <button class="card-button">Explore Families</button>
        </div>
      </div>
    </div>

    <div class="welcome-features">
      <h2 class="features-title">What you can do</h2>
      <div class="features-grid">
        <div class="feature-item">
          <div class="feature-icon">🌳</div>
          <h4>Family Trees</h4>
          <p>Visualize complex family relationships with interactive tree diagrams</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📋</div>
          <h4>Data Management</h4>
          <p>Organize and manage genealogical data with powerful filtering tools</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">💾</div>
          <h4>Import/Export</h4>
          <p>Upload GeneWeb files and export data in standard formats</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🔍</div>
          <h4>Search & Discovery</h4>
          <p>Find families and individuals with advanced search capabilities</p>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <footer class="welcome-footer">
      <p>© 2024 Geneweb Family Search</p>
    </footer>
  </div>
</template>

<style scoped>
.welcome-view {
  min-height: calc(100vh - 200px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem 0;
}

/* Header styles */
.welcome-header {
  text-align: center;
  margin-bottom: 3rem;
}

.welcome-header h1 {
  font-size: 3rem;
  color: #2c3e50;
  margin-bottom: 1rem;
  font-weight: 700;
}

.welcome-header p {
  font-size: 1.2rem;
  color: #7f8c8d;
  margin-bottom: 0;
}

/* Search section styles */
.search-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  margin: 2rem auto;
  max-width: 800px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.search-section h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.search-input-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
}

.search-input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s ease;
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
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.search-button:hover:not(:disabled) {
  background: #2980b9;
}

.search-button:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.results-limit {
  margin-bottom: 1rem;
}

.results-limit label {
  margin-right: 0.5rem;
  color: #2c3e50;
}

.results-limit select {
  padding: 0.5rem;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

/* Welcome state */
.welcome-state {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
}

.welcome-state h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.search-examples {
  margin-top: 1.5rem;
  text-align: left;
  max-width: 300px;
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

/* Search results */
.search-results {
  margin-top: 2rem;
}

.search-results h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
}

.results-list {
  display: grid;
  gap: 1rem;
}

.result-item {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.result-item:hover {
  background: #e3f2fd;
  border-color: #3498db;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.result-item h4 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.result-item p {
  color: #7f8c8d;
  margin: 0.25rem 0;
  font-size: 0.9rem;
}

/* Error and loading states */
.error-message {
  color: #e74c3c;
  background: #fdf2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.loading-message {
  color: #3498db;
  text-align: center;
  padding: 1rem;
  font-style: italic;
}

/* Footer */
.welcome-footer {
  text-align: center;
  padding: 2rem;
  color: #7f8c8d;
  border-top: 1px solid #e0e0e0;
  margin-top: 3rem;
}

.welcome-actions {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
  max-width: 800px;
  margin-left: auto;
  margin-right: auto;
}

.action-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.upload-card:hover {
  border-color: #e74c3c;
}

.manage-card:hover {
  border-color: #2ecc71;
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.card-description {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.card-features {
  margin-bottom: 2rem;
}

.feature {
  display: block;
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.card-button {
  width: 100%;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.card-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.welcome-features {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  text-align: center;
}

.features-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 3rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-item {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.feature-item:hover {
  transform: translateY(-3px);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-item h4 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.feature-item p {
  color: #7f8c8d;
  line-height: 1.6;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .action-cards {
    grid-template-columns: 1fr;
  }

  .welcome-hero {
    padding: 2rem 1rem;
  }

  .welcome-actions,
  .welcome-features {
    padding: 0 1rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }

  .action-card {
    padding: 1.5rem;
  }
}
</style>
