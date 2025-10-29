<template>
  <div class="management-controls">
    <div class="search-section">
      <div class="search-input-group">
        <input
          :value="searchQuery"
          @input="$emit('update:searchQuery', ($event.target as HTMLInputElement).value)"
          type="text"
          placeholder="Search families by name, place, or notes..."
          class="search-input"
          @keyup.enter="$emit('search')"
        />
        <button @click="$emit('search')" class="search-button">Search</button>
        <button @click="$emit('clear-search')" class="clear-button">Clear</button>
      </div>
    </div>

    <div class="filter-section">
      <div class="filter-controls">
        <label class="filter-label">
          Sort by:
          <select 
            :value="sortBy" 
            @change="$emit('update:sortBy', ($event.target as HTMLSelectElement).value as 'summary' | 'marriage_date' | 'marriage_place')"
            class="filter-select"
          >
            <option value="summary">Family Name</option>
            <option value="marriage_date">Marriage Date</option>
            <option value="marriage_place">Marriage Place</option>
          </select>
        </label>
        <label class="filter-label">
          Order:
          <select 
            :value="sortOrder" 
            @change="$emit('update:sortOrder', ($event.target as HTMLSelectElement).value as 'asc' | 'desc')"
            class="filter-select"
          >
            <option value="asc">Ascending</option>
            <option value="desc">Descending</option>
          </select>
        </label>
        <label class="filter-label">
          Items per page:
          <select 
            :value="itemsPerPage" 
            @change="$emit('update:itemsPerPage', Number(($event.target as HTMLSelectElement).value))"
            class="filter-select"
          >
            <option value="10">10</option>
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  searchQuery: string
  sortBy: 'summary' | 'marriage_date' | 'marriage_place'
  sortOrder: 'asc' | 'desc'
  itemsPerPage: number
}

defineProps<Props>()

defineEmits<{
  'update:searchQuery': [value: string]
  'update:sortBy': [value: 'summary' | 'marriage_date' | 'marriage_place']
  'update:sortOrder': [value: 'asc' | 'desc']
  'update:itemsPerPage': [value: number]
  search: []
  'clear-search': []
}>()
</script>

<style scoped>
.management-controls {
  max-width: 1200px;
  margin: 0 auto 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  padding: 1.5rem 2rem;
}

.search-section {
  margin-bottom: 1.5rem;
}

.search-input-group {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 0.9rem;
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
  font-size: 0.9rem;
  transition: background-color 0.2s;
  min-width: 100px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-button:hover {
  background: #2980b9;
}

.clear-button {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.9rem;
  transition: background-color 0.2s;
  min-width: 100px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-button:hover {
  background: #c0392b;
}

.filter-section {
  border-top: 1px solid #e9ecef;
  padding-top: 1.5rem;
}

.filter-controls {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1.5rem;
  align-items: end;
}

.filter-label {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  font-weight: 500;
  color: #495057;
  font-size: 0.9rem;
}

.filter-select {
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 6px;
  font-size: 0.9rem;
  background: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.filter-select:focus {
  outline: none;
  border-color: #3498db;
}

@media (max-width: 768px) {
  .filter-controls {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .search-input-group {
    flex-direction: column;
    gap: 1rem;
  }
}
</style>

