<template>
  <div
    class="marriage-line"
    :class="marriageClasses"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  ></div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Couple } from '../../utils/familyUtils'

interface Props {
  couple: Couple
}

const props = defineProps<Props>()

const emit = defineEmits<{
  mouseenter: [event: MouseEvent, couple: Couple]
  mouseleave: []
}>()

const marriageClasses = computed(() => ({
  'marriage-line-married': props.couple.isMarried && !props.couple.isDivorced,
  'marriage-line-divorced': props.couple.isDivorced,
  'marriage-line-unknown': !props.couple.isMarried && !props.couple.isDivorced,
}))

const handleMouseEnter = (event: MouseEvent) => {
  emit('mouseenter', event, props.couple)
}

const handleMouseLeave = () => {
  emit('mouseleave')
}
</script>

<!-- CSS is now imported from external files -->
