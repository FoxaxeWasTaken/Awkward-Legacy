<template>
  <div class="family-tree">
    <div class="tree-header">
      <div class="header-left">
        <button @click="$router.push('/')" class="back-button">
          <span class="back-icon">←</span>
          Back to Search
        </button>
        <h2>{{ familyTitle }}</h2>
      </div>
      <div class="tree-controls">
        <button @click="resetZoom" class="control-button">Reset View</button>
        <button @click="toggleFullscreen" class="control-button">
          {{ isFullscreen ? 'Exit Fullscreen' : 'Fullscreen' }}
        </button>
      </div>
    </div>
    
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading family tree...</p>
    </div>
    
    <div v-else-if="error" class="error-state">
      <div class="error-icon">⚠️</div>
      <h3>Error Loading Family Tree</h3>
      <p>{{ error }}</p>
      <button @click="loadFamilyData" class="retry-button">Retry</button>
    </div>
    
    <div v-else class="tree-container" ref="treeContainer">
      <div class="tree-content" ref="treeContent">
        <div class="family-generation" v-for="(generation, index) in familyGenerations" :key="index">
          <div class="generation-label" v-if="index > 0">Generation {{ index + 1 }}</div>
          <div class="couples-row">
            <div 
              v-for="couple in generation.couples" 
              :key="couple.id" 
              class="couple-container"
              :class="{ 'has-children': couple.children.length > 0 }"
            >
              <!-- Spouses Row - Husband and Wife side by side -->
              <div class="spouses-row">
                <!-- Husband -->
                <div 
                  v-if="couple.husband" 
                  class="person-node husband"
                  :class="{ 'has-spouse': couple.wife }"
                  @click="selectPerson(couple.husband)"
                  @mouseover="showTooltip($event, couple.husband)"
                  @mouseout="hideTooltip"
                >
                  <div class="person-avatar">
                    <div class="avatar-circle">
                      <span class="gender-icon">👨</span>
                    </div>
                  </div>
                  <div class="person-info">
                    <div class="person-name">{{ couple.husband.first_name }} {{ couple.husband.last_name }}</div>
                    <div class="person-dates" v-if="couple.husband.birth_date">
                      {{ formatDate(couple.husband.birth_date) }} - {{ couple.husband.death_date ? formatDate(couple.husband.death_date) : 'Present' }}
                    </div>
                  </div>
                </div>
                
                <!-- Marriage Line -->
                <div class="marriage-line" v-if="couple.husband && couple.wife"></div>
                
                <!-- Wife -->
                <div 
                  v-if="couple.wife" 
                  class="person-node wife"
                  :class="{ 'has-spouse': couple.husband }"
                  @click="selectPerson(couple.wife)"
                  @mouseover="showTooltip($event, couple.wife)"
                  @mouseout="hideTooltip"
                >
                  <div class="person-avatar">
                    <div class="avatar-circle">
                      <span class="gender-icon">👩</span>
                    </div>
                  </div>
                  <div class="person-info">
                    <div class="person-name">{{ couple.wife.first_name }} {{ couple.wife.last_name }}</div>
                    <div class="person-dates" v-if="couple.wife.birth_date">
                      {{ formatDate(couple.wife.birth_date) }} - {{ couple.wife.death_date ? formatDate(couple.wife.death_date) : 'Present' }}
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Children Connection -->
              <div v-if="couple.children.length > 0" class="children-connection">
                <div class="connection-line"></div>
                <div class="children-container">
                  <div 
                    v-for="child in couple.children" 
                    :key="child.id"
                    class="child-node"
                    @click="selectPerson(child)"
                    @mouseover="showTooltip($event, child)"
                    @mouseout="hideTooltip"
                  >
                    <div class="child-avatar">
                      <div class="avatar-circle">
                        <span class="gender-icon">{{ child.sex === 'M' ? '👦' : '👧' }}</span>
                      </div>
                    </div>
                    <div class="child-info">
                      <div class="child-name">{{ child.first_name }} {{ child.last_name }}</div>
                      <div class="child-dates" v-if="child.birth_date">
                        {{ formatDate(child.birth_date) }} - {{ child.death_date ? formatDate(child.death_date) : 'Present' }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Tooltip -->
    <div 
      v-if="tooltip.visible" 
      class="person-tooltip"
      :style="{ left: tooltip.x + 'px', top: tooltip.y + 'px' }"
    >
      <div class="tooltip-content">
        <div class="tooltip-name">{{ tooltip.person?.first_name }} {{ tooltip.person?.last_name }}</div>
        <div class="tooltip-details">
          <div v-if="tooltip.person?.birth_date">
            <strong>Born:</strong> {{ formatDate(tooltip.person.birth_date) }}
          </div>
          <div v-if="tooltip.person?.death_date">
            <strong>Died:</strong> {{ formatDate(tooltip.person.death_date) }}
          </div>
          <div v-if="tooltip.person?.sex">
            <strong>Gender:</strong> {{ tooltip.person.sex === 'M' ? 'Male' : 'Female' }}
          </div>
          <div v-if="tooltip.person?.notes">
            <strong>Notes:</strong> {{ tooltip.person.notes }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue';
import apiService from '../services/api';
import type { FamilyDetailResult, Person, Child } from '../types/family';

interface Props {
  familyId: string;
}

interface Couple {
  id: string;
  husband?: Person;
  wife?: Person;
  children: Person[];
  marriageDate?: string;
  marriagePlace?: string;
}

interface FamilyGeneration {
  couples: Couple[];
}

const props = defineProps<Props>();

// Reactive state
const isLoading = ref(true);
const error = ref('');
const familyData = ref<FamilyDetailResult | null>(null);
const familyTitle = ref('Family Tree');
const selectedPerson = ref<Person | null>(null);
const crossFamilyChildren = ref<Map<string, Person[]>>(new Map());

// Template refs
const treeContainer = ref<HTMLElement>();
const treeContent = ref<HTMLElement>();

// Tooltip state
const tooltip = ref({
  visible: false,
  x: 0,
  y: 0,
  person: null as Person | null
});

let isFullscreen = ref(false);

// Computed property for family generations
const familyGenerations = computed((): FamilyGeneration[] => {
  if (!familyData.value) return [];
  
  const data = familyData.value;
  const generations: FamilyGeneration[] = [];
  
  // Create the main couple (current family)
  const mainCouple: Couple = {
    id: data.id,
    husband: data.husband || undefined,
    wife: data.wife || undefined,
    children: data.children.map(child => child.person).filter(Boolean) as Person[],
    marriageDate: data.marriage_date,
    marriagePlace: data.marriage_place
  };
  
  // Add main couple to first generation
  generations.push({
    couples: [mainCouple]
  });
  
  // Process children who have their own families
  const childCouples: Couple[] = [];
  
  data.children.forEach(child => {
    if (child.person?.has_own_family && child.person.own_families) {
      child.person.own_families.forEach(ownFamily => {
        if (ownFamily.spouse) {
          const childCouple: Couple = {
            id: ownFamily.id,
            husband: child.person?.sex === 'M' ? child.person : undefined,
            wife: child.person?.sex === 'F' ? child.person : undefined,
            children: crossFamilyChildren.value.get(ownFamily.id) || [],
            marriageDate: ownFamily.marriage_date,
            marriagePlace: ownFamily.marriage_place
          };
          
          // Add spouse
          if (child.person?.sex === 'M') {
            childCouple.wife = {
              id: ownFamily.spouse.id,
              first_name: ownFamily.spouse.name.split(' ')[0],
              last_name: ownFamily.spouse.name.split(' ').slice(1).join(' '),
              sex: ownFamily.spouse.sex,
              has_own_family: false
            };
          } else {
            childCouple.husband = {
              id: ownFamily.spouse.id,
              first_name: ownFamily.spouse.name.split(' ')[0],
              last_name: ownFamily.spouse.name.split(' ').slice(1).join(' '),
              sex: ownFamily.spouse.sex,
              has_own_family: false
            };
          }
          
          childCouples.push(childCouple);
        }
      });
    }
  });
  
  // Add child couples as second generation
  if (childCouples.length > 0) {
    generations.push({
      couples: childCouples
    });
  }
  
  return generations;
});

// Methods
const loadFamilyData = async () => {
  isLoading.value = true;
  error.value = '';
  
  try {
    const data = await apiService.getFamilyDetail(props.familyId);
    familyData.value = data;
    
    // Create family title
    const parts = [];
    if (data.husband) {
      parts.push(`${data.husband.first_name} ${data.husband.last_name}`);
    }
    if (data.wife) {
      parts.push(`${data.wife.first_name} ${data.wife.last_name}`);
    }
    familyTitle.value = parts.length > 0 ? parts.join(' & ') : 'Family Tree';
    
    // Fetch children data for cross-family relationships
    await loadCrossFamilyChildren(data);
    
  } catch (err: any) {
    console.error('Error loading family data:', err);
    error.value = err.response?.data?.detail || 'Failed to load family tree. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

const loadCrossFamilyChildren = async (data: FamilyDetailResult) => {
  const childrenMap = new Map<string, Person[]>();
  
  for (const child of data.children) {
    if (child.person?.has_own_family && child.person.own_families) {
      for (const ownFamily of child.person.own_families) {
        try {
          const familyDetail = await apiService.getFamilyDetail(ownFamily.id);
          const children = familyDetail.children.map(c => c.person).filter(Boolean) as Person[];
          childrenMap.set(ownFamily.id, children);
        } catch (err) {
          console.error(`Error loading children for family ${ownFamily.id}:`, err);
        }
      }
    }
  }
  
  crossFamilyChildren.value = childrenMap;
};

const selectPerson = (person: Person) => {
  selectedPerson.value = person;
  // You can add navigation to person detail page here
  console.log('Selected person:', person);
};

const showTooltip = (event: MouseEvent, person: Person) => {
  tooltip.value = {
    visible: true,
    x: event.pageX + 10,
    y: event.pageY - 10,
    person: person
  };
};

const hideTooltip = () => {
  tooltip.value.visible = false;
};

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  } catch (error) {
    return dateString;
  }
};

const resetZoom = () => {
  // Scroll to top of tree content
  if (treeContent.value) {
    treeContent.value.scrollTo({ top: 0, left: 0, behavior: 'smooth' });
  }
};

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    treeContainer.value?.requestFullscreen();
    isFullscreen.value = true;
  } else {
    document.exitFullscreen();
    isFullscreen.value = false;
  }
};

// Lifecycle
onMounted(() => {
  loadFamilyData();
});

onUnmounted(() => {
  // Clean up any event listeners if needed
});

// Watch for family ID changes
watch(() => props.familyId, () => {
  loadFamilyData();
});
</script>

<style scoped>
.family-tree {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-bottom: none;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  position: relative;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: rgba(255, 255, 255, 0.15);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  text-decoration: none;
}

.back-button:hover {
  background: rgba(255, 255, 255, 0.25);
  border-color: rgba(255, 255, 255, 0.4);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.back-icon {
  font-size: 1.1rem;
  font-weight: bold;
}

.tree-header h2 {
  color: white;
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  text-shadow: 0 1px 3px rgba(0,0,0,0.3);
}

.tree-controls {
  display: flex;
  gap: 0.75rem;
}

.control-button {
  padding: 0.75rem 1.5rem;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.control-button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.loading-state,
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state {
  color: #dc2626;
}

.error-icon {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.retry-button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.tree-container {
  flex: 1;
  overflow: auto;
  position: relative;
  padding: 2rem;
}

.tree-content {
  max-width: 1200px;
  margin: 0 auto;
}

.family-generation {
  margin-bottom: 4rem;
}

.generation-label {
  text-align: center;
  font-size: 1.2rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 2rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 20px;
  display: inline-block;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.couples-row {
  display: flex;
  flex-wrap: wrap;
  gap: 3rem;
  justify-content: center;
  align-items: flex-start;
}

.couple-container {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 500px;
}

.spouses-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
}

.marriage-line {
  width: 60px;
  height: 3px;
  background: linear-gradient(90deg, #e74c3c, #f39c12);
  border-radius: 2px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  flex-shrink: 0;
}

.person-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1.5rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  z-index: 2;
  min-width: 180px;
  margin-bottom: 1rem;
}

.person-node:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 30px rgba(0,0,0,0.15);
}

.person-node.husband {
  border-left: 4px solid #3498db;
}

.person-node.wife {
  border-left: 4px solid #e74c3c;
}

.person-avatar {
  margin-bottom: 1rem;
}

.avatar-circle {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.person-node.husband .avatar-circle {
  background: linear-gradient(135deg, #3498db, #2980b9);
}

.person-node.wife .avatar-circle {
  background: linear-gradient(135deg, #e74c3c, #c0392b);
}

.person-info {
  text-align: center;
}

.person-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.person-dates {
  font-size: 0.9rem;
  color: #7f8c8d;
  font-style: italic;
}

.children-connection {
  position: relative;
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.connection-line {
  width: 3px;
  height: 40px;
  background: linear-gradient(180deg, #95a5a6, #bdc3c7);
  border-radius: 2px;
  margin-bottom: 1rem;
}

.children-container {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  justify-content: center;
  align-items: flex-start;
}

.child-node {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 1rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 3px 15px rgba(0,0,0,0.08);
  transition: all 0.3s ease;
  cursor: pointer;
  min-width: 150px;
  border-left: 3px solid #27ae60;
}

.child-node:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0,0,0,0.12);
}

.child-avatar {
  margin-bottom: 0.75rem;
}

.child-avatar .avatar-circle {
  width: 45px;
  height: 45px;
  font-size: 1.5rem;
  background: linear-gradient(135deg, #27ae60, #2ecc71);
}

.child-info {
  text-align: center;
}

.child-name {
  font-size: 1rem;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.25rem;
}

.child-dates {
  font-size: 0.8rem;
  color: #7f8c8d;
  font-style: italic;
}

.person-tooltip {
  position: fixed;
  background: rgba(0, 0, 0, 0.9);
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-family: system-ui, -apple-system, sans-serif;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  pointer-events: none;
  z-index: 1000;
  max-width: 250px;
  line-height: 1.4;
}

.tooltip-content {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.tooltip-name {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.tooltip-details {
  font-size: 0.9rem;
}

.tooltip-details div {
  margin-bottom: 0.25rem;
}

/* Fullscreen styles */
:fullscreen .tree-container {
  height: 100vh;
}

/* Responsive */
@media (max-width: 768px) {
  .tree-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .tree-controls {
    justify-content: center;
  }
  
  .couples-row {
    flex-direction: column;
    align-items: center;
  }
  
  .couple-container {
    min-width: 320px;
  }
  
  .spouses-row {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .marriage-line {
    width: 3px;
    height: 30px;
    background: linear-gradient(180deg, #e74c3c, #f39c12);
  }
  
  .children-container {
    flex-direction: column;
    align-items: center;
  }
}
</style>
