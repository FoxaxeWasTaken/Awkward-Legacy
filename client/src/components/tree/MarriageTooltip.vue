<script setup lang="ts">
import type { Couple } from '../../utils/familyUtils'
import { formatDate } from '../../utils/dateUtils'

interface Props {
  visible: boolean
  x: number
  y: number
  couple: Couple | null
}

defineProps<Props>()
</script>

<template>
  <div v-if="visible" class="marriage-tooltip" :style="{ left: x + 'px', top: y + 'px' }">
    <div class="tooltip-content">
      <div class="tooltip-name">
        {{ couple?.husband?.first_name }}
        {{ couple?.husband?.last_name }} &
        {{ couple?.wife?.first_name }}
        {{ couple?.wife?.last_name }}
      </div>
      <div class="tooltip-details">
        <div v-if="couple?.isMarried && !couple?.isDivorced" class="relationship-status married">
          <strong>Status:</strong> Married 💒
        </div>
        <div v-else-if="couple?.isDivorced" class="relationship-status divorced">
          <strong>Status:</strong> Divorced 💔
        </div>
        <div v-else class="relationship-status unknown">
          <strong>Status:</strong> Relationship Unknown ❓
        </div>

        <div v-if="couple?.marriageDate">
          <strong>Married:</strong> {{ formatDate(couple.marriageDate) }}
        </div>
        <div v-if="couple?.marriagePlace">
          <strong>Marriage Place:</strong> {{ couple.marriagePlace }}
        </div>

        <div v-if="couple?.divorceDate">
          <strong>Divorced:</strong> {{ formatDate(couple.divorceDate) }}
        </div>
        <div v-if="couple?.divorcePlace">
          <strong>Divorce Place:</strong> {{ couple.divorcePlace }}
        </div>

        <div v-if="couple?.events && couple.events.length > 0">
          <strong>Events:</strong>
          <ul class="events-list">
            <li v-for="event in couple.events" :key="event.id">
              {{ event.type }}
              <span v-if="event.date"> - {{ formatDate(event.date) }}</span>
              <span v-if="event.place"> in {{ event.place }}</span>
              <span v-if="event.description">: {{ event.description }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
