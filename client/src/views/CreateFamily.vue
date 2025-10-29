<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { familyService, type CreateFamily } from '@/services/familyService'
import { personService } from '@/services/personService'
import { childService } from '@/services/childService'
import { eventService } from '@/services/eventService'
import { FAMILY_EVENT_TYPES } from '@/types/event'
import type { Person } from '@/types/family'
import CreatePersonModal from '@/components/CreatePersonModal.vue'

const router = useRouter()

type PersonOption = {
  id: string
  label: string
}

const husbandId = ref<string>('')
const wifeId = ref<string>('')
const marriage_date = ref<string>('')
const marriage_place = ref<string>('')
const notes = ref<string>('')

// Enfants
const children = ref<Array<{ id: string; label: string }>>([])
const queryChild = ref('')
const childOptions = ref<PersonOption[]>([])

// Events
const events = ref<Array<{
  type: string
  date: string
  place: string
  description: string
}>>([])
const eventTypes = FAMILY_EVENT_TYPES

const submitting = ref(false)
const error = ref('')
const success = ref('')

// Selected parent data for validation
const selectedHusband = ref<Person | null>(null)
const selectedWife = ref<Person | null>(null)
const marriageDateError = ref('')

// Modales
const showCreatePersonModal = ref(false)
const currentParentType = ref<'husband' | 'wife' | 'child'>('husband')

// Simple autocompletion (free text)
const queryHusband = ref('')
const queryWife = ref('')
const husbandOptions = ref<PersonOption[]>([])
const wifeOptions = ref<PersonOption[]>([])

// Show/hide dropdown states
const showHusbandDropdown = ref(false)
const showWifeDropdown = ref(false)
const showChildDropdown = ref(false)

// Debounce pour la recherche
let searchTimeout: ReturnType<typeof setTimeout> | null = null

async function searchPersons(query: string, type: 'husband' | 'wife' | 'child') {
  if (!query.trim()) {
    if (type === 'husband') {
      husbandOptions.value = []
      showHusbandDropdown.value = false
    } else if (type === 'wife') {
      wifeOptions.value = []
      showWifeDropdown.value = false
    } else if (type === 'child') {
      childOptions.value = []
      showChildDropdown.value = false
    }
    return
  }

  try {
    const response = await personService.searchPersonsByName(query, { limit: 10 })
    const persons = response.data

    const options = persons.map((person: Person) => ({
      id: person.id,
      label: `${person.first_name} ${person.last_name}${person.birth_date ? ' • n. ' + person.birth_date : ''}${person.birth_place ? ' • ' + person.birth_place : ''}`
    }))

    if (type === 'husband') {
      husbandOptions.value = options
      showHusbandDropdown.value = options.length > 0
    } else if (type === 'wife') {
      wifeOptions.value = options
      showWifeDropdown.value = options.length > 0
    } else if (type === 'child') {
      childOptions.value = options
      showChildDropdown.value = options.length > 0
    }
  } catch (error) {
    console.error('Error during search:', error)
    if (type === 'husband') {
      husbandOptions.value = []
      showHusbandDropdown.value = false
    } else if (type === 'wife') {
      wifeOptions.value = []
      showWifeDropdown.value = false
    } else if (type === 'child') {
      childOptions.value = []
      showChildDropdown.value = false
    }
  }
}

function onInputSearch(type: 'husband' | 'wife') {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  const query = type === 'husband' ? queryHusband.value : queryWife.value

  searchTimeout = setTimeout(() => {
    searchPersons(query, type)
  }, 300)
}

// Select person from dropdown
function selectPerson(option: PersonOption, type: 'husband' | 'wife' | 'child') {
  if (type === 'husband') {
    husbandId.value = option.id
    queryHusband.value = option.label
    showHusbandDropdown.value = false
    loadPersonDetails('husband', option.id)
  } else if (type === 'wife') {
    wifeId.value = option.id
    queryWife.value = option.label
    showWifeDropdown.value = false
    loadPersonDetails('wife', option.id)
  } else if (type === 'child') {
    // Find the last added child and fill it with the selected person
    const lastChildIndex = children.value.length - 1
    if (lastChildIndex >= 0) {
      children.value[lastChildIndex].id = option.id
      children.value[lastChildIndex].label = option.label
      queryChild.value = option.label
      showChildDropdown.value = false
      loadChildDetails(option.id)
    }
  }
}

// Clear selection
function clearSelection(type: 'husband' | 'wife' | 'child') {
  if (type === 'husband') {
    husbandId.value = ''
    queryHusband.value = ''
    selectedHusband.value = null
    showHusbandDropdown.value = false
  } else if (type === 'wife') {
    wifeId.value = ''
    queryWife.value = ''
    selectedWife.value = null
    showWifeDropdown.value = false
  } else if (type === 'child') {
    queryChild.value = ''
    showChildDropdown.value = false
  }
}

// Handle blur events with delay
function handleHusbandBlur() {
  setTimeout(() => { showHusbandDropdown.value = false }, 200)
}

function handleWifeBlur() {
  setTimeout(() => { showWifeDropdown.value = false }, 200)
}

function handleChildBlur() {
  setTimeout(() => { showChildDropdown.value = false }, 200)
}

// Marriage date validation (complex logic extracted to helpers to lower complexity)
function isFutureDate(date: Date): boolean {
  const today = new Date()
  return date > today
}

function validateAgainstPerson(marriageDate: Date, person: Person | null, label: 'husband' | 'wife'): string | null {
  if (!person) return null
  if (person.birth_date) {
    const birth = new Date(person.birth_date)
    if (marriageDate < birth) return `Marriage date cannot be before the ${label}'s birth.`
  }
  if (person.death_date) {
    const death = new Date(person.death_date)
    if (marriageDate > death) return `Marriage date cannot be after the ${label}'s death.`
  }
  return null
}

function computeMarriageDateError(dateStr: string): string {
  const marriageDate = new Date(dateStr)
  if (isFutureDate(marriageDate)) return 'Marriage date cannot be in the future.'
  return (
    validateAgainstPerson(marriageDate, selectedHusband.value, 'husband') ||
    validateAgainstPerson(marriageDate, selectedWife.value, 'wife') ||
    ''
  )
}

function validateMarriageDate() {
  marriageDateError.value = ''
  if (!marriage_date.value) return
  marriageDateError.value = computeMarriageDateError(marriage_date.value)
}

// Load details of a selected person
async function loadPersonDetails(type: 'husband' | 'wife', personId: string) {
  try {
    // If none selected, reset preview
    if (!personId) {
      if (type === 'husband') {
        selectedHusband.value = null
      } else {
        selectedWife.value = null
      }
      // Revalidate date if needed (to clear any message)
      if (marriage_date.value) {
        validateMarriageDate()
      }
      return
    }
    const response = await personService.getPersonById(personId)
    const person = response.data

    if (type === 'husband') {
      selectedHusband.value = person
    } else {
      selectedWife.value = person
    }

    // Revalidate marriage date if already entered
    if (marriage_date.value) {
      validateMarriageDate()
    }
  } catch (error) {
    console.error('Error loading person details:', error)
  }
}

// Open person creation modal
function openCreatePersonModal(type: 'husband' | 'wife' | 'child') {
  currentParentType.value = type
  showCreatePersonModal.value = true
}

// Close modal
function closeCreatePersonModal() {
  showCreatePersonModal.value = false
}

// Navigation vers l'accueil
const navigateToHome = () => {
  router.push('/')
}

// Handle person creation from modal
function handlePersonCreated(createdPerson: Person) {
  // Add created person to options and select it
  const newOption = {
    id: createdPerson.id,
    label: `${createdPerson.first_name} ${createdPerson.last_name}`
  }

  if (currentParentType.value === 'husband') {
    husbandOptions.value = [newOption, ...husbandOptions.value]
    husbandId.value = createdPerson.id
    queryHusband.value = newOption.label
    selectedHusband.value = createdPerson
  } else if (currentParentType.value === 'wife') {
    wifeOptions.value = [newOption, ...wifeOptions.value]
    wifeId.value = createdPerson.id
    queryWife.value = newOption.label
    selectedWife.value = createdPerson
  } else if (currentParentType.value === 'child') {
    // Find the last added child and fill it with the created person
    const lastChildIndex = children.value.length - 1
    if (lastChildIndex >= 0) {
      const newOption = {
        id: createdPerson.id,
        label: `${createdPerson.first_name} ${createdPerson.last_name}${createdPerson.birth_date ? ' • n. ' + createdPerson.birth_date : ''}`
      }
      childOptions.value = [newOption, ...childOptions.value]
      children.value[lastChildIndex].id = createdPerson.id
      children.value[lastChildIndex].label = newOption.label
      queryChild.value = newOption.label
    }
  }

  // Close modal
  closeCreatePersonModal()

  // Show success message
  success.value = `Person "${createdPerson.first_name} ${createdPerson.last_name}" created successfully`
  setTimeout(() => { success.value = '' }, 3000)
}

// Children management
function addChild() {
  children.value.push({
    id: '',
    label: ''
  })
}

function removeChild(index: number) {
  children.value.splice(index, 1)
}

async function onInputSearchChild() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  searchTimeout = setTimeout(() => {
    searchPersons(queryChild.value, 'child')
  }, 300)
}

async function loadChildDetails(childId: string) {
  if (!childId) return

  try {
    const response = await personService.getPersonById(childId)
    const person = response.data

    // Update child label
    const childIndex = children.value.findIndex(child => child.id === childId)
    if (childIndex !== -1) {
      children.value[childIndex].label = `${person.first_name} ${person.last_name}`
    }
  } catch (error) {
    console.error('Error loading child details:', error)
  }
}

// Event management
function addEvent() {
  events.value.push({
    type: '',
    date: '',
    place: '',
    description: ''
  })
}

function removeEvent(index: number) {
  events.value.splice(index, 1)
}

const payload = computed<CreateFamily>(() => {
  const data: CreateFamily = {}
  if (husbandId.value) data.husband_id = husbandId.value
  if (wifeId.value) data.wife_id = wifeId.value
  if (marriage_date.value) data.marriage_date = marriage_date.value
  if (marriage_place.value) data.marriage_place = marriage_place.value
  if (notes.value) data.notes = notes.value
  return data
})

// Validation functions
function validateFormSubmission(): boolean {
  // Marriage date validation before submission
  validateMarriageDate()
  if (marriageDateError.value) {
    error.value = marriageDateError.value
    return false
  }

  // Minimum validation: at least one parent
  if (!husbandId.value && !wifeId.value) {
    error.value = 'At least one parent is required.'
    return false
  }

  return true
}

// Child creation logic
async function createChildrenRelationships(familyId: string): Promise<void> {
  if (children.value.length === 0) return

  for (const child of children.value) {
    try {
      await childService.createChild({
        family_id: familyId,
        child_id: child.id
      })
    } catch (childError: unknown) {
      console.error(`Error adding child ${child.label}:`, childError)
      // Continue even if a child fails
    }
  }
}

// Event creation logic
async function createFamilyEvents(familyId: string): Promise<void> {
  console.log('createFamilyEvents called with familyId:', familyId)
  console.log('events.value:', events.value)
  
  if (events.value.length === 0) {
    console.log('No events to create')
    return
  }

  // Filter events that have a valid type
  const validEvents = events.value.filter(event => event.type && event.type.trim() !== '')
  console.log('validEvents:', validEvents)
  
  for (const event of validEvents) {
    try {
      console.log('Creating event:', event)
      await eventService.createEvent({
        family_id: familyId,
        type: event.type,
        date: event.date || null,
        place: event.place || null,
        description: event.description || null
      })
      console.log('Event created successfully:', event.type)
    } catch (eventError: unknown) {
      console.error(`Error adding event ${event.type}:`, eventError)
      // Continue even if an event fails
    }
  }
}

// Success message generation
function generateSuccessMessage(): string {
  const childCount = children.value.length
  const validEventCount = events.value.filter(event => event.type && event.type.trim() !== '').length
  let message = 'Family created'

  if (childCount > 0) {
    message += ` with ${childCount} child${childCount > 1 ? 'ren' : ''}`
  }

  if (validEventCount > 0) {
    message += `${childCount > 0 ? ' and' : ' with'} ${validEventCount} event${validEventCount > 1 ? 's' : ''}`
  }

  return message + '.'
}

// Form reset logic
function resetForm(): void {
  husbandId.value = ''
  wifeId.value = ''
  marriage_date.value = ''
  marriage_place.value = ''
  notes.value = ''
  children.value = []
  events.value = []
  husbandOptions.value = []
  wifeOptions.value = []
  childOptions.value = []
  queryHusband.value = ''
  queryWife.value = ''
  queryChild.value = ''
  selectedHusband.value = null
  selectedWife.value = null
  showHusbandDropdown.value = false
  showWifeDropdown.value = false
  showChildDropdown.value = false
}

// Main submit function - now much simpler
async function submit() {
  console.log('Submit function called')
  error.value = ''
  success.value = ''
  marriageDateError.value = ''

  if (!validateFormSubmission()) {
    submitting.value = false
    return
  }

  submitting.value = true

  try {
    const res = await familyService.createFamily(payload.value)
    const familyId = res.data.id

    await createChildrenRelationships(familyId)
    await createFamilyEvents(familyId)

    success.value = generateSuccessMessage()
    resetForm()

  } catch (e: unknown) {
    const apiError = e as { response?: { data?: { detail?: string } } }
    error.value = apiError.response?.data?.detail || 'Error creating family'
  } finally {
    submitting.value = false
  }
}

// Expose methods/refs for unit tests
defineExpose({
  loadPersonDetails,
  validateMarriageDate,
  submit,
  // state
  marriage_date,
  marriageDateError,
  husbandId,
  wifeId,
  error,
  success,
  // search helpers
  queryHusband,
  searchPersons,
  husbandOptions,
  // modal controls
  openCreatePersonModal,
  showCreatePersonModal,
  currentParentType,
})
</script>

<template>
  <div class="create-family-view">
    <div class="create-family">
      <div class="page-header">
        <div class="header-content">
          <div class="header-text">
            <h2>👨‍👩‍👧‍👦 Create a Family</h2>
            <p>Create a new family by adding parents and marriage information</p>
          </div>
          <button @click="navigateToHome" class="back-to-home-btn" data-cy="back-to-home">
            🏠 Go back to home
          </button>
        </div>
      </div>

      <form @submit.prevent="submit" class="family-form">
        <!-- Parents Section -->
        <div class="form-section">
          <div class="section-header">
            <h3>👫 Parents</h3>
            <p>Add one or two parents to the family</p>
          </div>

          <div class="parents-grid">
            <!-- Mari -->
            <div class="parent-card">
              <div class="parent-header">
                <h4>👨 Husband</h4>
                <span class="required-badge">Optional</span>
              </div>

              <div class="search-container">
                <div class="search-input-wrapper">
                  <input
                    v-model="queryHusband"
                    type="text"
                    placeholder="Search for existing husband..."
                    class="search-input"
                    data-cy="search-husband"
                    @input="onInputSearch('husband')"
                    @focus="showHusbandDropdown = husbandOptions.length > 0"
                    @blur="handleHusbandBlur"
                  />
                  <button
                    v-if="husbandId"
                    type="button"
                    class="clear-btn"
                    @click="clearSelection('husband')"
                    title="Clear selection"
                  >
                    ✕
                  </button>
                  
                  <!-- Dropdown suggestions -->
                  <div v-if="showHusbandDropdown && husbandOptions.length > 0" class="dropdown-suggestions" data-cy="husband-suggestions">
                    <div
                      v-for="option in husbandOptions"
                      :key="option.id"
                      class="suggestion-item"
                      :data-cy="`husband-suggestion-${option.id}`"
                      @click="selectPerson(option, 'husband')"
                    >
                      {{ option.label }}
                    </div>
                  </div>
                </div>
                
                <button
                  type="button"
                  class="create-person-btn"
                  data-cy="create-husband-btn"
                  @click="openCreatePersonModal('husband')"
                >
                  ➕ Create
                </button>
              </div>

              <!-- Aperçu du mari sélectionné -->
              <div v-if="selectedHusband" class="person-preview" data-cy="preview-husband">
                <div class="person-info">
                  <strong>{{ selectedHusband.first_name }} {{ selectedHusband.last_name }}</strong>
                  <span class="person-sex">{{ selectedHusband.sex === 'M' ? '♂' : selectedHusband.sex === 'F' ? '♀' : '⚥' }}</span>
                </div>
                <div v-if="selectedHusband.birth_date || selectedHusband.death_date" class="person-dates">
                  <span v-if="selectedHusband.birth_date">Born: {{ selectedHusband.birth_date }}</span>
                  <span v-if="selectedHusband.death_date">Died: {{ selectedHusband.death_date }}</span>
                </div>
                <div v-if="selectedHusband.birth_place || selectedHusband.death_place" class="person-places">
                  <span v-if="selectedHusband.birth_place">Place of birth: {{ selectedHusband.birth_place }}</span>
                  <span v-if="selectedHusband.death_place">Place of death: {{ selectedHusband.death_place }}</span>
                </div>
                <div v-if="selectedHusband.notes" class="person-notes">
                  Notes: {{ selectedHusband.notes }}
                </div>
              </div>
            </div>

            <!-- Femme -->
            <div class="parent-card">
              <div class="parent-header">
                <h4>👩 Wife</h4>
                <span class="required-badge">Optional</span>
              </div>

              <div class="search-container">
                <div class="search-input-wrapper">
                  <input
                    v-model="queryWife"
                    type="text"
                    placeholder="Search for existing wife..."
                    class="search-input"
                    data-cy="search-wife"
                    @input="onInputSearch('wife')"
                    @focus="showWifeDropdown = wifeOptions.length > 0"
                    @blur="handleWifeBlur"
                  />
                  <button
                    v-if="wifeId"
                    type="button"
                    class="clear-btn"
                    @click="clearSelection('wife')"
                    title="Clear selection"
                  >
                    ✕
                  </button>
                  
                  <!-- Dropdown suggestions -->
                  <div v-if="showWifeDropdown && wifeOptions.length > 0" class="dropdown-suggestions" data-cy="wife-suggestions">
                    <div
                      v-for="option in wifeOptions"
                      :key="option.id"
                      class="suggestion-item"
                      :data-cy="`wife-suggestion-${option.id}`"
                      @click="selectPerson(option, 'wife')"
                    >
                      {{ option.label }}
                    </div>
                  </div>
                </div>
                
                <button
                  type="button"
                  class="create-person-btn"
                  data-cy="create-wife-btn"
                  @click="openCreatePersonModal('wife')"
                >
                  ➕ Create
                </button>
              </div>

              <!-- Aperçu de la femme sélectionnée -->
              <div v-if="selectedWife" class="person-preview" data-cy="preview-wife">
                <div class="person-info">
                  <strong>{{ selectedWife.first_name }} {{ selectedWife.last_name }}</strong>
                  <span class="person-sex">{{ selectedWife.sex === 'M' ? '♂' : selectedWife.sex === 'F' ? '♀' : '⚥' }}</span>
                </div>
                <div v-if="selectedWife.birth_date || selectedWife.death_date" class="person-dates">
                  <span v-if="selectedWife.birth_date">Born: {{ selectedWife.birth_date }}</span>
                  <span v-if="selectedWife.death_date">Died: {{ selectedWife.death_date }}</span>
                </div>
                <div v-if="selectedWife.birth_place || selectedWife.death_place" class="person-places">
                  <span v-if="selectedWife.birth_place">Place of birth: {{ selectedWife.birth_place }}</span>
                  <span v-if="selectedWife.death_place">Place of death: {{ selectedWife.death_place }}</span>
                </div>
                <div v-if="selectedWife.notes" class="person-notes">
                  Notes: {{ selectedWife.notes }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Informations de mariage Section -->
        <div class="form-section">
          <div class="section-header">
            <h3>💒 Marriage information</h3>
            <p>Add marriage details (optional)</p>
          </div>

          <div class="marriage-fields">
            <div class="form-group">
              <label for="marriage_date">📅 Date of marriage</label>
              <input
                id="marriage_date"
                v-model="marriage_date"
                type="date"
                data-cy="marriage-date"
                @change="validateMarriageDate"
              />
              <div v-if="marriageDateError" class="field-error">{{ marriageDateError }}</div>
            </div>
            <div class="form-group">
              <label for="marriage_place">📍 Place of marriage</label>
              <input
                id="marriage_place"
                v-model="marriage_place"
                type="text"
                placeholder="Ex: Paris, France"
                data-cy="marriage-place"
              />
            </div>
          </div>
        </div>

        <!-- Événements Section -->
        <div class="form-section">
          <div class="section-header">
            <h3>📅 Events</h3>
            <p>Add events linked to the family</p>
          </div>

          <div class="events-section">
            <button
              type="button"
              class="add-event-btn"
              data-cy="add-event-btn"
              @click="addEvent"
            >
              ➕ Add an event
            </button>

            <div v-for="(event, index) in events" :key="index" class="event-form" :data-cy="`event-${index}`">
              <div class="event-header">
                <h4>Event {{ index + 1 }}</h4>
                <button
                  type="button"
                  class="remove-event-btn"
                  :data-cy="`remove-event-${index}`"
                  @click="removeEvent(index)"
                >
                  🗑️ Delete
                </button>
              </div>

              <div class="event-fields">
                <div class="form-group">
                  <label>Type of event</label>
                  <select v-model="event.type" :data-cy="`event-type-${index}`">
                    <option value="">Select a type</option>
                    <option
                      v-for="eventType in eventTypes"
                      :key="eventType.value"
                      :value="eventType.value"
                    >
                      {{ eventType.label }}
                    </option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Date</label>
                  <input
                    v-model="event.date"
                    type="date"
                    :data-cy="`event-date-${index}`"
                  />
                </div>

                <div class="form-group">
                  <label>Place</label>
                  <input
                    v-model="event.place"
                    type="text"
                    placeholder="Ex: Paris, France"
                    :data-cy="`event-place-${index}`"
                  />
                </div>

                <div class="form-group">
                  <label>Description</label>
                  <textarea
                    v-model="event.description"
                    placeholder="Event description..."
                    :data-cy="`event-description-${index}`"
                  ></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Enfants Section -->
        <div class="form-section">
          <div class="section-header">
            <h3>👶 Children</h3>
            <p>Add children to the family</p>
          </div>

          <div class="children-section">
            <button
              type="button"
              class="add-child-btn"
              data-cy="add-child-button"
              @click="addChild"
            >
              ➕ Add a child
            </button>

            <div v-for="(child, index) in children" :key="index" class="child-form" data-cy="children-list">
              <div class="child-header">
                <h4>Child {{ index + 1 }}</h4>
                <button
                  type="button"
                  class="remove-child-btn"
                  data-cy="remove-child-btn"
                  @click="removeChild(index)"
                >
                  🗑️ Delete
                </button>
              </div>

              <div class="child-fields">
                <div class="search-container">
                  <div class="search-input-wrapper">
                  <input
                      v-model="queryChild"
                      type="text"
                      placeholder="Search an existing child..."
                      class="search-input"
                      data-cy="search-child"
                      @input="onInputSearchChild"
                      @focus="showChildDropdown = childOptions.length > 0"
                      @blur="handleChildBlur"
                    />
                    <button
                      v-if="child.id"
                      type="button"
                      class="clear-btn"
                      @click="clearSelection('child')"
                      title="Clear selection"
                    >
                      ✕
                    </button>
                    
                    <!-- Dropdown suggestions -->
                    <div v-if="showChildDropdown && childOptions.length > 0" class="dropdown-suggestions" data-cy="child-suggestions">
                      <div
                        v-for="option in childOptions"
                        :key="option.id"
                        class="suggestion-item"
                        :data-cy="`child-suggestion-${option.id}`"
                        @click="selectPerson(option, 'child')"
                      >
                        {{ option.label }}
                      </div>
                    </div>
                  </div>
                  
                  <button
                    type="button"
                    class="create-person-btn"
                    data-cy="create-child-button"
                    @click="openCreatePersonModal('child')"
                  >
                    ➕ Create
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Notes Section -->
        <div class="form-section">
          <div class="section-header">
            <h3>📝 Notes</h3>
            <p>Add notes about this family</p>
          </div>

          <div class="form-group">
            <label for="notes">Family Notes</label>
            <textarea
              id="notes"
              v-model="notes"
              placeholder="Family notes, additional information..."
              data-cy="family-notes"
            ></textarea>
          </div>
        </div>

        <!-- Boutons d'action -->
        <div class="form-actions">
          <button
            type="submit"
            :disabled="submitting"
            class="submit-btn"
            data-cy="submit-family"
          >
            <span v-if="submitting" class="loading-spinner"></span>
            {{ submitting ? 'Creating...' : '✨ Create Family' }}
          </button>
        </div>
      </form>

      <!-- Messages d'erreur et de succès -->
      <div v-if="error" class="error-message">
        <div class="error-icon">⚠️</div>
        <div class="error-content">
          <h4>Error</h4>
          <p>{{ error }}</p>
        </div>
      </div>

      <div v-if="success" class="success-message">
        <div class="success-icon">✅</div>
        <div class="success-content">
          <h4>Success</h4>
          <p>{{ success }}</p>
        </div>
      </div>
    </div>

    <!-- Modale de création de personne -->
    <CreatePersonModal
      :show="showCreatePersonModal"
      :parent-type="currentParentType"
      @close="closeCreatePersonModal"
      @person-created="handlePersonCreated"
    />
  </div>
</template>

<style scoped>
.create-family-view {
  flex: 1;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
  padding: 2rem 0;
}

.create-family {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.page-header {
  margin-bottom: 3rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-text {
  text-align: center;
  flex: 1;
}

.back-to-home-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.back-to-home-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

/* Responsive design pour le header */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
  }

  .header-text {
    margin-bottom: 1rem;
  }
}

.page-header h2 {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.page-header p {
  font-size: 1.1rem;
  color: #7f8c8d;
  max-width: 600px;
  margin: 0 auto;
}

.family-form {
  background: white;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.form-section {
  padding: 2rem;
  border-bottom: 1px solid #ecf0f1;
}

.form-section:last-of-type {
  border-bottom: none;
}

.section-header {
  margin-bottom: 2rem;
}

.section-header h3 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-header p {
  color: #7f8c8d;
  font-size: 0.95rem;
}

.parents-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
}

.parent-card {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
  transition: all 0.3s ease;
}

.parent-card:hover {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
}

.parent-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.parent-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.required-badge {
  background: #e74c3c;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.search-container {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input {
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
  flex: 1;
  padding-right: 2.5rem;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.clear-btn {
  position: absolute;
  right: 0.5rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 0.75rem;
  transition: all 0.2s ease;
}

.clear-btn:hover {
  background: #c0392b;
  transform: scale(1.1);
}

.dropdown-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 2px solid #e9ecef;
  border-top: none;
  border-radius: 0 0 8px 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 200px;
  overflow-y: auto;
}

.suggestion-item {
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f8f9fa;
  transition: background-color 0.2s ease;
  font-size: 0.9rem;
}

.suggestion-item:hover {
  background-color: #f8f9fa;
}

.suggestion-item:last-child {
  border-bottom: none;
}


.create-person-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.create-person-btn:hover {
  background: #5a6fd8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.person-preview {
  margin-top: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.person-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.person-info strong {
  color: #2c3e50;
  font-size: 1rem;
}

.person-sex {
  font-size: 1.2rem;
}

.person-dates,
.person-places,
.person-notes {
  font-size: 0.85rem;
  color: #7f8c8d;
  margin-bottom: 0.25rem;
}

.marriage-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.95rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  min-height: 80px;
  resize: vertical;
}

.field-error {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.events-section,
.children-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.add-event-btn,
.add-child-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  align-self: flex-start;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.add-event-btn:hover,
.add-child-btn:hover {
  background: #229954;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
}

.event-form,
.child-form {
  background: #f8f9fa;
  border: 2px solid #e9ecef;
  border-radius: 12px;
  padding: 1.5rem;
}

.event-header,
.child-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.event-header h4,
.child-header h4 {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.remove-event-btn,
.remove-child-btn {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.remove-event-btn:hover,
.remove-child-btn:hover {
  background: #c0392b;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.event-fields,
.child-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.event-fields .form-group:last-child {
  grid-column: 1 / -1;
}

.form-actions {
  padding: 2rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: center;
}

.submit-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-width: 200px;
  justify-content: center;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid transparent;
  border-top: 2px solid currentColor;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message,
.success-message {
  margin: 2rem 0;
  padding: 1.5rem;
  border-radius: 12px;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.error-message {
  background: #fdf2f2;
  border: 2px solid #fecaca;
  color: #dc2626;
}

.success-message {
  background: #f0fdf4;
  border: 2px solid #bbf7d0;
  color: #16a34a;
}

.error-icon,
.success-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.error-content,
.success-content {
  flex: 1;
}

.error-content h4,
.success-content h4 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
}

.error-content p,
.success-content p {
  margin: 0;
  font-size: 0.95rem;
}

/* Responsive */
@media (max-width: 768px) {
  .create-family {
    padding: 0 1rem;
  }

  .page-header h2 {
    font-size: 2rem;
  }

  .parents-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .marriage-fields {
    grid-template-columns: 1fr;
  }

  .event-fields {
    grid-template-columns: 1fr;
  }

  .form-section {
    padding: 1.5rem;
  }

  .form-actions {
    padding: 1.5rem;
  }
}
</style>
