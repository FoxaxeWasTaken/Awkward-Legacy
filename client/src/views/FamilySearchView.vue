<script setup lang="ts">
import FamilySearch from '../components/FamilySearch.vue'
</script>

<template>
  <div class="family-search-view">
    <FamilySearch />
  </div>
</template>

<style scoped>
.family-search-view {
  height: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  overflow: auto;
}
</style>
