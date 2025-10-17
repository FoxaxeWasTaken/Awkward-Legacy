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
      <div class="tree-controls">
        <div class="zoom-info">
          <span class="zoom-label">{{ Math.round(scale * 100) }}%</span>
        </div>
        <button @click="zoomOut" class="control-button control-button-small" title="Zoom Out">
          −
        </button>
        <button @click="zoomIn" class="control-button control-button-small" title="Zoom In">
          +
        </button>
        <button @click="resetZoom" class="control-button control-button-small" title="Reset View">
          ⟲
        </button>
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
      @wheel="handleWheel"
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
                <div
                  v-if="couple.husband"
                  class="person-node husband"
                  :class="[{ 'has-spouse': couple.wife }, getPersonHighlightClass(couple.husband)]"
                  @click="selectPerson(couple.husband)"
                  @mouseenter="handlePersonHoverAndShowTooltip($event, couple.husband)"
                  @mouseleave="handlePersonLeaveAndHideTooltip()"
                >
                  <div class="person-avatar">
                    <div class="avatar-circle">
                      <span class="gender-icon">👨</span>
                    </div>
                  </div>
                  <div class="person-info">
                    <div class="person-name">
                      {{ couple.husband.first_name }} {{ couple.husband.last_name }}
                    </div>
                    <div class="person-dates" v-if="couple.husband.birth_date">
                      {{ formatDate(couple.husband.birth_date) }} -
                      {{
                        couple.husband.death_date
                          ? formatDate(couple.husband.death_date)
                          : 'Present'
                      }}
                    </div>
                  </div>
                </div>

                <!-- Marriage/Divorce Line -->
                <div
                  class="marriage-line"
                  :class="{
                    'marriage-line-married': couple.isMarried && !couple.isDivorced,
                    'marriage-line-divorced': couple.isDivorced,
                    'marriage-line-unknown': !couple.isMarried && !couple.isDivorced,
                  }"
                  v-if="couple.husband && couple.wife"
                  @mouseenter="showMarriageTooltip($event, couple)"
                  @mouseleave="hideMarriageTooltip()"
                ></div>

                <!-- Wife -->
                <div
                  v-if="couple.wife"
                  class="person-node wife"
                  :class="[{ 'has-spouse': couple.husband }, getPersonHighlightClass(couple.wife)]"
                  @click="selectPerson(couple.wife)"
                  @mouseenter="handlePersonHoverAndShowTooltip($event, couple.wife)"
                  @mouseleave="handlePersonLeaveAndHideTooltip()"
                >
                  <div class="person-avatar">
                    <div class="avatar-circle">
                      <span class="gender-icon">👩</span>
                    </div>
                  </div>
                  <div class="person-info">
                    <div class="person-name">
                      {{ couple.wife.first_name }} {{ couple.wife.last_name }}
                    </div>
                    <div class="person-dates" v-if="couple.wife.birth_date">
                      {{ formatDate(couple.wife.birth_date) }} -
                      {{ couple.wife.death_date ? formatDate(couple.wife.death_date) : 'Present' }}
                    </div>
                  </div>
                </div>
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
                  <div
                    v-for="child in couple.children"
                    :key="child.id"
                    class="child-node person-node child"
                    :class="getPersonHighlightClass(child)"
                    @click="selectPerson(child)"
                    @mouseenter="handlePersonHoverAndShowTooltip($event, child)"
                    @mouseleave="handlePersonLeaveAndHideTooltip()"
                  >
                    <div class="child-avatar">
                      <div class="avatar-circle">
                        <span class="gender-icon">{{ child.sex === 'M' ? '👦' : '👧' }}</span>
                      </div>
                    </div>
                    <div class="child-info">
                      <div class="child-name">{{ child.first_name }} {{ child.last_name }}</div>
                      <div class="child-dates" v-if="child.birth_date">
                        {{ formatDate(child.birth_date) }} -
                        {{ child.death_date ? formatDate(child.death_date) : 'Present' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tooltip -->
    <div
      v-if="tooltip.visible"
      class="person-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div class="tooltip-content">
        <div class="tooltip-name">
          {{ tooltip.person?.first_name }} {{ tooltip.person?.last_name }}
        </div>
        <div class="tooltip-details">
          <div v-if="tooltip.person?.sex">
            <strong>Gender:</strong>
            {{
              tooltip.person.sex === 'M'
                ? 'Male'
                : tooltip.person.sex === 'F'
                  ? 'Female'
                  : 'Unknown'
            }}
          </div>
          <div v-if="tooltip.person?.birth_date">
            <strong>Born:</strong> {{ formatDate(tooltip.person.birth_date) }}
          </div>
          <div v-if="tooltip.person?.birth_place">
            <strong>Birth Place:</strong> {{ tooltip.person.birth_place }}
          </div>
          <div v-if="tooltip.person?.death_date">
            <strong>Died:</strong> {{ formatDate(tooltip.person.death_date) }}
          </div>
          <div v-if="tooltip.person?.death_place">
            <strong>Death Place:</strong> {{ tooltip.person.death_place }}
          </div>
          <div v-if="tooltip.person?.occupation">
            <strong>Occupation:</strong> {{ tooltip.person.occupation }}
          </div>
          <div v-if="tooltip.person?.notes"><strong>Notes:</strong> {{ tooltip.person.notes }}</div>
        </div>
      </div>
    </div>

    <!-- Marriage Tooltip -->
    <div
      v-if="marriageTooltip.visible"
      class="marriage-tooltip"
      :style="{ left: marriageTooltip.x + 'px', top: marriageTooltip.y + 'px' }"
    >
      <div class="tooltip-content">
        <div class="tooltip-name">
          {{ marriageTooltip.couple?.husband?.first_name }}
          {{ marriageTooltip.couple?.husband?.last_name }} &
          {{ marriageTooltip.couple?.wife?.first_name }}
          {{ marriageTooltip.couple?.wife?.last_name }}
        </div>
        <div class="tooltip-details">
          <div
            v-if="marriageTooltip.couple?.isMarried && !marriageTooltip.couple?.isDivorced"
            class="relationship-status married"
          >
            <strong>Status:</strong> Married 💒
          </div>
          <div v-else-if="marriageTooltip.couple?.isDivorced" class="relationship-status divorced">
            <strong>Status:</strong> Divorced 💔
          </div>
          <div v-else class="relationship-status unknown">
            <strong>Status:</strong> Relationship Unknown ❓
          </div>

          <div v-if="marriageTooltip.couple?.marriageDate">
            <strong>Married:</strong> {{ formatDate(marriageTooltip.couple.marriageDate) }}
          </div>
          <div v-if="marriageTooltip.couple?.marriagePlace">
            <strong>Marriage Place:</strong> {{ marriageTooltip.couple.marriagePlace }}
          </div>

          <div v-if="marriageTooltip.couple?.divorceDate">
            <strong>Divorced:</strong> {{ formatDate(marriageTooltip.couple.divorceDate) }}
          </div>
          <div v-if="marriageTooltip.couple?.divorcePlace">
            <strong>Divorce Place:</strong> {{ marriageTooltip.couple.divorcePlace }}
          </div>

          <div v-if="marriageTooltip.couple?.events && marriageTooltip.couple.events.length > 0">
            <strong>Events:</strong>
            <ul class="events-list">
              <li v-for="event in marriageTooltip.couple.events" :key="event.id">
                {{ event.type }}
                <span v-if="event.date"> - {{ formatDate(event.date) }}</span>
                <span v-if="event.place"> in {{ event.place }}</span>
                <span v-if="event.description">: {{ event.description }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import apiService from '../services/api'
import type { FamilyDetailResult, Person, Event } from '../types/family'

interface Props {
  familyId: string
}

interface Couple {
  id: string
  husband?: Person
  wife?: Person
  children: Person[]
  marriageDate?: string
  marriagePlace?: string
  events: Event[]
  isMarried: boolean
  isDivorced: boolean
  divorceDate?: string
  divorcePlace?: string
}

interface FamilyGeneration {
  couples: Couple[]
}

const props = defineProps<Props>()

// Reactive state
const isLoading = ref(true)
const error = ref('')
const familyData = ref<FamilyDetailResult | null>(null)
const familyTitle = ref('Family Tree')
const selectedPerson = ref<Person | null>(null)
const crossFamilyChildren = ref<Map<string, Person[]>>(new Map())

// Template refs
const treeContainer = ref<HTMLElement>()
const treeContent = ref<HTMLElement>()

// Tooltip state
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  person: null as Person | null,
})

// Marriage tooltip state
const marriageTooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  couple: null as Couple | null,
})

// Highlight state
const hoveredPerson = ref<Person | null>(null)
const clickedPerson = ref<Person | null>(null)
const highlightedParents = ref<Set<string>>(new Set())
const highlightedChildren = ref<Set<string>>(new Set())
const highlightedSpouse = ref<string | null>(null)

// Pan and zoom state
const panX = ref(0)
const panY = ref(0)
const scale = ref(1)
const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })
const panStart = ref({ x: 0, y: 0 })

// Computed property for family generations
const familyGenerations = computed((): FamilyGeneration[] => {
  if (!familyData.value) return []

  const data = familyData.value
  const generations: FamilyGeneration[] = []

  // Analyze relationship events for the main couple
  const relationshipAnalysis = analyzeRelationshipEvents(data.events, data.marriage_date)

  // Create the main couple (current family)
  const mainCouple: Couple = {
    id: data.id,
    husband: data.husband || undefined,
    wife: data.wife || undefined,
    children: data.children.map((child) => child.person).filter(Boolean) as Person[],
    marriageDate: data.marriage_date,
    marriagePlace: data.marriage_place,
    events: data.events,
    isMarried: relationshipAnalysis.isMarried,
    isDivorced: relationshipAnalysis.isDivorced,
    divorceDate: relationshipAnalysis.divorceDate,
    divorcePlace: relationshipAnalysis.divorcePlace,
  }

  // Add main couple to first generation
  generations.push({
    couples: [mainCouple],
  })

  // Recursively process all generations
  let currentGenCouples = [mainCouple]

  while (currentGenCouples.length > 0) {
    const nextGenCouples: Couple[] = []

    // For each couple in the current generation, find their children who have families
    currentGenCouples.forEach((couple) => {
      const coupleChildren = couple.children

      coupleChildren.forEach((child) => {
        if (child.has_own_family && child.own_families) {
          child.own_families.forEach((ownFamily) => {
            const childFamilyData = crossFamilyChildren.value.get(ownFamily.id)

            if (ownFamily.spouse || childFamilyData) {
              // For child couples, we need to fetch their events
              // Analyze relationship events for the child couple
              const childRelationshipAnalysis = analyzeRelationshipEvents(
                ownFamily.events || [],
                ownFamily.marriage_date,
              )

              const childCouple: Couple = {
                id: ownFamily.id,
                husband: child.sex === 'M' ? child : undefined,
                wife: child.sex === 'F' ? child : undefined,
                children: childFamilyData || [],
                marriageDate: ownFamily.marriage_date,
                marriagePlace: ownFamily.marriage_place,
                events: ownFamily.events || [],
                isMarried: childRelationshipAnalysis.isMarried,
                isDivorced: childRelationshipAnalysis.isDivorced,
                divorceDate: childRelationshipAnalysis.divorceDate,
                divorcePlace: childRelationshipAnalysis.divorcePlace,
              }

              // Add spouse
              if (ownFamily.spouse) {
                if (child.sex === 'M') {
                  childCouple.wife = {
                    id: ownFamily.spouse.id,
                    first_name: ownFamily.spouse.name.split(' ')[0],
                    last_name: ownFamily.spouse.name.split(' ').slice(1).join(' '),
                    sex: ownFamily.spouse.sex,
                    has_own_family: false,
                  }
                } else {
                  childCouple.husband = {
                    id: ownFamily.spouse.id,
                    first_name: ownFamily.spouse.name.split(' ')[0],
                    last_name: ownFamily.spouse.name.split(' ').slice(1).join(' '),
                    sex: ownFamily.spouse.sex,
                    has_own_family: false,
                  }
                }
              }

              nextGenCouples.push(childCouple)
            }
          })
        }
      })
    })

    // Add next generation if it exists
    if (nextGenCouples.length > 0) {
      generations.push({
        couples: nextGenCouples,
      })
      currentGenCouples = nextGenCouples
    } else {
      break
    }
  }

  return generations
})

// Helper function to analyze events and determine relationship status
const analyzeRelationshipEvents = (events: Event[], marriageDate?: string) => {
  const marriageEvents = events.filter(
    (event) =>
      (event.type && event.type.toLowerCase().includes('marriage')) ||
      (event.type && event.type.toLowerCase().includes('wedding')) ||
      (event.type && event.type.toLowerCase().includes('marry')),
  )

  const divorceEvents = events.filter(
    (event) =>
      (event.type && event.type.toLowerCase().includes('divorce')) ||
      (event.type && event.type.toLowerCase().includes('separation')) ||
      (event.type && event.type.toLowerCase().includes('annulment')),
  )

  // Consider a couple married if they have marriage events OR a marriage date
  const isMarried = marriageEvents.length > 0 || !!marriageDate
  const isDivorced = divorceEvents.length > 0

  // Get the most recent divorce event
  const latestDivorce = divorceEvents.sort((a, b) => {
    if (!a.date || !b.date) return 0
    return new Date(b.date).getTime() - new Date(a.date).getTime()
  })[0]

  return {
    isMarried,
    isDivorced,
    divorceDate: latestDivorce?.date,
    divorcePlace: latestDivorce?.place,
    marriageEvents,
    divorceEvents,
  }
}

// Methods
const loadFamilyData = async () => {
  isLoading.value = true
  error.value = ''

  try {
    const data = await apiService.getFamilyDetail(props.familyId)

    if (!data) {
      throw new Error('No family data received')
    }

    familyData.value = data

    // Create family title
    const parts = []
    if (data.husband) {
      parts.push(`${data.husband.first_name} ${data.husband.last_name}`)
    }
    if (data.wife) {
      parts.push(`${data.wife.first_name} ${data.wife.last_name}`)
    }
    familyTitle.value = parts.length > 0 ? parts.join(' & ') : 'Family Tree'

    // Fetch children data for cross-family relationships
    await loadCrossFamilyChildren(data)

    // Fit tree to view after data is loaded
    await nextTick()
    setTimeout(() => {
      fitTreeToView()
    }, 100) // Small delay to ensure DOM is fully rendered
  } catch (err: unknown) {
    console.error('Error loading family data:', err)
    const errorMessage =
      err && typeof err === 'object' && 'response' in err
        ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
        : 'Failed to load family tree. Please try again.'
    error.value = errorMessage || 'Failed to load family tree. Please try again.'
  } finally {
    isLoading.value = false
  }
}

const loadCrossFamilyChildren = async (data: FamilyDetailResult) => {
  const childrenMap = new Map<string, Person[]>()
  const processedFamilies = new Set<string>([data.id]) // Track processed families to avoid infinite loops

  // Recursive function to load all descendant families
  const loadDescendantFamilies = async (children: Person[]) => {
    for (const child of children) {
      if (child.has_own_family && child.own_families) {
        for (const ownFamily of child.own_families) {
          // Skip if already processed
          if (processedFamilies.has(ownFamily.id)) continue
          processedFamilies.add(ownFamily.id)

          try {
            const familyDetail = await apiService.getFamilyDetail(ownFamily.id)
            const familyChildren = familyDetail.children
              .map((c) => c.person)
              .filter(Boolean) as Person[]
            childrenMap.set(ownFamily.id, familyChildren)

            // Recursively load grandchildren families
            if (familyChildren.length > 0) {
              await loadDescendantFamilies(familyChildren)
            }
          } catch (err) {
            console.error(`Error loading children for family ${ownFamily.id}:`, err)
          }
        }
      }
    }
  }

  // Start loading from the root family's children
  const rootChildren = data.children.map((c) => c.person).filter(Boolean) as Person[]
  await loadDescendantFamilies(rootChildren)

  crossFamilyChildren.value = childrenMap
}

const selectPerson = (person: Person) => {
  // Toggle off if clicking the same person
  if (clickedPerson.value?.id === person.id) {
    clickedPerson.value = null
    clearHighlights()
  } else {
    clickedPerson.value = person
    selectedPerson.value = person
    updateHighlights(person)
  }
}

const handlePersonHover = (person: Person) => {
  if (!clickedPerson.value) {
    hoveredPerson.value = person
    updateHighlights(person)
  }
}

const handlePersonHoverAndShowTooltip = (event: MouseEvent, person: Person) => {
  handlePersonHover(person)
  showTooltip(event, person)
}

const handlePersonLeaveAndHideTooltip = () => {
  handlePersonLeave()
  hideTooltip()
}

const handlePersonLeave = () => {
  if (!clickedPerson.value) {
    hoveredPerson.value = null
    clearHighlights()
  }
}

const clearHighlights = () => {
  highlightedParents.value = new Set()
  highlightedChildren.value = new Set()
  highlightedSpouse.value = null
}

const updateHighlights = (person: Person) => {
  clearHighlights()

  if (!familyData.value) return

  const parents = new Set<string>()
  const children = new Set<string>()
  let spouse: string | null = null

  // Find parents (check if person is a child in the main family or any sub-family)
  const findParents = (data: FamilyDetailResult) => {
    data.children.forEach((child) => {
      if (child.person?.id === person.id) {
        if (data.husband?.id) parents.add(data.husband.id)
        if (data.wife?.id) parents.add(data.wife.id)
      }
    })
  }

  // Check main family
  findParents(familyData.value)

  // Check all cross-families
  familyGenerations.value.forEach((generation) => {
    generation.couples.forEach((couple) => {
      couple.children.forEach((child) => {
        if (child.id === person.id) {
          if (couple.husband?.id) parents.add(couple.husband.id)
          if (couple.wife?.id) parents.add(couple.wife.id)
        }
      })
    })
  })

  // Find spouse (check if person is part of a couple)
  familyGenerations.value.forEach((generation) => {
    generation.couples.forEach((couple) => {
      if (couple.husband?.id === person.id && couple.wife?.id) {
        spouse = couple.wife.id
      } else if (couple.wife?.id === person.id && couple.husband?.id) {
        spouse = couple.husband.id
      }
    })
  })

  // Recursively find all descendants (children, grandchildren, etc.)
  const findAllDescendants = (personToCheck: Person) => {
    if (personToCheck.has_own_family && personToCheck.own_families) {
      personToCheck.own_families.forEach((ownFamily) => {
        const familyChildren = crossFamilyChildren.value.get(ownFamily.id) || []
        familyChildren.forEach((child) => {
          if (child.id && !children.has(child.id)) {
            children.add(child.id)
            // Recursively find this child's descendants
            findAllDescendants(child)
          }
        })
      })
    }
  }

  // Start recursive search from the selected person
  findAllDescendants(person)

  highlightedParents.value = parents
  highlightedChildren.value = children
  highlightedSpouse.value = spouse
}

const getPersonHighlightClass = (person: Person): string => {
  const activePerson = clickedPerson.value || hoveredPerson.value
  if (!activePerson) return ''

  if (person.id === activePerson.id) return 'highlight-self'
  if (highlightedParents.value.has(person.id)) return 'highlight-parent'
  if (highlightedChildren.value.has(person.id)) return 'highlight-child'
  if (highlightedSpouse.value === person.id) return 'highlight-spouse'

  return ''
}

const showTooltip = (event: MouseEvent, person: Person) => {
  tooltip.value = {
    visible: true,
    x: event.pageX + 10,
    y: event.pageY - 10,
    person: person,
  }
}

const hideTooltip = () => {
  tooltip.value.visible = false
}

const showMarriageTooltip = (event: MouseEvent, couple: Couple) => {
  marriageTooltip.value = {
    visible: true,
    x: event.pageX + 10,
    y: event.pageY - 10,
    couple: couple,
  }
}

const hideMarriageTooltip = () => {
  marriageTooltip.value.visible = false
}

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch (_error) {
    return dateString
  }
}

const startDrag = (e: MouseEvent) => {
  // Allow drag from anywhere
  isDragging.value = true
  dragStart.value = { x: e.clientX, y: e.clientY }
  panStart.value = { x: panX.value, y: panY.value }
}

const handleDrag = (e: MouseEvent) => {
  if (!isDragging.value) return

  const dx = e.clientX - dragStart.value.x
  const dy = e.clientY - dragStart.value.y

  // Only start panning if moved more than 3 pixels (to allow clicks)
  const distance = Math.sqrt(dx * dx + dy * dy)
  if (distance > 3) {
    panX.value = panStart.value.x + dx
    panY.value = panStart.value.y + dy
  }
}

const stopDrag = () => {
  isDragging.value = false
}

const handleWheel = (e: WheelEvent) => {
  e.preventDefault()

  const delta = e.deltaY > 0 ? 0.9 : 1.1
  const newScale = Math.min(Math.max(0.1, scale.value * delta), 3)

  // Zoom towards mouse position
  if (treeContainer.value) {
    const rect = treeContainer.value.getBoundingClientRect()
    const mouseX = e.clientX - rect.left
    const mouseY = e.clientY - rect.top

    // Calculate the point in the content that's under the mouse
    const contentX = (mouseX - panX.value) / scale.value
    const contentY = (mouseY - panY.value) / scale.value

    // Update pan to keep that point under the mouse after zoom
    panX.value = mouseX - contentX * newScale
    panY.value = mouseY - contentY * newScale
  }

  scale.value = newScale
}

const zoomIn = () => {
  const newScale = Math.min(scale.value * 1.1, 3)

  // Zoom towards center
  if (treeContainer.value) {
    const rect = treeContainer.value.getBoundingClientRect()
    const centerX = rect.width / 2
    const centerY = rect.height / 2

    const contentX = (centerX - panX.value) / scale.value
    const contentY = (centerY - panY.value) / scale.value

    panX.value = centerX - contentX * newScale
    panY.value = centerY - contentY * newScale
  }

  scale.value = newScale
}

const zoomOut = () => {
  const newScale = Math.max(scale.value / 1.1, 0.1)

  // Zoom towards center
  if (treeContainer.value) {
    const rect = treeContainer.value.getBoundingClientRect()
    const centerX = rect.width / 2
    const centerY = rect.height / 2

    const contentX = (centerX - panX.value) / scale.value
    const contentY = (centerY - panY.value) / scale.value

    panX.value = centerX - contentX * newScale
    panY.value = centerY - contentY * newScale
  }

  scale.value = newScale
}

const resetZoom = () => {
  scale.value = 1
  panX.value = 0
  panY.value = 0
}

const fitTreeToView = async () => {
  // Wait for next tick to ensure DOM is updated
  await nextTick()

  if (!treeContainer.value || !treeContent.value) return

  const containerRect = treeContainer.value.getBoundingClientRect()
  const contentRect = treeContent.value.getBoundingClientRect()

  // Calculate scale to fit content with some padding (90% of container)
  const scaleX = (containerRect.width * 0.9) / contentRect.width
  const scaleY = (containerRect.height * 0.9) / contentRect.height
  const newScale = Math.min(scaleX, scaleY, 1) // Don't zoom in beyond 100%

  // Calculate pan to center the content
  const scaledWidth = contentRect.width * newScale
  const scaledHeight = contentRect.height * newScale

  panX.value = (containerRect.width - scaledWidth) / 2
  panY.value = (containerRect.height - scaledHeight) / 2 + 50 // Add offset for header
  scale.value = newScale
}

// Lifecycle
onMounted(() => {
  loadFamilyData()

  // Add global mouse event listeners for drag
  window.addEventListener('mousemove', handleDrag)
  window.addEventListener('mouseup', stopDrag)
})

onUnmounted(() => {
  // Clean up event listeners
  window.removeEventListener('mousemove', handleDrag)
  window.removeEventListener('mouseup', stopDrag)
})

// Watch for family ID changes
watch(
  () => props.familyId,
  () => {
    loadFamilyData()
  },
)
</script>

<style scoped>
.family-tree {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: none;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  text-decoration: none;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.back-icon {
  font-size: 1.1rem;
  font-weight: bold;
}

.tree-header h2 {
  color: white;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.tree-controls {
  display: flex;
  gap: 0.75rem;
  align-items: center;
}

.zoom-info {
  padding: 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.25);
  border-radius: 6px;
  backdrop-filter: blur(10px);
  min-width: 60px;
  text-align: center;
}

.zoom-label {
  color: white;
  font-size: 0.85rem;
  font-weight: 600;
  font-family: monospace;
}

.control-button {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.control-button-small {
  padding: 0.5rem 0.75rem;
  font-size: 1.1rem;
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.control-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.error-state {
  color: #dc2626;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.tree-container {
  flex: 1;
  overflow: hidden;
  position: relative;
  background:
    linear-gradient(90deg, rgba(200, 200, 200, 0.1) 1px, transparent 1px),
    linear-gradient(rgba(200, 200, 200, 0.1) 1px, transparent 1px);
  background-size: 50px 50px;
  background-position: 0 0;
  cursor: grab;
}

.tree-container:active {
  cursor: grabbing;
}

.tree-content {
  min-width: 100%;
  min-height: 100%;
  padding: 100px;
  position: relative;
  user-select: none;
}

.family-generation {
  margin-bottom: 4rem;
}

.generation-label {
  text-align: center;
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0 auto 2rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  display: block;
  width: fit-content;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.marriage-info {
  text-align: center;
  margin-bottom: 2rem;
}

.marriage-details {
  display: inline-flex;
  gap: 2rem;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 2px solid rgba(52, 152, 219, 0.3);
}

.marriage-date,
.marriage-place {
  color: #2c3e50;
  font-size: 1rem;
}

.marriage-date strong,
.marriage-place strong {
  color: #3498db;
  margin-right: 0.5rem;
}

.couples-row {
  display: flex;
  gap: 3rem;
  justify-content: center;
  align-items: flex-start;
  padding: 0 2rem;
}

.couple-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 500px;
}

.spouses-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  justify-content: center;
  width: 100%;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 16px;
  border: 2px solid rgba(150, 150, 200, 0.3);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.marriage-line {
  width: 60px;
  height: 3px;
  border-radius: 2px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  flex-shrink: 0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.marriage-line-married {
  background: linear-gradient(90deg, #27ae60, #2ecc71) !important;
  border: 2px solid #27ae60;
}

.marriage-line-divorced {
  background: repeating-linear-gradient(
    90deg,
    #e74c3c 0px,
    #e74c3c 8px,
    transparent 8px,
    transparent 16px
  ) !important;
  border: 2px solid #e74c3c;
}

.marriage-line-unknown {
  background: linear-gradient(90deg, #95a5a6, #bdc3c7) !important;
  border: 2px solid #95a5a6;
}

.marriage-line:hover {
  transform: scaleY(1.5);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
}

.person-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  z-index: 2;
  min-width: 180px;
  margin-bottom: 1rem;
}

.person-node:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.person-node.husband {
  border-left: 4px solid #3498db;
}

.person-node.wife {
  border-left: 4px solid #e74c3c;
}

/* Highlight states */
.person-node.highlight-self,
.child-node.highlight-self {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%) !important;
  border-left-color: #ff8c00 !important;
  box-shadow: 0 8px 35px rgba(255, 215, 0, 0.5) !important;
  transform: scale(1.05);
  z-index: 100;
}

.person-node.highlight-parent,
.child-node.highlight-parent {
  background: linear-gradient(135deg, #87ceeb 0%, #b0e0e6 100%) !important;
  border-left-color: #4682b4 !important;
  box-shadow: 0 6px 25px rgba(70, 130, 180, 0.4) !important;
  z-index: 50;
}

.person-node.highlight-spouse,
.child-node.highlight-spouse {
  background: linear-gradient(135deg, #ffb6c1 0%, #ffc0cb 100%) !important;
  border-left-color: #ff69b4 !important;
  box-shadow: 0 6px 25px rgba(255, 105, 180, 0.4) !important;
  z-index: 50;
}

.person-node.highlight-child,
.child-node.highlight-child {
  background: linear-gradient(135deg, #98fb98 0%, #90ee90 100%) !important;
  border-left-color: #32cd32 !important;
  box-shadow: 0 6px 25px rgba(50, 205, 50, 0.4) !important;
  z-index: 50;
}

.person-avatar {
  margin-bottom: 1rem;
}

.avatar-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.person-node.husband .avatar-circle {
  background: linear-gradient(135deg, #3498db, #2980b9);
}

.person-node.wife .avatar-circle {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.person-info {
  text-align: center;
}

.person-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.person-dates {
  font-size: 0.9rem;
  color: #7f8c8d;
  font-style: italic;
}

.generation-children-row {
  display: flex;
  gap: 3rem;
  justify-content: center;
  align-items: flex-start;
  margin-top: 2rem;
  padding: 0 2rem;
}

.children-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 500px;
  min-height: 50px;
}

.children-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
}

.children-connection {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 1rem;
}

.connection-line {
  width: 3px;
  height: 40px;
  background: linear-gradient(180deg, #95a5a6, #bdc3c7);
  border-radius: 2px;
}

.children-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
  align-items: flex-start;
  width: 100%;
  min-width: 500px;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 16px;
  border: 2px dashed rgba(100, 180, 100, 0.4);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.child-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 3px 15px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  min-width: 150px;
  border-left: 3px solid #27ae60;
}

.child-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 0, 0, 0.12);
}

.child-avatar {
  margin-bottom: 0.75rem;
}

.child-avatar .avatar-circle {
  width: 45px;
  height: 45px;
  font-size: 1.5rem;
  background: linear-gradient(135deg, #27ae60, #2ecc71);
}

.child-info {
  text-align: center;
}

.child-name {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.child-dates {
  font-size: 0.8rem;
  color: #7f8c8d;
  font-style: italic;
}

.person-tooltip,
.marriage-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-family:
    system-ui,
    -apple-system,
    sans-serif;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  pointer-events: none;
  z-index: 1000;
  max-width: 350px;
  line-height: 1.4;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tooltip-name {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.tooltip-details {
  font-size: 0.9rem;
}

.tooltip-details div {
  margin-bottom: 0.25rem;
}

.relationship-status {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.relationship-status.married {
  background: rgba(39, 174, 96, 0.2);
  color: #27ae60;
  border: 1px solid #27ae60;
}

.relationship-status.divorced {
  background: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
  border: 1px solid #e74c3c;
}

.relationship-status.unknown {
  background: rgba(149, 165, 166, 0.2);
  color: #95a5a6;
  border: 1px solid #95a5a6;
}

.events-list {
  margin: 0.5rem 0 0 0;
  padding-left: 1rem;
  max-height: 150px;
  overflow-y: auto;
}

.events-list li {
  margin-bottom: 0.25rem;
  font-size: 0.85rem;
  color: #ecf0f1;
}

/* Responsive */
@media (max-width: 768px) {
  .tree-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }

  .tree-controls {
    justify-content: center;
  }

  .couples-row {
    flex-direction: column;
    align-items: center;
  }

  .couple-container {
    width: 320px;
  }

  .spouses-row {
    flex-direction: column;
    gap: 0.5rem;
    padding: 1rem;
  }

  .marriage-line {
    width: 3px;
    height: 30px;
    background: linear-gradient(180deg, #e74c3c, #f39c12);
  }

  .generation-children-row {
    flex-direction: column;
    align-items: center;
    gap: 2rem;
  }

  .children-group {
    width: 320px;
  }

  .children-container {
    flex-direction: column;
    align-items: center;
    padding: 1rem;
  }
}
</style>
