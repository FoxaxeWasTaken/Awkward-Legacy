<template>
  <div class="family-search-view">
    <FamilySearch />
  </div>
</template>

<script setup lang="ts">
import FamilySearch from '../components/FamilySearch.vue';
</script>

<style scoped>
.family-search-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}
</style>
