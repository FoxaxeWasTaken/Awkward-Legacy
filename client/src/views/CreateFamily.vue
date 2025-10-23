<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { familyService, type CreateFamily } from '@/services/familyService'
import { personService } from '@/services/personService'
import { childService } from '@/services/childService'
import { eventService } from '@/services/eventService'
import { FAMILY_EVENT_TYPES } from '@/types/event'
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

// Événements
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

// Données des parents sélectionnés pour validation
const selectedHusband = ref<any>(null)
const selectedWife = ref<any>(null)
const marriageDateError = ref('')

// Modales
const showCreatePersonModal = ref(false)
const currentParentType = ref<'husband' | 'wife' | 'child'>('husband')

// Autocomplétion simple (texte libre)
const queryHusband = ref('')
const queryWife = ref('')
const husbandOptions = ref<PersonOption[]>([])
const wifeOptions = ref<PersonOption[]>([])

// Debounce pour la recherche
let searchTimeout: NodeJS.Timeout | null = null

async function searchPersons(query: string, type: 'husband' | 'wife' | 'child') {
  if (!query.trim()) {
    if (type === 'husband') {
      husbandOptions.value = []
    } else if (type === 'wife') {
      wifeOptions.value = []
    } else if (type === 'child') {
      childOptions.value = []
    }
    return
  }

  try {
    const response = await personService.searchPersonsByName(query, { limit: 10 })
    const persons = response.data
    
    const options = persons.map((person: any) => ({
      id: person.id,
      label: `${person.first_name} ${person.last_name}${person.birth_date ? ' • n. ' + person.birth_date : ''}${person.birth_place ? ' • ' + person.birth_place : ''}`
    }))
    
    if (type === 'husband') {
      husbandOptions.value = options
    } else if (type === 'wife') {
      wifeOptions.value = options
    } else if (type === 'child') {
      childOptions.value = options
    }
  } catch (error) {
    console.error('Erreur lors de la recherche:', error)
    if (type === 'husband') {
      husbandOptions.value = []
    } else if (type === 'wife') {
      wifeOptions.value = []
    } else if (type === 'child') {
      childOptions.value = []
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

// Validation de la date de mariage
function validateMarriageDate() {
  marriageDateError.value = ''
  
  if (!marriage_date.value) return
  
  const marriageDate = new Date(marriage_date.value)
  const today = new Date()
  
  // Vérifier que la date n'est pas dans le futur
  if (marriageDate > today) {
    marriageDateError.value = 'La date de mariage ne peut pas être dans le futur.'
    return
  }
  
  // Vérifier contre les dates de naissance et décès des parents
  if (selectedHusband.value) {
    if (selectedHusband.value.birth_date) {
      const husbandBirth = new Date(selectedHusband.value.birth_date)
      if (marriageDate < husbandBirth) {
        marriageDateError.value = 'La date de mariage ne peut pas être antérieure à la naissance du mari.'
        return
      }
    }
    if (selectedHusband.value.death_date) {
      const husbandDeath = new Date(selectedHusband.value.death_date)
      if (marriageDate > husbandDeath) {
        marriageDateError.value = 'La date de mariage ne peut pas être postérieure au décès du mari.'
        return
      }
    }
  }
  
  if (selectedWife.value) {
    if (selectedWife.value.birth_date) {
      const wifeBirth = new Date(selectedWife.value.birth_date)
      if (marriageDate < wifeBirth) {
        marriageDateError.value = 'La date de mariage ne peut pas être antérieure à la naissance de la femme.'
        return
      }
    }
    if (selectedWife.value.death_date) {
      const wifeDeath = new Date(selectedWife.value.death_date)
      if (marriageDate > wifeDeath) {
        marriageDateError.value = 'La date de mariage ne peut pas être postérieure au décès de la femme.'
        return
      }
    }
  }
}

// Charger les détails d'une personne sélectionnée
async function loadPersonDetails(type: 'husband' | 'wife', personId: string) {
  try {
    // Si aucun sélectionné, réinitialiser l'aperçu
    if (!personId) {
      if (type === 'husband') {
        selectedHusband.value = null
      } else {
        selectedWife.value = null
      }
      // Revalider la date si besoin (pour nettoyer un éventuel message)
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
    
    // Revalider la date de mariage si elle est déjà saisie
    if (marriage_date.value) {
      validateMarriageDate()
    }
  } catch (error) {
    console.error('Erreur lors du chargement des détails de la personne:', error)
  }
}

// Ouvrir modale de création de personne
function openCreatePersonModal(type: 'husband' | 'wife') {
  currentParentType.value = type
  showCreatePersonModal.value = true
}

// Fermer la modale
function closeCreatePersonModal() {
  showCreatePersonModal.value = false
}

// Navigation vers l'accueil
const navigateToHome = () => {
  router.push('/')
}

// Gérer la création de personne depuis la modale
function handlePersonCreated(createdPerson: any) {
  // Ajouter la personne créée aux options et la sélectionner
  const newOption = {
    id: createdPerson.id,
    label: `${createdPerson.first_name} ${createdPerson.last_name}`
  }

  if (currentParentType.value === 'husband') {
    husbandOptions.value = [newOption, ...husbandOptions.value]
    husbandId.value = createdPerson.id
    selectedHusband.value = createdPerson
  } else if (currentParentType.value === 'wife') {
    wifeOptions.value = [newOption, ...wifeOptions.value]
    wifeId.value = createdPerson.id
    selectedWife.value = createdPerson
  } else if (currentParentType.value === 'child') {
    // Trouver le dernier enfant ajouté et le remplir avec la personne créée
    const lastChildIndex = children.value.length - 1
    if (lastChildIndex >= 0) {
      const newOption = {
        id: createdPerson.id,
        label: `${createdPerson.first_name} ${createdPerson.last_name}${createdPerson.birth_date ? ' • n. ' + createdPerson.birth_date : ''}`
      }
      childOptions.value = [newOption, ...childOptions.value]
      children.value[lastChildIndex].id = createdPerson.id
      children.value[lastChildIndex].label = newOption.label
    }
  }

  // Fermer la modale
  closeCreatePersonModal()
  
  // Afficher un message de succès
  success.value = `Personne "${createdPerson.first_name} ${createdPerson.last_name}" créée avec succès`
  setTimeout(() => { success.value = '' }, 3000)
}

// Gestion des enfants
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
    
    // Mettre à jour le label de l'enfant
    const childIndex = children.value.findIndex(child => child.id === childId)
    if (childIndex !== -1) {
      children.value[childIndex].label = `${person.first_name} ${person.last_name}`
    }
  } catch (error) {
    console.error('Erreur lors du chargement des détails de l\'enfant:', error)
  }
}

// Gestion des événements
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

async function submit() {
  console.log('Submit function called')
  error.value = ''
  success.value = ''
  marriageDateError.value = ''
  
  // Validation de la date de mariage avant soumission
  validateMarriageDate()
  if (marriageDateError.value) {
    error.value = marriageDateError.value
    return
  }
  
  submitting.value = true
  try {
  // Validation minimale: au moins un parent
  if (!husbandId.value && !wifeId.value) {
    error.value = 'Au moins un parent est requis.'
    submitting.value = false
    return
  }
    const res = await familyService.createFamily(payload.value)
    const familyId = res.data.id
    
    // Créer les relations enfant-famille
    if (children.value.length > 0) {
      for (const child of children.value) {
        try {
          await childService.createChild({
            family_id: familyId,
            child_id: child.id
          })
        } catch (childError: any) {
          console.error(`Erreur lors de l'ajout de l'enfant ${child.label}:`, childError)
          // On continue même si un enfant échoue
        }
      }
    }
    
    // Créer les événements familiaux
    if (events.value.length > 0) {
      for (const event of events.value) {
        try {
          await eventService.createEvent({
            family_id: familyId,
            type: event.type,
            date: event.date || null,
            place: event.place || null,
            description: event.description || null
          })
        } catch (eventError: any) {
          console.error(`Erreur lors de l'ajout de l'événement ${event.type}:`, eventError)
          // On continue même si un événement échoue
        }
      }
    }
    
    const childCount = children.value.length
    const eventCount = events.value.length
    let message = 'Famille créée'
    if (childCount > 0) message += ` avec ${childCount} enfant${childCount > 1 ? 's' : ''}`
    if (eventCount > 0) message += `${childCount > 0 ? ' et' : ' avec'} ${eventCount} événement${eventCount > 1 ? 's' : ''}`
    success.value = message + '.'
    
    // Reset simple
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
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Erreur lors de la création de la famille'
  } finally {
    submitting.value = false
  }
}

</script>

<template>
  <div class="create-family-view">
    <div class="create-family">
      <div class="page-header">
        <div class="header-content">
          <div class="header-text">
            <h2>👨‍👩‍👧‍👦 Créer une famille</h2>
            <p>Créez une nouvelle famille en ajoutant les parents et les informations de mariage</p>
          </div>
          <button @click="navigateToHome" class="back-to-home-btn" data-cy="back-to-home">
            🏠 Retour à l'accueil
          </button>
        </div>
      </div>
      
      <form @submit.prevent="submit" class="family-form">
        <!-- Parents Section -->
        <div class="form-section">
          <div class="section-header">
            <h3>👫 Parents</h3>
            <p>Ajoutez un ou deux parents à la famille</p>
          </div>
          
          <div class="parents-grid">
            <!-- Mari -->
            <div class="parent-card">
              <div class="parent-header">
                <h4>👨 Mari</h4>
                <span class="required-badge">Optionnel</span>
              </div>
              
              <div class="search-container">
                <input
                  v-model="queryHusband"
                  type="text"
                  placeholder="Rechercher un mari existant..."
                  class="search-input"
                  data-cy="search-husband"
                  @input="onInputSearch('husband')"
                />
                <select
                  v-model="husbandId"
                  class="person-select"
                  data-cy="select-husband"
                  @change="loadPersonDetails('husband', husbandId)"
                >
                  <option value="">— Aucun —</option>
                  <option
                    v-for="option in husbandOptions"
                    :key="option.id"
                    :value="option.id"
                  >
                    {{ option.label }}
                  </option>
                </select>
                <button
                  type="button"
                  class="create-person-btn"
                  data-cy="create-husband-btn"
                  @click="openCreatePersonModal('husband')"
                >
                  ➕ Créer
                </button>
              </div>
              
              <!-- Aperçu du mari sélectionné -->
              <div v-if="selectedHusband" class="person-preview" data-cy="preview-husband">
                <div class="person-info">
                  <strong>{{ selectedHusband.first_name }} {{ selectedHusband.last_name }}</strong>
                  <span class="person-sex">{{ selectedHusband.sex === 'M' ? '♂' : selectedHusband.sex === 'F' ? '♀' : '⚥' }}</span>
                </div>
                <div v-if="selectedHusband.birth_date || selectedHusband.death_date" class="person-dates">
                  <span v-if="selectedHusband.birth_date">Né: {{ selectedHusband.birth_date }}</span>
                  <span v-if="selectedHusband.death_date">Décédé: {{ selectedHusband.death_date }}</span>
                </div>
                <div v-if="selectedHusband.birth_place || selectedHusband.death_place" class="person-places">
                  <span v-if="selectedHusband.birth_place">Lieu de naissance: {{ selectedHusband.birth_place }}</span>
                  <span v-if="selectedHusband.death_place">Lieu de décès: {{ selectedHusband.death_place }}</span>
                </div>
                <div v-if="selectedHusband.notes" class="person-notes">
                  Notes: {{ selectedHusband.notes }}
                </div>
              </div>
            </div>

            <!-- Femme -->
            <div class="parent-card">
              <div class="parent-header">
                <h4>👩 Femme</h4>
                <span class="required-badge">Optionnel</span>
              </div>
              
              <div class="search-container">
                <input
                  v-model="queryWife"
                  type="text"
                  placeholder="Rechercher une femme existante..."
                  class="search-input"
                  data-cy="search-wife"
                  @input="onInputSearch('wife')"
                />
                <select
                  v-model="wifeId"
                  class="person-select"
                  data-cy="select-wife"
                  @change="loadPersonDetails('wife', wifeId)"
                >
                  <option value="">— Aucun —</option>
                  <option
                    v-for="option in wifeOptions"
                    :key="option.id"
                    :value="option.id"
                  >
                    {{ option.label }}
                  </option>
                </select>
                <button
                  type="button"
                  class="create-person-btn"
                  data-cy="create-wife-btn"
                  @click="openCreatePersonModal('wife')"
                >
                  ➕ Créer
                </button>
              </div>
              
              <!-- Aperçu de la femme sélectionnée -->
              <div v-if="selectedWife" class="person-preview" data-cy="preview-wife">
                <div class="person-info">
                  <strong>{{ selectedWife.first_name }} {{ selectedWife.last_name }}</strong>
                  <span class="person-sex">{{ selectedWife.sex === 'M' ? '♂' : selectedWife.sex === 'F' ? '♀' : '⚥' }}</span>
                </div>
                <div v-if="selectedWife.birth_date || selectedWife.death_date" class="person-dates">
                  <span v-if="selectedWife.birth_date">Née: {{ selectedWife.birth_date }}</span>
                  <span v-if="selectedWife.death_date">Décédée: {{ selectedWife.death_date }}</span>
                </div>
                <div v-if="selectedWife.birth_place || selectedWife.death_place" class="person-places">
                  <span v-if="selectedWife.birth_place">Lieu de naissance: {{ selectedWife.birth_place }}</span>
                  <span v-if="selectedWife.death_place">Lieu de décès: {{ selectedWife.death_place }}</span>
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
            <h3>💒 Informations de mariage</h3>
            <p>Ajoutez les détails du mariage (optionnel)</p>
          </div>
          
          <div class="marriage-fields">
            <div class="form-group">
              <label for="marriage_date">📅 Date de mariage</label>
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
              <label for="marriage_place">📍 Lieu de mariage</label>
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
            <h3>📅 Événements</h3>
            <p>Ajoutez des événements liés à cette famille</p>
          </div>
          
          <div class="events-section">
            <button
              type="button"
              class="add-event-btn"
              data-cy="add-event-btn"
              @click="addEvent"
            >
              ➕ Ajouter un événement
            </button>
            
            <div v-for="(event, index) in events" :key="index" class="event-form" :data-cy="`event-${index}`">
              <div class="event-header">
                <h4>Événement {{ index + 1 }}</h4>
                <button
                  type="button"
                  class="remove-event-btn"
                  :data-cy="`remove-event-${index}`"
                  @click="removeEvent(index)"
                >
                  🗑️ Supprimer
                </button>
              </div>
              
              <div class="event-fields">
                <div class="form-group">
                  <label>Type d'événement</label>
                  <select v-model="event.type" :data-cy="`event-type-${index}`">
                    <option value="">Sélectionner un type</option>
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
                  <label>Lieu</label>
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
                    placeholder="Description de l'événement..."
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
            <h3>👶 Enfants</h3>
            <p>Ajoutez des enfants à cette famille</p>
          </div>
          
          <div class="children-section">
            <button
              type="button"
              class="add-child-btn"
              data-cy="add-child-button"
              @click="addChild"
            >
              ➕ Ajouter un enfant
            </button>
            
            <div v-for="(child, index) in children" :key="index" class="child-form" data-cy="children-list">
              <div class="child-header">
                <h4>Enfant {{ index + 1 }}</h4>
                <button
                  type="button"
                  class="remove-child-btn"
                  data-cy="remove-child-btn"
                  @click="removeChild(index)"
                >
                  🗑️ Supprimer
                </button>
              </div>
              
              <div class="child-fields">
                <div class="search-container">
                  <input
                    v-model="queryChild"
                    type="text"
                    placeholder="Rechercher un enfant existant..."
                    class="search-input"
                    data-cy="search-child"
                    @input="onInputSearchChild"
                  />
                  <select
                    v-model="child.id"
                    class="person-select"
                    data-cy="select-child"
                    @change="loadChildDetails(child.id)"
                  >
                    <option value="">— Aucun —</option>
                    <option
                      v-for="option in childOptions"
                      :key="option.id"
                      :value="option.id"
                    >
                      {{ option.label }}
                    </option>
                  </select>
                  <button
                    type="button"
                    class="create-person-btn"
                    data-cy="create-child-button"
                    @click="openCreatePersonModal('child')"
                  >
                    ➕ Créer
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
            <p>Ajoutez des notes sur cette famille</p>
          </div>
          
          <div class="form-group">
            <label for="notes">Notes sur la famille</label>
            <textarea
              id="notes"
              v-model="notes"
              placeholder="Notes sur la famille, informations supplémentaires..."
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
            {{ submitting ? 'Création en cours...' : '✨ Créer la famille' }}
          </button>
        </div>
      </form>

      <!-- Messages d'erreur et de succès -->
      <div v-if="error" class="error-message">
        <div class="error-icon">⚠️</div>
        <div class="error-content">
          <h4>Erreur</h4>
          <p>{{ error }}</p>
        </div>
      </div>
      
      <div v-if="success" class="success-message">
        <div class="success-icon">✅</div>
        <div class="success-content">
          <h4>Succès</h4>
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

.search-input {
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 0.95rem;
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.person-select {
  padding: 0.75rem;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  font-size: 0.95rem;
  background: white;
  transition: all 0.3s ease;
}

.person-select:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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