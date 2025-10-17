<template>
  <div
    class="person-node"
    :class="nodeClasses"
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <div class="person-avatar">
      <div class="avatar-circle">
        <span class="gender-icon">{{ genderIcon }}</span>
      </div>
    </div>
    <div class="person-info">
      <div class="person-name">{{ fullName }}</div>
      <div class="person-dates" v-if="person.birth_date">{{ dateRange }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Person } from '../../types/family'
import { getGenderIcon } from '../../utils/familyUtils'
import { getDateRange } from '../../utils/dateUtils'

interface Props {
  person: Person
  type: 'husband' | 'wife'
  hasSpouse: boolean
  highlightClass: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [person: Person]
  mouseenter: [event: MouseEvent, person: Person]
  mouseleave: []
}>()

const fullName = computed(() => `${props.person.first_name} ${props.person.last_name}`)

const dateRange = computed(() => getDateRange(props.person.birth_date, props.person.death_date))

const genderIcon = computed(() => getGenderIcon(props.person.sex))

const nodeClasses = computed(() => [
  props.type,
  { 'has-spouse': props.hasSpouse },
  props.highlightClass,
])

const handleClick = () => {
  emit('click', props.person)
}

const handleMouseEnter = (event: MouseEvent) => {
  emit('mouseenter', event, props.person)
}

const handleMouseLeave = () => {
  emit('mouseleave')
}
</script>

<!-- CSS is now imported from external files -->
