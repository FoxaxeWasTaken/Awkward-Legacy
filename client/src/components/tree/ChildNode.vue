<script setup lang="ts">
import { computed } from 'vue'
import type { Person } from '../../types/family'
import { getChildGenderIcon } from '../../utils/familyUtils'
import { getDateRange } from '../../utils/dateUtils'

interface Props {
  child: Person
  highlightClass: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [person: Person]
  mouseenter: [event: MouseEvent, person: Person]
  mouseleave: []
}>()

const fullName = computed(() => {
  const firstName = props.child.first_name || ''
  const lastName = props.child.last_name || ''
  const name = `${firstName} ${lastName}`.trim()
  return name || 'Unknown'
})

const dateRange = computed(() => getDateRange(props.child.birth_date, props.child.death_date))

const genderIcon = computed(() => getChildGenderIcon(props.child.sex))

const handleClick = () => {
  emit('click', props.child)
}

const handleMouseEnter = (event: MouseEvent) => {
  emit('mouseenter', event, props.child)
}

const handleMouseLeave = () => {
  emit('mouseleave')
}
</script>

<template>
  <div
    class="child-node person-node child"
    :class="highlightClass"
    @click="handleClick"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
    <div class="child-avatar">
      <div class="avatar-circle">
        <span class="gender-icon">{{ genderIcon }}</span>
      </div>
    </div>
    <div class="child-info">
      <div class="child-name">{{ fullName }}</div>
      <div class="child-dates" v-if="child.birth_date">{{ dateRange }}</div>
    </div>
  </div>
</template>
