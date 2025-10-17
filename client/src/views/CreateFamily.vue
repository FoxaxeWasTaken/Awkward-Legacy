<script setup lang="ts">
import { ref, computed } from 'vue'
import { familyService, type CreateFamily } from '@/services/familyService'
import { personService } from '@/services/personService'

type PersonOption = {
  id: string
  label: string
}

const husbandId = ref<string>('')
const wifeId = ref<string>('')
const marriage_date = ref<string>('')
const marriage_place = ref<string>('')
const notes = ref<string>('')

const submitting = ref(false)
const error = ref('')
const success = ref('')

// Données des parents sélectionnés pour validation
const selectedHusband = ref<any>(null)
const selectedWife = ref<any>(null)
const marriageDateError = ref('')

// Modales
const showCreatePersonModal = ref(false)
const showLinkPersonModal = ref(false)
const currentParentType = ref<'husband' | 'wife'>('husband')

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
  const res = await personService.searchPersonsByName(q)
  const list = (res.data || []).map((p: any) => ({
    id: p.id,
    label: `${p.first_name} ${p.last_name} (${p.sex})${p.birth_date ? ' • n. ' + p.birth_date : ''}${p.birth_place ? ' • ' + p.birth_place : ''}`,
  }))
  if (target === 'husband') husbandOptions.value = list
  else wifeOptions.value = list
}

function onInputSearch(target: 'husband' | 'wife') {
  debounce(() => searchPersons(target))
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

// Ouvrir modale de liaison de personne
function openLinkPersonModal(type: 'husband' | 'wife') {
  currentParentType.value = type
  showLinkPersonModal.value = true
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
      return
    }
    const res = await familyService.createFamily(payload.value)
    success.value = 'Famille créée.'
    // Reset simple
    husbandId.value = ''
    wifeId.value = ''
    marriage_date.value = ''
    marriage_place.value = ''
    notes.value = ''
    husbandOptions.value = []
    wifeOptions.value = []
    queryHusband.value = ''
    queryWife.value = ''
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
            <button type="button" @click="openLinkPersonModal('husband')" class="btn-secondary">
              Lier
            </button>
          </div>
          <select v-model="husbandId" @change="loadPersonDetails(husbandId, 'husband')" data-cy="select-husband">
            <option value="">— Aucun —</option>
            <option v-for="opt in husbandOptions" :key="opt.id" :value="opt.id">{{ opt.label }}</option>
          </select>
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
            <button type="button" @click="openLinkPersonModal('wife')" class="btn-secondary">
              Lier
            </button>
          </div>
          <select v-model="wifeId" @change="loadPersonDetails(wifeId, 'wife')" data-cy="select-wife">
            <option value="">— Aucun —</option>
            <option v-for="opt in wifeOptions" :key="opt.id" :value="opt.id">{{ opt.label }}</option>
          </select>
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
</style>


