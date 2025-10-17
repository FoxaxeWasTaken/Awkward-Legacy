<template>
  <div v-if="visible" class="person-tooltip" :style="{ left: x + 'px', top: y + 'px' }">
    <div class="tooltip-content">
      <div class="tooltip-name">{{ person?.first_name }} {{ person?.last_name }}</div>
      <div class="tooltip-details">
        <div v-if="person?.sex">
          <strong>Gender:</strong>
          {{ person.sex === 'M' ? 'Male' : person.sex === 'F' ? 'Female' : 'Unknown' }}
        </div>
        <div v-if="person?.birth_date">
          <strong>Born:</strong> {{ formatDate(person.birth_date) }}
        </div>
        <div v-if="person?.birth_place"><strong>Birth Place:</strong> {{ person.birth_place }}</div>
        <div v-if="person?.death_date">
          <strong>Died:</strong> {{ formatDate(person.death_date) }}
        </div>
        <div v-if="person?.death_place"><strong>Death Place:</strong> {{ person.death_place }}</div>
        <div v-if="person?.occupation"><strong>Occupation:</strong> {{ person.occupation }}</div>
        <div v-if="person?.notes"><strong>Notes:</strong> {{ person.notes }}</div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Person } from '../../types/family'
import { formatDate } from '../../utils/dateUtils'

interface Props {
  visible: boolean
  x: number
  y: number
  person: Person | null
}

defineProps<Props>()
</script>

<!-- CSS is now imported from external files -->
