<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const navigateToSearch = () => {
  router.push('/manage')
}

const navigateToUpload = () => {
  router.push('/upload')
}

const navigateToManage = () => {
  router.push('/manage')
}
</script>

<template>
  <div class="welcome-view">

    <div class="welcome-actions">
      <div class="action-cards">
        <div class="action-card search-card" @click="navigateToSearch">
          <div class="card-icon">🔍</div>
          <h3 class="card-title">Search Families</h3>
          <p class="card-description">
            Search and explore existing family trees in the database
          </p>
          <div class="card-features">
            <span class="feature">• Browse family trees</span>
            <span class="feature">• View family details</span>
            <span class="feature">• Interactive visualization</span>
          </div>
          <button class="card-button">Start Searching</button>
        </div>

        <div class="action-card upload-card" @click="navigateToUpload">
          <div class="card-icon">📁</div>
          <h3 class="card-title">Upload Family File</h3>
          <p class="card-description">
            Upload and import your GeneWeb (.gw) files to the database
          </p>
          <div class="card-features">
            <span class="feature">• Drag & drop upload</span>
            <span class="feature">• Automatic parsing</span>
            <span class="feature">• Instant preview</span>
          </div>
          <button class="card-button">Upload File</button>
        </div>

        <div class="action-card manage-card" @click="navigateToManage">
          <div class="card-icon">📊</div>
          <h3 class="card-title">Manage Families</h3>
          <p class="card-description">
            View, filter, and manage all families in the database
          </p>
          <div class="card-features">
            <span class="feature">• Advanced filtering</span>
            <span class="feature">• Bulk operations</span>
            <span class="feature">• Data export</span>
          </div>
          <button class="card-button">Manage Data</button>
        </div>
      </div>
    </div>

    <div class="welcome-features">
      <h2 class="features-title">What you can do</h2>
      <div class="features-grid">
        <div class="feature-item">
          <div class="feature-icon">🌳</div>
          <h4>Family Trees</h4>
          <p>Visualize complex family relationships with interactive tree diagrams</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📋</div>
          <h4>Data Management</h4>
          <p>Organize and manage genealogical data with powerful filtering tools</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">💾</div>
          <h4>Import/Export</h4>
          <p>Upload GeneWeb files and export data in standard formats</p>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🔍</div>
          <h4>Search & Discovery</h4>
          <p>Find families and individuals with advanced search capabilities</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.welcome-view {
  min-height: calc(100vh - 200px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem 0;
}

.welcome-actions {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-bottom: 4rem;
}

.action-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 2px solid transparent;
}

.action-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.search-card:hover {
  border-color: #3498db;
}

.upload-card:hover {
  border-color: #e74c3c;
}

.manage-card:hover {
  border-color: #2ecc71;
}

.card-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.card-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.card-description {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.card-features {
  margin-bottom: 2rem;
}

.feature {
  display: block;
  color: #7f8c8d;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
}

.card-button {
  width: 100%;
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.card-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.welcome-features {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  text-align: center;
}

.features-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 3rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.feature-item {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease;
}

.feature-item:hover {
  transform: translateY(-3px);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-item h4 {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 1rem;
}

.feature-item p {
  color: #7f8c8d;
  line-height: 1.6;
}

/* Responsive Design */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2.5rem;
  }

  .hero-subtitle {
    font-size: 1.2rem;
  }

  .action-cards {
    grid-template-columns: 1fr;
  }

  .welcome-hero {
    padding: 2rem 1rem;
  }

  .welcome-actions,
  .welcome-features {
    padding: 0 1rem;
  }
}

@media (max-width: 480px) {
  .hero-title {
    font-size: 2rem;
  }

  .action-card {
    padding: 1.5rem;
  }
}
</style>
