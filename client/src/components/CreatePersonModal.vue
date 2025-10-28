<template>
  <div v-if="show" class="modal-overlay" @click="closeModal">
    <div class="modal" @click.stop>
      <div class="modal-header">
        <h3>Create a New Person</h3>
        <button class="close-button close-btn" @click="closeModal" data-cy="close-modal">×</button>
      </div>
      
      <form @submit.prevent="createPerson" class="modal-body">
        <div class="form-group">
          <label for="first_name">First Name *</label>
          <input
            id="first_name"
            v-model="newPerson.first_name"
            type="text"
            required
            data-cy="new-person-first-name"
            :disabled="creatingPerson"
          />
        </div>

        <div class="form-group">
          <label for="last_name">Last Name *</label>
          <input
            id="last_name"
            v-model="newPerson.last_name"
            type="text"
            required
            data-cy="new-person-last-name"
            :disabled="creatingPerson"
          />
        </div>

        <div class="form-group">
          <label for="sex">Gender</label>
          <select
            id="sex"
            v-model="newPerson.sex"
            data-cy="new-person-sex"
            :disabled="creatingPerson"
          >
            <option value="U">Undefined</option>
            <option value="M">Male</option>
            <option value="F">Female</option>
          </select>
        </div>

        <div class="form-group">
          <label for="birth_date">Birth Date</label>
          <input
            id="birth_date"
            v-model="newPerson.birth_date"
            type="date"
            data-cy="new-person-birth-date"
            :disabled="creatingPerson"
          />
        </div>

        <div class="form-group">
          <label for="birth_place">Birth Place</label>
          <input
            id="birth_place"
            v-model="newPerson.birth_place"
            type="text"
            data-cy="new-person-birth-place"
            :disabled="creatingPerson"
          />
        </div>

        <div class="form-group">
          <label for="death_date">Death Date</label>
          <input
            id="death_date"
            v-model="newPerson.death_date"
            type="date"
            data-cy="new-person-death-date"
            :disabled="creatingPerson"
          />
        </div>

        <div class="form-group">
          <label for="death_place">Death Place</label>
          <input
            id="death_place"
            v-model="newPerson.death_place"
            type="text"
            data-cy="new-person-death-place"
            :disabled="creatingPerson"
          />
        </div>

        <div class="form-group">
          <label for="occupation">Occupation</label>
          <input
            id="occupation"
            v-model="newPerson.occupation"
            type="text"
            data-cy="new-person-occupation"
            :disabled="creatingPerson"
          />
        </div>

        <div class="form-group">
          <label for="notes">Notes</label>
          <textarea
            id="notes"
            v-model="newPerson.notes"
            data-cy="new-person-notes"
            :disabled="creatingPerson"
          ></textarea>
        </div>

        <div v-if="personCreationError" class="error-message field-error">
          {{ personCreationError }}
        </div>

        <div class="modal-footer">
          <button
            type="button"
            @click="closeModal"
            class="cancel-button"
            data-cy="cancel-person-creation"
            :disabled="creatingPerson"
          >
            Cancel
          </button>
          <button
            type="submit"
            class="submit-button"
            data-cy="create-person-submit"
            :disabled="creatingPerson"
          >
            {{ creatingPerson ? 'Creating...' : 'Create' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { personService } from '@/services/personService'
import type { Person } from '@/types/family'

interface Props {
  show: boolean
  parentType: 'husband' | 'wife' | 'child'
}

const _props = defineProps<Props>()

type ApiError = {
  response?: { data?: { detail?: string } }
  message?: string
}

const emit = defineEmits<{
  close: []
  personCreated: [person: Person]
}>()

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

function validateRequiredNames(): string | null {
  const first = newPerson.value.first_name.trim()
  const last = newPerson.value.last_name.trim()
  return !first || !last ? 'First name and last name are required' : null
}

function buildPayload() {
  return {
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
}

const createPerson = async () => {
  const namesError = validateRequiredNames()
  if (namesError) {
    personCreationError.value = namesError
    return
  }

  creatingPerson.value = true
  personCreationError.value = ''

  try {
    const response = await personService.createPerson(buildPayload())
    const createdPerson = response.data
    emit('personCreated', createdPerson)
    resetForm()
  } catch (err: unknown) {
    const apiErr = err as ApiError
    personCreationError.value = apiErr.response?.data?.detail || apiErr.message || 'Error creating person'
  } finally {
    creatingPerson.value = false
  }
}

// Expose to avoid false-positive "assigned but never used" lint errors
defineExpose({ closeModal, createPerson })
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 0;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-button:hover {
  color: #374151;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 4px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group input:disabled,
.form-group select:disabled,
.form-group textarea:disabled {
  background-color: #f9fafb;
  color: #6b7280;
  cursor: not-allowed;
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.error-message {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.cancel-button,
.submit-button {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-button {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.cancel-button:hover:not(:disabled) {
  background-color: #e5e7eb;
}

.submit-button {
  background-color: #3b82f6;
  color: white;
  border: 1px solid #3b82f6;
}

.submit-button:hover:not(:disabled) {
  background-color: #2563eb;
}

.submit-button:disabled,
.cancel-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
