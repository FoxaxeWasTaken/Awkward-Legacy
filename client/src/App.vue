<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

const _router = useRouter()

onMounted(() => {
  console.log('Geneweb Family Search App initialized')
})
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
      <RouterView />
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

.app-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: visible;
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
}
</style>
