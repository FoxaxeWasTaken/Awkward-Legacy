<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import apiService from '../services/api'
import type { UploadResult } from '../types/family'

const router = useRouter()

const isDragOver = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const selectedFile = ref<File | null>(null)
const uploadResult = ref<UploadResult | null>(null)
const error = ref('')
const isSuccess = ref<boolean>(false)

const handleDragOver = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = false
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  isDragOver.value = false
  
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    handleFileSelect(files[0])
  }
}

const handleFileInput = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    handleFileSelect(target.files[0])
  }
}

const handleFileSelect = (file: File) => {
  // Validate file type
  if (!file.name.toLowerCase().endsWith('.gw')) {
    error.value = 'Please select a valid GeneWeb file (.gw extension)'
    return
  }
  
  // Validate file size (max 10MB)
  if (file.size > 10 * 1024 * 1024) {
    error.value = 'File size must be less than 10MB'
    return
  }
  
  selectedFile.value = file
  error.value = ''
  uploadResult.value = null
  isSuccess.value = false
}

// Helper functions to reduce complexity
const startProgressSimulation = (): ReturnType<typeof setInterval> => {
  return setInterval(() => {
    if (uploadProgress.value < 90) {
      uploadProgress.value += Math.random() * 10
    }
  }, 100)
}

const handleUploadSuccess = (result: UploadResult) => {
  uploadResult.value = result
  isSuccess.value = true
  
  // Auto-navigate to family tree after 2 seconds
  setTimeout(() => {
    router.push('/manage')
  }, 2000)
}

const isErrorWithResponse = (err: unknown): err is { response?: { data?: { detail?: string } } } => {
  return Boolean(err && typeof err === 'object' && 'response' in err)
}

const extractErrorMessage = (err: unknown): string => {
  if (isErrorWithResponse(err)) {
    return err.response?.data?.detail || 'Failed to upload file. Please try again.'
  }
  return 'Failed to upload file. Please try again.'
}

const handleUploadError = (err: unknown) => {
  console.error('Upload error:', err)
  error.value = extractErrorMessage(err)
}

const uploadFile = async () => {
  if (!selectedFile.value) return
  
  isUploading.value = true
  uploadProgress.value = 0
  error.value = ''
  
  try {
    const progressInterval = startProgressSimulation()
    const result = await apiService.uploadFamilyFile(selectedFile.value)
    
    clearInterval(progressInterval)
    uploadProgress.value = 100
    handleUploadSuccess(result)
    
  } catch (err: unknown) {
    handleUploadError(err)
  } finally {
    isUploading.value = false
  }
}

const resetUpload = () => {
  selectedFile.value = null
  uploadResult.value = null
  error.value = ''
  isSuccess.value = false
  uploadProgress.value = 0
}

const goBack = () => {
  router.push('/')
}

onMounted(() => {
  // Check if API is available
  apiService.healthCheck().then((isHealthy) => {
    if (!isHealthy) {
      error.value = 'Unable to connect to the server. Please check your connection.'
    }
  })
})
</script>

<template>
  <div class="file-upload-view">
    <div class="upload-header">
      <button class="back-button" @click="goBack">← Back to Home</button>
      <h1 class="upload-title">📁 Upload Family File</h1>
      <p class="upload-subtitle">
        Upload your GeneWeb (.gw) file to import family data into the database
      </p>
    </div>

    <div class="upload-container">
      <!-- File Selection Area -->
      <div 
        v-if="!selectedFile && !isSuccess"
        class="upload-zone"
        :class="{ 'drag-over': isDragOver }"
        @dragover="handleDragOver"
        @dragleave="handleDragLeave"
        @drop="handleDrop"
      >
        <div class="upload-content">
          <div class="upload-icon">📄</div>
          <h3 class="upload-zone-title">Drop your GeneWeb file here</h3>
          <p class="upload-zone-subtitle">or click to browse</p>
          <input
            type="file"
            accept=".gw"
            @change="handleFileInput"
            class="file-input"
            id="file-input"
          />
        </div>
        <div class="upload-requirements">
          <p><strong>Supported formats:</strong> .gw files only</p>
          <p><strong>Maximum size:</strong> 10MB</p>
          <label for="file-input" class="file-input-label">
            Choose File
          </label>
        </div>
      </div>

      <!-- File Selected State -->
      <div v-if="selectedFile && !isUploading && !isSuccess" class="file-selected">
        <div class="file-info">
          <div class="file-icon">📄</div>
          <div class="file-details">
            <h4 class="file-name">{{ selectedFile.name }}</h4>
            <p class="file-size">{{ (selectedFile.size / 1024 / 1024).toFixed(2) }} MB</p>
          </div>
        </div>
        <div class="file-actions">
          <button @click="uploadFile" class="upload-button">
            Upload File
          </button>
          <button @click="resetUpload" class="cancel-button">
            Cancel
          </button>
        </div>
      </div>

      <!-- Upload Progress -->
      <div v-if="isUploading" class="upload-progress">
        <div class="progress-header">
          <h3>Uploading...</h3>
          <span class="progress-percentage">{{ Math.round(uploadProgress) }}%</span>
        </div>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${uploadProgress}%` }"
          ></div>
        </div>
        <p class="progress-text">Processing your GeneWeb file...</p>
      </div>

      <!-- Success State -->
      <div v-if="isSuccess && uploadResult" class="upload-success">
        <div class="success-icon">✅</div>
        <h3 class="success-title">Upload Successful!</h3>
        <div class="success-summary">
          <div class="summary-item">
            <span class="summary-label">Persons:</span>
            <span class="summary-value">{{ uploadResult.persons_created }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Families:</span>
            <span class="summary-value">{{ uploadResult.families_created }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Events:</span>
            <span class="summary-value">{{ uploadResult.events_created }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">Children:</span>
            <span class="summary-value">{{ uploadResult.children_created }}</span>
          </div>
        </div>
        <p class="success-message">
          Your file has been processed successfully. Redirecting to family management...
        </p>
      </div>

      <!-- Error State -->
      <div v-if="error" class="upload-error">
        <div class="error-icon">⚠️</div>
        <h3 class="error-title">Upload Failed</h3>
        <p class="error-message">{{ error }}</p>
        <button @click="resetUpload" class="retry-button">
          Try Again
        </button>
      </div>
    </div>

    <!-- Help Section -->
    <div class="upload-help">
      <h3>Need help?</h3>
      <div class="help-content">
        <div class="help-item">
          <strong>What is a GeneWeb file?</strong>
          <p>GeneWeb files (.gw) contain genealogical data in a standardized format used by the GeneWeb genealogy software.</p>
        </div>
        <div class="help-item">
          <strong>How to create a GeneWeb file?</strong>
          <p>You can export data from GeneWeb software or use other genealogy tools that support the GeneWeb format.</p>
        </div>
        <div class="help-item">
          <strong>What happens after upload?</strong>
          <p>Your data will be parsed and stored in the database, where you can view family trees and manage the information.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.file-upload-view {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem 0;
}

.upload-header {
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.back-button {
  position: absolute;
  left: 2rem;
  top: 0;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #2c3e50;
  transition: all 0.2s ease;
}

.back-button:hover {
  background: white;
  transform: translateY(-1px);
}

.upload-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.upload-subtitle {
  font-size: 1.2rem;
  color: #7f8c8d;
  max-width: 600px;
  margin: 0 auto;
}

.upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 2rem;
}

.upload-zone {
  border: 3px dashed #bdc3c7;
  border-radius: 12px;
  padding: 4rem 2rem;
  text-align: center;
  background: white;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
}

.upload-zone:hover,
.upload-zone.drag-over {
  border-color: #3498db;
  background: #f8f9fa;
  transform: translateY(-2px);
}

.upload-content {
  position: relative;
}

.upload-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.upload-zone-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.upload-zone-subtitle {
  color: #7f8c8d;
  margin-bottom: 2rem;
}

.file-input {
  display: none;
}

.file-input-label {
  display: inline-block;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0.75rem 2rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
}

.file-input-label:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.upload-requirements {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #ecf0f1;
  color: #7f8c8d;
  font-size: 0.9rem;
  text-align: center;
}

.upload-requirements .file-input-label {
  margin-top: 1rem;
  display: inline-block;
}

.file-selected {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.file-info {
  display: flex;
  align-items: center;
  margin-bottom: 2rem;
}

.file-icon {
  font-size: 3rem;
  margin-right: 1rem;
}

.file-details {
  flex: 1;
}

.file-name {
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.file-size {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.file-actions {
  display: flex;
  gap: 1rem;
}

.upload-button {
  background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(46, 204, 113, 0.4);
}

.cancel-button {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.cancel-button:hover {
  background: #7f8c8d;
}

.upload-progress {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.progress-percentage {
  font-weight: 600;
  color: #3498db;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  transition: width 0.3s ease;
}

.progress-text {
  color: #7f8c8d;
  text-align: center;
}

.upload-success {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.success-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.success-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 2rem;
}

.success-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.summary-label {
  font-size: 0.9rem;
  color: #7f8c8d;
  margin-bottom: 0.5rem;
}

.summary-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.success-message {
  color: #7f8c8d;
  font-style: italic;
}

.upload-error {
  background: #fdf2f2;
  border: 1px solid #fecaca;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.error-title {
  font-size: 1.3rem;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 1rem;
}

.error-message {
  color: #dc2626;
  margin-bottom: 2rem;
}

.retry-button {
  background: #dc2626;
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.retry-button:hover {
  background: #b91c1c;
}

.upload-help {
  max-width: 800px;
  margin: 4rem auto 0;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.upload-help h3 {
  color: #2c3e50;
  margin-bottom: 2rem;
  text-align: center;
}

.help-content {
  display: grid;
  gap: 2rem;
}

.help-item {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.help-item strong {
  color: #2c3e50;
  display: block;
  margin-bottom: 0.5rem;
}

.help-item p {
  color: #7f8c8d;
  line-height: 1.6;
  margin: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .upload-title {
    font-size: 2rem;
  }

  .upload-zone {
    padding: 3rem 1rem;
  }

  .file-actions {
    flex-direction: column;
  }

  .back-button {
    position: static;
    margin-bottom: 1rem;
  }
}

@media (max-width: 480px) {
  .upload-container {
    padding: 0 1rem;
  }

  .upload-zone {
    padding: 2rem 1rem;
  }

  .success-summary {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
