<template>
  <div class="family-tree-view">
    <FamilyTree :family-id="familyId" />
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router'
import FamilyTree from '../components/FamilyTree.vue'

const route = useRoute()
const familyId = route.params.id as string
</script>

<style scoped>
.family-tree-view {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
