<script setup lang="ts">
interface Props {
  scale: number
}

defineProps<Props>()

const emit = defineEmits<{
  zoomIn: []
  zoomOut: []
  resetZoom: []
}>()

const zoomIn = () => emit('zoomIn')
const zoomOut = () => emit('zoomOut')
const resetZoom = () => emit('resetZoom')
</script>

<template>
  <div class="tree-controls">
    <div class="zoom-info">
      <span class="zoom-label">{{ Math.round(scale * 100) }}%</span>
    </div>
    <button @click="zoomOut" class="control-button control-button-small" title="Zoom Out">−</button>
    <button @click="zoomIn" class="control-button control-button-small" title="Zoom In">+</button>
    <button @click="resetZoom" class="control-button control-button-small" title="Reset View">
      ⟲
    </button>
  </div>
</template>
