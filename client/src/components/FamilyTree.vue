<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, computed, toRef } from 'vue'
import type { Person } from '../types/family'
import { useFamilyTree } from '../composables/useFamilyTree'
import { useTreeNavigation } from '../composables/useTreeNavigation'
import { usePersonHighlighting } from '../composables/usePersonHighlighting'
import { useTooltips } from '../composables/useTooltips'
import { createFamilyGenerations } from '../utils/familyUtils'
import { formatDate } from '../utils/dateUtils'
import apiService from '../services/api'
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

const treeContainer = ref<HTMLElement>()
const treeContent = ref<HTMLElement>()
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

const familyGenerations = computed(() => {
  if (!familyData.value) return []
  return createFamilyGenerations(familyData.value, crossFamilyChildren.value)
})
const handlePersonHoverAndShowTooltip = (event: MouseEvent, person: Person) => {
  if (!clickedPerson.value) {
    handlePersonHover(person)
    if (familyData.value) {
      updateHighlights(person, familyData.value, familyGenerations.value, crossFamilyChildren.value)
    }
  }
  showTooltip(event, person)
}

const handlePersonLeaveAndHideTooltip = () => {
  if (!clickedPerson.value) {
    handlePersonLeave()
  }
  hideTooltip()
}

const selectPersonWithHighlights = (person: Person) => {
  selectPerson(person)
  if (familyData.value) {
    updateHighlights(person, familyData.value, familyGenerations.value, crossFamilyChildren.value)
  }
}

const loadFamilyDataAndFit = async () => {
  try {
    await loadFamilyData()
    await nextTick()
    // Don't auto-fit to view - start with normal scale
    // setTimeout(() => {
    //   fitTreeToView(treeContainer.value, treeContent.value)
    // }, 100)
  } catch (error) {
    console.error('Error loading family data:', error)
  }
}

const isDownloading = ref(false)

const downloadFamilyData = async () => {
  try {
    isDownloading.value = true
    const blob = await apiService.downloadFamilyFile(props.familyId)
    
    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `family-${props.familyId}-${new Date().toISOString().split('T')[0]}.gw`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error downloading family data:', error)
    alert('Failed to download family data. Please try again.')
  } finally {
    isDownloading.value = false
  }
}
onMounted(() => {
  loadFamilyDataAndFit()
  globalThis.addEventListener('mousemove', handleDrag)
  globalThis.addEventListener('mouseup', stopDrag)
})

onUnmounted(() => {
  globalThis.removeEventListener('mousemove', handleDrag)
  globalThis.removeEventListener('mouseup', stopDrag)
})
</script>

<template>
  <div class="family-tree">
    <div class="tree-header">
      <button @click="$router.push('/manage')" class="back-button">
        <span class="back-icon">←</span>
        Back to Family Management
      </button>
      <h2>{{ familyTitle }}</h2>
      <div class="header-controls">
        <button 
          @click="downloadFamilyData" 
          :disabled="isDownloading"
          class="download-family-btn"
          title="Download this family as .gw file"
        >
          <span v-if="isDownloading">⏳</span>
          <span v-else>📥</span>
          {{ isDownloading ? 'Downloading...' : 'Download Family' }}
        </button>
        <TreeControls
          :scale="scale"
          @zoom-in="() => zoomIn(treeContainer)"
          @zoom-out="() => zoomOut(treeContainer)"
          @reset-zoom="resetZoom"
        />
      </div>
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

          <div class="couples-row">
            <div
              v-for="couple in generation.couples"
              :key="couple.id"
              class="couple-container"
              :class="{ 'has-children': couple.children.length > 0 }"
            >
              <div class="spouses-row">
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

                <MarriageLine
                  v-if="couple.husband && couple.wife"
                  :couple="couple"
                  @mouseenter="showMarriageTooltip"
                  @mouseleave="hideMarriageTooltip"
                />

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

<style scoped>
.family-tree {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
}

.tree-header {
  background: white;
  border-bottom: 1px solid #e9ecef;
  padding: 1rem 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
  min-height: 4rem;
}

.back-button {
  background: rgba(255, 255, 255, 0.9);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #2c3e50;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.back-button:hover {
  background: white;
  transform: translateY(-1px);
}

.back-icon {
  font-size: 1.1rem;
  font-weight: bold;
}

.tree-header h2 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50 !important;
  text-align: center;
  line-height: 1.2;
  flex: 1;
  padding: 0 2rem; /* Add some padding but not too much */
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.download-family-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.download-family-btn:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 123, 255, 0.3);
}

.download-family-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 2rem;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #007bff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-button {
  background: #007bff;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  margin-top: 1rem;
  transition: background-color 0.2s ease;
}

.retry-button:hover {
  background: #0056b3;
}

.tree-container {
  flex: 1;
  overflow: hidden;
  position: relative;
  background: #f8f9fa;
  cursor: grab;
}

.tree-container:active {
  cursor: grabbing;
}

.tree-content {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  min-width: 100%;
  min-height: 100%;
}

/* Responsive */
@media (max-width: 768px) {
  .tree-header {
    padding: 0.75rem 1rem;
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .back-button {
    align-self: flex-start;
    margin-bottom: 0.5rem;
  }

  .header-controls {
    justify-content: center;
    order: 3;
  }

  .tree-header h2 {
    font-size: 1.25rem;
    padding: 0;
    order: 2;
  }

  .download-family-btn {
    padding: 0.5rem 1rem;
    font-size: 0.8rem;
  }
}
</style>
