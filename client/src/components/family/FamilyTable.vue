<template>
  <div class="data-grid-container">
    <div class="grid-header">
      <h3>Families ({{ filteredCount }} of {{ totalCount }})</h3>
      <div class="grid-actions">
        <button @click="$emit('refresh')" class="refresh-button">Refresh</button>
      </div>
    </div>

    <div class="data-grid">
      <table class="families-table">
        <thead>
          <tr>
            <th @click="$emit('sort', 'summary')" class="sortable">
              Family Name
              <span v-if="sortBy === 'summary'" class="sort-indicator">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th>Husband</th>
            <th>Wife</th>
            <th @click="$emit('sort', 'marriage_date')" class="sortable">
              Marriage Date
              <span v-if="sortBy === 'marriage_date'" class="sort-indicator">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th @click="$emit('sort', 'marriage_place')" class="sortable">
              Marriage Place
              <span v-if="sortBy === 'marriage_place'" class="sort-indicator">
                {{ sortOrder === 'asc' ? '↑' : '↓' }}
              </span>
            </th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="family in families" :key="family.id" class="family-row">
            <td class="family-name">{{ family.summary || 'N/A' }}</td>
            <td>
              <span v-if="family.husband_name">
                {{ getGenderIcon(family.husband_sex) }} {{ family.husband_name }}
              </span>
              <span v-else>N/A</span>
            </td>
            <td>
              <span v-if="family.wife_name">
                {{ getGenderIcon(family.wife_sex) }} {{ family.wife_name }}
              </span>
              <span v-else>N/A</span>
            </td>
            <td>{{ formatDate(family.marriage_date) }}</td>
            <td>{{ family.marriage_place || 'N/A' }}</td>
            <td class="actions-cell">
              <div class="action-buttons">
                <button 
                  @click="$emit('view-tree', family.id)" 
                  class="action-button view-button"
                  title="View Family Tree"
                >
                  🌳 View Tree
                </button>
                <button 
                  @click="$emit('download', family.id)" 
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
  </div>
</template>

<script setup lang="ts">
import type { FamilySearchResult } from '../../types/family'

interface Props {
  families: FamilySearchResult[]
  filteredCount: number
  totalCount: number
  sortBy: 'summary' | 'marriage_date' | 'marriage_place'
  sortOrder: 'asc' | 'desc'
}

defineProps<Props>()

defineEmits<{
  sort: [column: 'summary' | 'marriage_date' | 'marriage_place']
  refresh: []
  'view-tree': [familyId: string]
  download: [familyId: string]
}>()

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

const getGenderIcon = (sex?: 'M' | 'F' | 'U'): string => {
  switch (sex) {
    case 'M':
      return '👨'
    case 'F':
      return '👩'
    default:
      return '👤'
  }
}
</script>

<style scoped>
.data-grid-container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem 2rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.grid-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.25rem;
  font-weight: 600;
}

.grid-actions {
  display: flex;
  gap: 1rem;
}

.refresh-button {
  background: #27ae60;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.refresh-button:hover {
  background: #229954;
}

.data-grid {
  overflow-x: auto;
}

.families-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.families-table th {
  background: #f8f9fa;
  color: #495057;
  font-weight: 600;
  padding: 1rem;
  text-align: left;
  border-bottom: 2px solid #e9ecef;
  position: sticky;
  top: 0;
  z-index: 10;
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
  font-size: 0.8rem;
  color: #3498db;
}

.families-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.family-row:hover {
  background: #f8f9fa;
}

.family-name {
  font-weight: 600;
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
  padding: 0.4rem 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
  font-weight: 500;
  transition: all 0.2s;
}

.view-button {
  background: #3498db;
  color: white;
}

.view-button:hover {
  background: #2980b9;
  transform: translateY(-1px);
}

.download-button {
  background: #e67e22;
  color: white;
}

.download-button:hover {
  background: #d35400;
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .families-table {
    font-size: 0.8rem;
  }
  
  .families-table th,
  .families-table td {
    padding: 0.5rem;
  }
  
  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .action-button {
    font-size: 0.7rem;
    padding: 0.3rem 0.6rem;
  }
}
</style>

