<template>
  <div class="family-card" @click="handleViewDetails">
    <div class="family-header">
      <h4 class="family-title">{{ family.summary }}</h4>
      <div class="family-id">ID: {{ family.id.slice(0, 8) }}...</div>
    </div>
    
    <div class="family-details">
      <div v-if="family.husband_name" class="spouse-info">
        <span class="spouse-label">Husband:</span>
        <span class="spouse-name">{{ family.husband_name }}</span>
      </div>
      
      <div v-if="family.wife_name" class="spouse-info">
        <span class="spouse-label">Wife:</span>
        <span class="spouse-name">{{ family.wife_name }}</span>
      </div>
      
      <div v-if="family.marriage_date" class="marriage-info">
        <span class="marriage-label">Married:</span>
        <span class="marriage-date">{{ formatDate(family.marriage_date) }}</span>
      </div>
      
      <div v-if="family.marriage_place" class="marriage-info">
        <span class="marriage-label">Place:</span>
        <span class="marriage-place">{{ family.marriage_place }}</span>
      </div>
      
      <div class="children-info">
        <span class="children-label">Children:</span>
        <span class="children-count">{{ family.children_count }}</span>
      </div>
    </div>
    
    <div class="family-actions">
      <button class="view-button" @click.stop="handleViewDetails">
        View Family Tree
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FamilySearchResult } from '../types/family';

interface Props {
  family: FamilySearchResult;
}

const props = defineProps<Props>();

const emit = defineEmits<{
  viewDetails: [familyId: string];
}>();

const handleViewDetails = () => {
  emit('viewDetails', props.family.id);
};

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch (error) {
    return dateString;
  }
};
</script>

<style scoped>
.family-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.family-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-color: #3498db;
}

.family-header {
  margin-bottom: 1rem;
  border-bottom: 1px solid #f1f3f4;
  padding-bottom: 0.75rem;
}

.family-title {
  color: #2c3e50;
  margin: 0 0 0.25rem 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.family-id {
  font-size: 0.8rem;
  color: #7f8c8d;
  font-family: monospace;
}

.family-details {
  margin-bottom: 1rem;
}

.spouse-info,
.marriage-info,
.children-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  font-size: 0.9rem;
}

.spouse-label,
.marriage-label,
.children-label {
  color: #7f8c8d;
  font-weight: 500;
  min-width: 80px;
}

.spouse-name,
.marriage-date,
.marriage-place,
.children-count {
  color: #2c3e50;
  font-weight: 400;
}

.marriage-place {
  max-width: 150px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.family-actions {
  display: flex;
  justify-content: center;
}

.view-button {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.view-button:hover {
  background: #2980b9;
}

/* Responsive */
@media (max-width: 480px) {
  .family-card {
    padding: 1rem;
  }
  
  .spouse-info,
  .marriage-info,
  .children-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .spouse-label,
  .marriage-label,
  .children-label {
    min-width: auto;
  }
}
</style>
