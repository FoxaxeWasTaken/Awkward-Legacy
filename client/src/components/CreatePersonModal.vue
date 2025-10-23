<script setup lang="ts">
import { ref } from 'vue'
import { personService } from '@/services/personService'

// Props
interface Props {
  show: boolean
  parentType: 'husband' | 'wife'
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  close: []
  personCreated: [person: any]
}>()

// Form data
const newPerson = ref({
  first_name: '',
  last_name: '',
  sex: 'U' as 'M' | 'F' | 'U',
  birth_date: '',
  birth_place: '',
  death_date: '',
  death_place: '',
  occupation: '',
  notes: ''
})

const creatingPerson = ref(false)
const personCreationError = ref('')

// Fonctions
const resetForm = () => {
  newPerson.value.first_name = ''
  newPerson.value.last_name = ''
  newPerson.value.sex = 'U'
  newPerson.value.birth_date = ''
  newPerson.value.birth_place = ''
  newPerson.value.death_date = ''
  newPerson.value.death_place = ''
  newPerson.value.occupation = ''
  newPerson.value.notes = ''
  personCreationError.value = ''
}

const closeModal = () => {
  resetForm()
  emit('close')
}

const createPerson = async () => {
  if (!newPerson.value.first_name.trim() || !newPerson.value.last_name.trim()) {
    personCreationError.value = 'Le prénom et le nom sont obligatoires'
    return
  }

  creatingPerson.value = true
  personCreationError.value = ''

  try {
    const personData = {
      first_name: newPerson.value.first_name.trim(),
      last_name: newPerson.value.last_name.trim(),
      sex: newPerson.value.sex,
      birth_date: newPerson.value.birth_date || null,
      birth_place: newPerson.value.birth_place.trim() || null,
      death_date: newPerson.value.death_date || null,
      death_place: newPerson.value.death_place.trim() || null,
      occupation: newPerson.value.occupation.trim() || null,
      notes: newPerson.value.notes.trim() || null
    }

    const response = await personService.createPerson(personData)
    const createdPerson = response.data
    
    // Emit event with created person
    emit('personCreated', createdPerson)
    
    // Reset and close
    resetForm()

  } catch (e: any) {
    personCreationError.value = e?.response?.data?.detail || 'Erreur lors de la création de la personne'
  } finally {
    creatingPerson.value = false
  }
}
</script>

<template>
  <div v-if="show" class="modal-overlay" @click="closeModal">
    <div class="modal" @click.stop>
      <div class="modal-header">
        <h3>Créer une nouvelle personne</h3>
        <button type="button" @click="closeModal" class="close-btn">&times;</button>
      </div>
      
      <form @submit.prevent="createPerson" class="modal-body">
        <div class="form-row">
          <div class="form-group">
            <label>Prénom *</label>
            <input 
              v-model="newPerson.first_name" 
              type="text" 
              required 
              placeholder="Prénom"
              data-cy="new-person-first-name"
            />
          </div>
          <div class="form-group">
            <label>Nom *</label>
            <input 
              v-model="newPerson.last_name" 
              type="text" 
              required 
              placeholder="Nom"
              data-cy="new-person-last-name"
            />
          </div>
        </div>

        <div class="form-group">
          <label>Sexe</label>
          <select v-model="newPerson.sex" data-cy="new-person-sex">
            <option value="U">Non défini</option>
            <option value="M">Homme</option>
            <option value="F">Femme</option>
          </select>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Date de naissance</label>
            <input 
              v-model="newPerson.birth_date" 
              type="date" 
              data-cy="new-person-birth-date"
            />
          </div>
          <div class="form-group">
            <label>Lieu de naissance</label>
            <input 
              v-model="newPerson.birth_place" 
              type="text" 
              placeholder="Lieu de naissance"
              data-cy="new-person-birth-place"
            />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Date de décès</label>
            <input 
              v-model="newPerson.death_date" 
              type="date" 
              data-cy="new-person-death-date"
            />
          </div>
          <div class="form-group">
            <label>Lieu de décès</label>
            <input 
              v-model="newPerson.death_place" 
              type="text" 
              placeholder="Lieu de décès"
              data-cy="new-person-death-place"
            />
          </div>
        </div>

        <div class="form-group">
          <label>Profession</label>
          <input 
            v-model="newPerson.occupation" 
            type="text" 
            placeholder="Profession"
            data-cy="new-person-occupation"
          />
        </div>

        <div class="form-group">
          <label>Notes</label>
          <textarea 
            v-model="newPerson.notes" 
            placeholder="Notes supplémentaires..."
            data-cy="new-person-notes"
          ></textarea>
        </div>

        <div v-if="personCreationError" class="field-error">{{ personCreationError }}</div>

        <div class="modal-actions">
          <button type="button" @click="closeModal" class="btn-secondary">
            Annuler
          </button>
          <button type="submit" :disabled="creatingPerson" class="btn-primary" data-cy="create-person-submit">
            {{ creatingPerson ? 'Création...' : 'Créer la personne' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
/* Styles pour la modale */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5em;
  border-bottom: 1px solid #e5e5e5;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5em;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 1.5em;
}

.form-row {
  display: flex;
  gap: 1em;
  margin-bottom: 1em;
}

.form-row .form-group {
  flex: 1;
}

.form-group {
  margin-bottom: 1em;
}

.form-group label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.3em;
  color: #333;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.5em;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1em;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.modal-actions {
  display: flex;
  gap: 1em;
  justify-content: flex-end;
  margin-top: 2em;
  padding-top: 1em;
  border-top: 1px solid #e5e5e5;
}

.btn-secondary {
  padding: 0.75em 1.5em;
  background: #f5f5f5;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
}

.btn-secondary:hover {
  background: #e5e5e5;
}

.btn-primary {
  padding: 0.75em 1.5em;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1em;
  font-weight: 600;
}

.btn-primary:hover:not(:disabled) {
  background: #0056b3;
}

.btn-primary:disabled {
  background: #6c757d;
  cursor: not-allowed;
}

.field-error {
  color: #b00020;
  font-size: 0.9em;
  margin-top: 0.5em;
}
</style>


