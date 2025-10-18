<script setup lang="ts">
import { useRoute } from 'vue-router'
import FamilyTree from '../components/FamilyTree.vue'

const route = useRoute()
const familyId = route.params.id as string
</script>

<template>
  <div class="family-tree-view">
    <FamilyTree :family-id="familyId" />
  </div>
</template>

<style scoped>
.family-tree-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
