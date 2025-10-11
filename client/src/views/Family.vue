<script setup lang="ts">
import { ref } from 'vue'
import { personService } from '../services/personService'

const form = ref({
  first_name: '',
  last_name: '',
  sex: 'U',
  birth_date: '',
  birth_place: '',
  death_date: '',
  death_place: '',
  notes: ''
})

const error = ref('')
const success = ref('')

const submitting = ref(false)

const submit = async () => {
  error.value = ''
  success.value = ''
  submitting.value = true
  try {
    // Prepare data, remove empty optional fields
    const data: any = { ...form.value }
    if (!data.birth_date) delete data.birth_date
    if (!data.birth_place) delete data.birth_place
    if (!data.death_date) delete data.death_date
    if (!data.death_place) delete data.death_place
    if (!data.notes) delete data.notes

    await personService.createPerson(data)
    success.value = 'Person created successfully!'
    // Optionally reset form
    form.value = {
      first_name: '',
      last_name: '',
      sex: 'U',
      birth_date: '',
      birth_place: '',
      death_date: '',
      death_place: '',
      notes: ''
    }
  } catch (e: any) {
    error.value = e?.response?.data?.detail || 'Failed to create person'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="create-person">
    <h2>Create Person</h2>
    <form @submit.prevent="submit">
      <div>
        <label>First Name *</label>
        <input v-model="form.first_name" required data-cy="first-name" />
      </div>
      <div>
        <label>Last Name *</label>
        <input v-model="form.last_name" required data-cy="last-name" />
      </div>
      <div>
        <label>Sex *</label>
        <select v-model="form.sex" required data-cy="sex" >
          <option value="M">Male</option>
          <option value="F">Female</option>
          <option value="U">Unknown</option>
        </select>
      </div>
      <div>
        <label>Birth Date</label>
        <input type="date" v-model="form.birth_date" data-cy="birth-date" />
      </div>
      <div>
        <label>Birth Place</label>
        <input v-model="form.birth_place" data-cy="birth-place" />
      </div>
      <div>
        <label>Death Date</label>
        <input type="date" v-model="form.death_date" data-cy="death-date" />
      </div>
      <div>
        <label>Death Place</label>
        <input v-model="form.death_place" data-cy="death-place" />
      </div>
      <div>
        <label>Notes</label>
        <textarea v-model="form.notes" data-cy="notes"></textarea>
      </div>
      <button type="submit" :disabled="submitting" data-cy="submit">Create</button>
    </form>
    <div v-if="error" style="color: red; margin-top: 1em;">{{ error }}</div>
    <div v-if="success" style="color: green; margin-top: 1em;">{{ success }}</div>
  </div>
</template>

<style scoped>
.create-person {
  max-width: 400px;
  margin: 2em auto;
  padding: 2em;
  border: 1px solid #ccc;
  border-radius: 8px;
}
.create-person form > div {
  margin-bottom: 1em;
}
.create-person label {
  display: block;
  margin-bottom: 0.3em;
  font-weight: bold;
}
.create-person input,
.create-person select,
.create-person textarea {
  width: 100%;
  padding: 0.4em;
  box-sizing: border-box;
}
.create-person button {
  padding: 0.5em 1.5em;
}
</style>
