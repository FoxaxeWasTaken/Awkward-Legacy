<template>
  <div v-if="totalPages > 1" class="pagination">
    <button 
      @click="$emit('go-to-page', currentPage - 1)"
      :disabled="currentPage === 1"
      class="pagination-button"
    >
      Previous
    </button>
    
    <div class="pagination-pages">
      <button
        v-for="page in Math.min(5, totalPages)"
        :key="page"
        @click="$emit('go-to-page', page)"
        :class="{ active: page === currentPage }"
        class="pagination-page"
      >
        {{ page }}
      </button>
      <span v-if="totalPages > 5" class="pagination-ellipsis">...</span>
      <button
        v-if="totalPages > 5"
        @click="$emit('go-to-page', totalPages)"
        :class="{ active: currentPage === totalPages }"
        class="pagination-page"
      >
        {{ totalPages }}
      </button>
    </div>
    
    <button 
      @click="$emit('go-to-page', currentPage + 1)"
      :disabled="currentPage === totalPages"
      class="pagination-button"
    >
      Next
    </button>
  </div>
</template>

<script setup lang="ts">
interface Props {
  currentPage: number
  totalPages: number
}

defineProps<Props>()

defineEmits<{
  'go-to-page': [page: number]
}>()
</script>

<style scoped>
.pagination {
  max-width: 1200px;
  margin: 2rem auto 0;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.pagination-pages {
  display: flex;
  gap: 0.5rem;
}

.pagination-button {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e9ecef;
  background: white;
  color: #495057;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.pagination-button:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #3498db;
  color: #3498db;
}

.pagination-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-page {
  padding: 0.5rem 0.75rem;
  border: 1px solid #e9ecef;
  background: white;
  color: #495057;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.pagination-page:hover {
  background: #f8f9fa;
  border-color: #3498db;
  color: #3498db;
}

.pagination-page.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.pagination-page.active:hover {
  background: #2980b9;
  border-color: #2980b9;
}

.pagination-ellipsis {
  padding: 0.5rem;
  color: #6c757d;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .pagination {
    flex-direction: column;
    gap: 1rem;
  }

  .pagination-pages {
    flex-wrap: wrap;
    justify-content: center;
  }
}
</style>

