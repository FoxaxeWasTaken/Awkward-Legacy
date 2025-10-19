<script setup lang="ts">
import { ref, computed } from 'vue'
import { familyService, type CreateFamily } from '@/services/familyService'
import { personService } from '@/services/personService'
import { childService } from '@/services/childService'
import CreatePersonModal from '@/components/CreatePersonModal.vue'

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
let debounceTimer: number | undefined

function debounce(fn: () => void, delay = 300) {
  if (debounceTimer) window.clearTimeout(debounceTimer)
  debounceTimer = window.setTimeout(fn, delay)
}

async function searchPersons(target: 'husband' | 'wife') {
  const q = target === 'husband' ? queryHusband.value : queryWife.value
  if (!q) {
    if (target === 'husband') husbandOptions.value = []
    else wifeOptions.value = []
    return
  }
  try {
    const res = await personService.searchPersonsByName(q)
    const list = (res.data || []).map((p: any) => ({
      id: p.id,
      label: `${p.first_name} ${p.last_name} (${p.sex})${p.birth_date ? ' • n. ' + p.birth_date : ''}${p.birth_place ? ' • ' + p.birth_place : ''}`,
    }))
    if (target === 'husband') husbandOptions.value = list
    else wifeOptions.value = list
  } catch (_e) {
    // En cas d'erreur réseau / serveur, ne pas faire échouer l'app
    if (target === 'husband') husbandOptions.value = []
    else wifeOptions.value = []
  }
}

function onInputSearch(target: 'husband' | 'wife') {
  debounce(() => searchPersons(target))
}

// Recherche d'enfants
async function searchChildren() {
  if (!queryChild.value) {
    childOptions.value = []
    return
  }
  try {
    const res = await personService.searchPersonsByName(queryChild.value)
    const list = (res.data || []).map((p: any) => ({
      id: p.id,
      label: `${p.first_name} ${p.last_name} (${p.sex})${p.birth_date ? ' • n. ' + p.birth_date : ''}${p.birth_place ? ' • ' + p.birth_place : ''}`,
    }))
    // Filtrer les personnes déjà ajoutées comme enfants, mari ou femme
    childOptions.value = list.filter((opt: PersonOption) => 
      !children.value.some(c => c.id === opt.id) && 
      opt.id !== husbandId.value && 
      opt.id !== wifeId.value
    )
  } catch (_e) {
    childOptions.value = []
  }
}

function onChildSearch() {
  debounce(() => searchChildren())
}

// Ajouter un enfant existant
function addExistingChild(childId: string) {
  if (!childId) return
  const child = childOptions.value.find(c => c.id === childId)
  if (child && !children.value.some(c => c.id === childId)) {
    children.value.push({ id: child.id, label: child.label })
    queryChild.value = ''
    childOptions.value = []
  }
}

// Supprimer un enfant
function removeChild(childId: string) {
  children.value = children.value.filter(c => c.id !== childId)
}

// Ouvrir la modale pour créer un enfant
function openCreateChildModal() {
  currentParentType.value = 'child'
  showCreatePersonModal.value = true
}

// Validation de la date de mariage
function validateMarriageDate() {
  marriageDateError.value = ''
  if (!marriage_date.value) return

  const marriageDate = new Date(marriage_date.value)
  const today = new Date()
  
  // Vérifier que la date n'est pas dans le futur
  if (marriageDate > today) {
    marriageDateError.value = 'La date de mariage ne peut pas être dans le futur'
    return
  }

  // Vérifier par rapport aux dates de naissance des parents
  if (selectedHusband.value?.birth_date) {
    const husbandBirth = new Date(selectedHusband.value.birth_date)
    if (marriageDate < husbandBirth) {
      marriageDateError.value = 'La date de mariage ne peut pas être avant la naissance du parent 1'
      return
    }
  }

  if (selectedWife.value?.birth_date) {
    const wifeBirth = new Date(selectedWife.value.birth_date)
    if (marriageDate < wifeBirth) {
      marriageDateError.value = 'La date de mariage ne peut pas être avant la naissance du parent 2'
      return
    }
  }

  // Vérifier par rapport aux dates de décès des parents
  if (selectedHusband.value?.death_date) {
    const husbandDeath = new Date(selectedHusband.value.death_date)
    if (marriageDate > husbandDeath) {
      marriageDateError.value = 'La date de mariage ne peut pas être après le décès du parent 1'
      return
    }
  }

  if (selectedWife.value?.death_date) {
    const wifeDeath = new Date(selectedWife.value.death_date)
    if (marriageDate > wifeDeath) {
      marriageDateError.value = 'La date de mariage ne peut pas être après le décès du parent 2'
      return
    }
  }
}

// Charger les données complètes d'une personne sélectionnée
async function loadPersonDetails(personId: string, type: 'husband' | 'wife') {
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
    // Ajouter l'enfant créé à la liste
    children.value.push({
      id: createdPerson.id,
      label: `${createdPerson.first_name} ${createdPerson.last_name}${createdPerson.birth_date ? ' • n. ' + createdPerson.birth_date : ''}`
    })
  }

  // Fermer la modale
  closeCreatePersonModal()
  
  // Afficher un message de succès
  success.value = `Personne "${createdPerson.first_name} ${createdPerson.last_name}" créée avec succès`
  setTimeout(() => { success.value = '' }, 3000)
}

// (Pas de modale de liaison: la liaison se fait via l'auto-complétion)

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
    
    const childCount = children.value.length
    success.value = `Famille créée${childCount > 0 ? ` avec ${childCount} enfant${childCount > 1 ? 's' : ''}` : ''}.`
    
    // Reset simple
    husbandId.value = ''
    wifeId.value = ''
    marriage_date.value = ''
    marriage_place.value = ''
    notes.value = ''
    children.value = []
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
  <div class="create-family">
    <h2>Créer une famille</h2>
    <form @submit.prevent="submit">
      <fieldset>
        <legend>Parents</legend>
        <div class="parent-field">
          <label>Parent 1 (Husband)</label>
          <div class="parent-input-group">
            <input
              v-model="queryHusband"
              @input="onInputSearch('husband')"
              placeholder="Rechercher une personne..."
              data-cy="search-husband"
            />
            <button type="button" @click="openCreatePersonModal('husband')" class="btn-secondary">
              Créer
            </button>
            
          </div>
          <select v-model="husbandId" @change="loadPersonDetails(husbandId, 'husband')" data-cy="select-husband">
            <option value="">— Aucun —</option>
            <option v-for="opt in husbandOptions" :key="opt.id" :value="opt.id">{{ opt.label }}</option>
          </select>
          <div v-if="selectedHusband" class="person-preview" data-cy="preview-husband">
            <strong>{{ selectedHusband.first_name }} {{ selectedHusband.last_name }}</strong>
            <div class="meta">
              <span>Sexe: {{ selectedHusband.sex }}</span>
              <span v-if="selectedHusband.birth_date">Naissance: {{ selectedHusband.birth_date }}</span>
              <span v-if="selectedHusband.birth_place">({{ selectedHusband.birth_place }})</span>
              <span v-if="selectedHusband.death_date"> • Décès: {{ selectedHusband.death_date }}</span>
              <span v-if="selectedHusband.death_place">({{ selectedHusband.death_place }})</span>
            </div>
            <div v-if="selectedHusband.notes" class="notes">{{ selectedHusband.notes }}</div>
          </div>
        </div>
        <div class="parent-field">
          <label>Parent 2 (Wife)</label>
          <div class="parent-input-group">
            <input
              v-model="queryWife"
              @input="onInputSearch('wife')"
              placeholder="Rechercher une personne..."
              data-cy="search-wife"
            />
            <button type="button" @click="openCreatePersonModal('wife')" class="btn-secondary">
              Créer
            </button>
            
          </div>
          <select v-model="wifeId" @change="loadPersonDetails(wifeId, 'wife')" data-cy="select-wife">
            <option value="">— Aucun —</option>
            <option v-for="opt in wifeOptions" :key="opt.id" :value="opt.id">{{ opt.label }}</option>
          </select>
          <div v-if="selectedWife" class="person-preview" data-cy="preview-wife">
            <strong>{{ selectedWife.first_name }} {{ selectedWife.last_name }}</strong>
            <div class="meta">
              <span>Sexe: {{ selectedWife.sex }}</span>
              <span v-if="selectedWife.birth_date">Naissance: {{ selectedWife.birth_date }}</span>
              <span v-if="selectedWife.birth_place">({{ selectedWife.birth_place }})</span>
              <span v-if="selectedWife.death_date"> • Décès: {{ selectedWife.death_date }}</span>
              <span v-if="selectedWife.death_place">({{ selectedWife.death_place }})</span>
            </div>
            <div v-if="selectedWife.notes" class="notes">{{ selectedWife.notes }}</div>
          </div>
        </div>
      </fieldset>

      <fieldset>
        <legend>Enfants ({{ children.length }})</legend>
        <div class="children-section">
          <div class="add-child-controls">
            <div class="search-and-select">
              <label>Rechercher et ajouter un enfant existant</label>
              <input 
                v-model="queryChild"
                @input="onChildSearch"
                placeholder="Nom ou prénom de l'enfant"
                data-cy="search-child"
              />
              <select 
                @change="(e) => { addExistingChild((e.target as HTMLSelectElement).value); (e.target as HTMLSelectElement).value = '' }"
                data-cy="select-child"
              >
                <option value="">— Sélectionner —</option>
                <option v-for="opt in childOptions" :key="opt.id" :value="opt.id">{{ opt.label }}</option>
              </select>
            </div>
            <div class="button-group">
              <button type="button" @click="openCreateChildModal" data-cy="create-child-button">
                Créer un nouvel enfant
              </button>
            </div>
          </div>

          <div v-if="children.length > 0" class="children-list">
            <h4>Enfants ajoutés :</h4>
            <ul data-cy="children-list">
              <li v-for="child in children" :key="child.id" class="child-item">
                <span>{{ child.label }}</span>
                <button 
                  type="button" 
                  @click="removeChild(child.id)" 
                  class="remove-btn"
                  :data-cy="`remove-child-${child.id}`"
                >
                  ✕
                </button>
              </li>
            </ul>
          </div>
        </div>
      </fieldset>

      <fieldset>
        <legend>Informations de mariage</legend>
        <div>
          <label>Date de mariage</label>
          <input 
            type="date" 
            v-model="marriage_date" 
            @change="validateMarriageDate"
            data-cy="marriage-date" 
          />
          <div v-if="marriageDateError" class="field-error">{{ marriageDateError }}</div>
        </div>
        <div>
          <label>Lieu de mariage</label>
          <input v-model="marriage_place" data-cy="marriage-place" />
        </div>
        <div>
          <label>Notes</label>
          <textarea v-model="notes" data-cy="notes"></textarea>
        </div>
      </fieldset>

      <button type="submit" :disabled="submitting" data-cy="submit-family">Créer</button>
    </form>

    <div v-if="error" class="error">{{ error }}</div>
    <div v-if="success" class="success">{{ success }}</div>
  </div>

  <!-- Modale de création de personne -->
  <CreatePersonModal
    :show="showCreatePersonModal"
    :parent-type="currentParentType"
    @close="closeCreatePersonModal"
    @person-created="handlePersonCreated"
  />
  
</template>

<style scoped>
.create-family {
  max-width: 720px;
  margin: 2em auto;
  padding: 2em;
  border: 1px solid #ddd;
  border-radius: 12px;
}
fieldset { margin-bottom: 1.5em; }
.parent-field { margin-bottom: 1em; }
label { display: block; font-weight: 600; margin-bottom: 0.3em; }
input, select, textarea { width: 100%; padding: 0.5em; box-sizing: border-box; }

.parent-input-group {
  display: flex;
  gap: 0.5em;
  margin-bottom: 0.5em;
}
.parent-input-group input {
  flex: 1;
}
.btn-secondary {
  padding: 0.5em 1em;
  background: #f5f5f5;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9em;
}
.btn-secondary:hover {
  background: #e5e5e5;
}

.error { color: #b00020; margin-top: 1em; }
.success { color: #0a7a2f; margin-top: 1em; }
.field-error { color: #b00020; font-size: 0.9em; margin-top: 0.3em; }
 
.person-preview {
  margin-top: 0.5em;
  padding: 0.75em;
  background: #fafafa;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
}
.person-preview .meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5em 1em;
  color: #555;
  margin-top: 0.25em;
}
.person-preview .notes {
  margin-top: 0.5em;
  font-style: italic;
  color: #666;
}

/* Styles pour la section enfants */
.children-section {
  margin-top: 1em;
}

.add-child-controls {
  display: flex;
  flex-direction: column;
  gap: 1em;
  margin-bottom: 1.5em;
}

.search-and-select {
  display: flex;
  flex-direction: column;
  gap: 0.5em;
}

.button-group {
  display: flex;
  gap: 0.5em;
}

.button-group button {
  padding: 0.6em 1.2em;
  background: #2196f3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.95em;
}

.button-group button:hover {
  background: #1976d2;
}

.children-list {
  margin-top: 1.5em;
}

.children-list h4 {
  margin-bottom: 0.75em;
  color: #333;
  font-weight: 600;
}

.children-list ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.child-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75em 1em;
  margin-bottom: 0.5em;
  background: #f5f5f5;
  border: 1px solid #e5e5e5;
  border-radius: 6px;
}

.child-item span {
  flex: 1;
  color: #333;
}

.remove-btn {
  padding: 0.3em 0.6em;
  background: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  font-weight: bold;
  line-height: 1;
}

.remove-btn:hover {
  background: #d32f2f;
}
</style>


