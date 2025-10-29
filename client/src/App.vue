<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import apiService from './services/api'

const _router = useRouter()
const isDownloading = ref(false)

onMounted(() => {
  console.log('Geneweb Family Search App initialized')
})

const downloadAllData = async () => {
  try {
    isDownloading.value = true
    const blob = await apiService.downloadAllData()
    
    // Create download link
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `geneweb-export-${new Date().toISOString().split('T')[0]}.gw`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
  } catch (error) {
    console.error('Error downloading data:', error)
    alert('Failed to download data. Please try again.')
  } finally {
    isDownloading.value = false
  }
}
</script>

<template>
  <div id="app">
        <header class="app-header">
          <div class="header-content">
            <h1 class="app-title">🏛️ Geneweb</h1>
            <p class="app-subtitle">Explore family trees and genealogical data</p>
          </div>
        </header>

    <main class="app-main">
      <div class="main-content">
        <RouterView />
        
        <!-- Global Download Button - only show on home page -->
        <div v-if="$route && $route.path === '/'" class="global-download-section">
          <button 
            @click="downloadAllData" 
            :disabled="isDownloading"
            class="download-all-btn"
            title="Download all data as .gw file"
          >
            <span v-if="isDownloading">⏳</span>
            <span v-else>📥</span>
            {{ isDownloading ? 'Downloading...' : 'Download All Data' }}
          </button>
        </div>
      </div>
    </main>

    <footer class="app-footer">
      <p>&copy; 2024 Geneweb Family Search. Built with Vue.js and FastAPI.</p>
    </footer>
  </div>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family:
    -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: #333;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem 0;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  text-align: center;
}

.app-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.app-subtitle {
  font-size: 1.2rem;
  opacity: 0.9;
  font-weight: 300;
}

.download-all-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  padding: 1rem 1.5rem;
  border-radius: 50px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  backdrop-filter: blur(10px);
}

.download-all-btn:hover:not(:disabled) {
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

.download-all-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: visible;
}

.main-content {
  position: relative;
}

.global-download-section {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 1000;
}

.app-footer {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  text-align: center;
  padding: 1rem;
  font-size: 0.9rem;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  position: relative;
  z-index: 10;
}

/* Responsive */
@media (max-width: 768px) {
  .app-title {
    font-size: 2rem;
  }

  .app-subtitle {
    font-size: 1rem;
  }

  .header-content {
    padding: 0 1rem;
  }

  .global-download-section {
    bottom: 1rem;
    right: 1rem;
  }

  .download-all-btn {
    padding: 0.8rem 1.2rem;
    font-size: 0.9rem;
  }
}
</style>
