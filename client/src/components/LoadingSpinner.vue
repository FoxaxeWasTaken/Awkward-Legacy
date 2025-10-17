<script setup lang="ts">
interface Props {
  message?: string
  fullscreen?: boolean
}

defineProps<Props>()
</script>

<template>
  <div class="loading-spinner" :class="{ fullscreen: fullscreen }">
    <div class="spinner"></div>
    <p v-if="message" class="loading-message">{{ message }}</p>
  </div>
</template>
