<template>
  <div class="family-tree">
    <div class="tree-header">
      <div class="header-left">
        <button @click="$router.push('/')" class="back-button">
          <span class="back-icon">←</span>
          Back to Search
        </button>
        <h2>{{ familyTitle }}</h2>
      </div>
      <TreeControls
        :scale="scale"
        @zoom-in="() => zoomIn(treeContainer)"
        @zoom-out="() => zoomOut(treeContainer)"
        @reset-zoom="resetZoom"
      />
    </div>

    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading family tree...</p>
    </div>

    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Error Loading Family Tree</h3>
      <p>{{ error }}</p>
      <button @click="loadFamilyData" class="retry-button">Retry</button>
    </div>

    <div
      v-else
      class="tree-container"
      ref="treeContainer"
      @mousedown="startDrag"
      @wheel="(e) => handleWheel(e, treeContainer)"
    >
      <div
        class="tree-content"
        ref="treeContent"
        :style="{
          transform: `translate(${panX}px, ${panY}px) scale(${scale})`,
          transformOrigin: '0 0',
          transition: isDragging ? 'none' : 'transform 0.3s ease',
        }"
      >
        <div
          class="family-generation"
          v-for="(generation, index) in familyGenerations"
          :key="index"
        >
          <div class="generation-label" v-if="index > 0">Generation {{ index + 1 }}</div>

          <!-- Marriage Information for the main couple -->
          <div v-if="index === 0 && generation.couples[0]" class="marriage-info">
            <div
              v-if="generation.couples[0].marriageDate || generation.couples[0].marriagePlace"
              class="marriage-details"
            >
              <div v-if="generation.couples[0].marriageDate" class="marriage-date">
                <strong>Married:</strong> {{ formatDate(generation.couples[0].marriageDate) }}
              </div>
              <div v-if="generation.couples[0].marriagePlace" class="marriage-place">
                <strong>Place:</strong> {{ generation.couples[0].marriagePlace }}
              </div>
            </div>
          </div>

          <!-- All couples of this generation on the same horizontal level -->
          <div class="couples-row">
            <div
              v-for="couple in generation.couples"
              :key="couple.id"
              class="couple-container"
              :class="{ 'has-children': couple.children.length > 0 }"
            >
              <!-- Spouses Row - Husband and Wife side by side -->
              <div class="spouses-row">
                <!-- Husband -->
                <PersonNode
                  v-if="couple.husband"
                  :person="couple.husband"
                  type="husband"
                  :has-spouse="!!couple.wife"
                  :highlight-class="getPersonHighlightClass(couple.husband)"
                  @click="selectPersonWithHighlights"
                  @mouseenter="handlePersonHoverAndShowTooltip"
                  @mouseleave="handlePersonLeaveAndHideTooltip"
                />

                <!-- Marriage/Divorce Line -->
                <MarriageLine
                  v-if="couple.husband && couple.wife"
                  :couple="couple"
                  @mouseenter="showMarriageTooltip"
                  @mouseleave="hideMarriageTooltip"
                />

                <!-- Wife -->
                <PersonNode
                  v-if="couple.wife"
                  :person="couple.wife"
                  type="wife"
                  :has-spouse="!!couple.husband"
                  :highlight-class="getPersonHighlightClass(couple.wife)"
                  @click="selectPersonWithHighlights"
                  @mouseenter="handlePersonHoverAndShowTooltip"
                  @mouseleave="handlePersonLeaveAndHideTooltip"
                />
              </div>
            </div>
          </div>

          <!-- All children of this generation below their parents -->
          <div
            v-if="generation.couples.some((c) => c.children.length > 0)"
            class="generation-children-row children-row"
          >
            <div
              v-for="couple in generation.couples"
              :key="`children-${couple.id}`"
              class="children-group"
            >
              <div v-if="couple.children.length > 0" class="children-wrapper">
                <div class="children-connection">
                  <div class="connection-line"></div>
                </div>
                <div class="children-container">
                  <ChildNode
                    v-for="child in couple.children"
                    :key="child.id"
                    :child="child"
                    :highlight-class="getPersonHighlightClass(child)"
                    @click="selectPersonWithHighlights"
                    @mouseenter="handlePersonHoverAndShowTooltip"
                    @mouseleave="handlePersonLeaveAndHideTooltip"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tooltips -->
    <PersonTooltip
      :visible="tooltip.visible"
      :x="tooltip.x"
      :y="tooltip.y"
      :person="tooltip.person"
    />

    <MarriageTooltip
      :visible="marriageTooltip.visible"
      :x="marriageTooltip.x"
      :y="marriageTooltip.y"
      :couple="marriageTooltip.couple"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed, toRef } from 'vue'
import type { Person } from '../types/family'
import { useFamilyTree } from '../composables/useFamilyTree'
import { useTreeNavigation } from '../composables/useTreeNavigation'
import { usePersonHighlighting } from '../composables/usePersonHighlighting'
import { useTooltips } from '../composables/useTooltips'
import { createFamilyGenerations } from '../utils/familyUtils'
import { formatDate } from '../utils/dateUtils'
import TreeControls from './tree/TreeControls.vue'
import PersonNode from './tree/PersonNode.vue'
import ChildNode from './tree/ChildNode.vue'
import MarriageLine from './tree/MarriageLine.vue'
import PersonTooltip from './tree/PersonTooltip.vue'
import MarriageTooltip from './tree/MarriageTooltip.vue'

interface Props {
  familyId: string
}

const props = defineProps<Props>()

// Template refs
const treeContainer = ref<HTMLElement>()
const treeContent = ref<HTMLElement>()

// Use composables
const { isLoading, error, familyData, familyTitle, crossFamilyChildren, loadFamilyData } =
  useFamilyTree(toRef(props, 'familyId'))
const {
  panX,
  panY,
  scale,
  isDragging,
  startDrag,
  handleDrag,
  stopDrag,
  handleWheel,
  zoomIn,
  zoomOut,
  resetZoom,
  fitTreeToView,
} = useTreeNavigation()
const {
  selectPerson,
  handlePersonHover,
  handlePersonLeave,
  updateHighlights,
  getPersonHighlightClass,
  clickedPerson,
} = usePersonHighlighting()
const {
  tooltip,
  marriageTooltip,
  showTooltip,
  hideTooltip,
  showMarriageTooltip,
  hideMarriageTooltip,
} = useTooltips()

// Computed property for family generations
const familyGenerations = computed(() => {
  if (!familyData.value) return []
  return createFamilyGenerations(familyData.value, crossFamilyChildren.value)
})

// Event handlers that combine multiple composable functions
const handlePersonHoverAndShowTooltip = (event: MouseEvent, person: Person) => {
  // Only apply hover effects if no one is currently clicked/selected
  if (!clickedPerson.value) {
    handlePersonHover(person)
    if (familyData.value) {
      updateHighlights(person, familyData.value, familyGenerations.value, crossFamilyChildren.value)
    }
  }
  // Always show tooltip on hover, regardless of selection state
  showTooltip(event, person)
}

const handlePersonLeaveAndHideTooltip = () => {
  // Only clear hover effects if no one is currently clicked/selected
  if (!clickedPerson.value) {
    handlePersonLeave()
  }
  hideTooltip()
}

// Enhanced selectPerson that updates highlights with family data
const selectPersonWithHighlights = (person: Person) => {
  selectPerson(person)
  if (familyData.value) {
    updateHighlights(person, familyData.value, familyGenerations.value, crossFamilyChildren.value)
  }
}

// Enhanced loadFamilyData that fits tree to view
const loadFamilyDataAndFit = async () => {
  await loadFamilyData()
  // Fit tree to view after data is loaded
  await nextTick()
  setTimeout(() => {
    fitTreeToView(treeContainer.value, treeContent.value)
  }, 100) // Small delay to ensure DOM is fully rendered
}

// Lifecycle
onMounted(() => {
  loadFamilyDataAndFit()

  // Add global mouse event listeners for drag
  window.addEventListener('mousemove', handleDrag)
  window.addEventListener('mouseup', stopDrag)
})

onUnmounted(() => {
  // Clean up event listeners
  window.removeEventListener('mousemove', handleDrag)
  window.removeEventListener('mouseup', stopDrag)
})

// Family ID changes are now handled by the useFamilyTree composable
</script>

<!-- CSS is now imported from external files -->
