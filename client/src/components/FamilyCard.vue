<script setup lang="ts">
import type { FamilySearchResult } from '../types/family'

interface Props {
  family: FamilySearchResult
}

const props = defineProps<Props>()

const emit = defineEmits<{
  viewDetails: [familyId: string]
}>()

const handleViewDetails = () => {
  emit('viewDetails', props.family.id)
}

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    })
  } catch (_error) {
    return dateString
  }
}
</script>

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
        <span class="children-count">{{ family.children_count }} children</span>
      </div>
    </div>

    <div class="family-actions">
      <button class="view-button" @click.stop="handleViewDetails">View Details</button>
    </div>
  </div>
</template>
