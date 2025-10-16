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
      <div ref="cyElement" class="cy-container"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import apiService from '../services/api';
import type { FamilyDetailResult, Person, Child } from '../types/family';

// Register Cytoscape extensions
cytoscape.use(dagre);

interface Props {
  familyId: string;
}

interface FamilyNode {
  id: string;
  name: string;
  type: 'person' | 'family';
  person?: Person;
  family?: {
    id: string;
    marriage_date?: string;
    marriage_place?: string;
  };
  gender?: 'M' | 'F';
}

interface FamilyEdge {
  id: string;
  source: string;
  target: string;
  type: 'marriage' | 'parent-child' | 'sibling';
}

const props = defineProps<Props>();

// Reactive state
const isLoading = ref(true);
const error = ref('');
const familyData = ref<FamilyDetailResult | null>(null);
const familyTitle = ref('Family Tree');
const isFullscreen = ref(false);

// Template refs
const treeContainer = ref<HTMLElement>();
const cyElement = ref<HTMLElement>();

// Cytoscape instance
let cy: cytoscape.Core | null = null;

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
    
    await nextTick();
    
    // Wait for DOM to be ready
    setTimeout(() => {
      renderFamilyTree();
    }, 100);
  } catch (err: any) {
    console.error('Error loading family data:', err);
    error.value = err.response?.data?.detail || 'Failed to load family tree. Please try again.';
  } finally {
    isLoading.value = false;
  }
};

const buildFamilyGraph = (): { nodes: FamilyNode[], edges: FamilyEdge[] } => {
  if (!familyData.value) {
    return { nodes: [], edges: [] };
  }
  
  const data = familyData.value;
  const nodes: FamilyNode[] = [];
  const edges: FamilyEdge[] = [];
  const nodeIds = new Set<string>();
  
  // Add family node (marriage connection)
  const familyNodeId = `family-${data.id}`;
  nodes.push({
    id: familyNodeId,
    name: 'Marriage',
    type: 'family',
    family: {
      id: data.id,
      marriage_date: data.marriage_date,
      marriage_place: data.marriage_place
    }
  });
  nodeIds.add(familyNodeId);
  
  // Add husband and wife nodes
  if (data.husband) {
    const husbandId = data.husband.id;
    nodes.push({
      id: husbandId,
      name: `${data.husband.first_name} ${data.husband.last_name}`,
      type: 'person',
      person: data.husband,
      gender: data.husband.sex
    });
    nodeIds.add(husbandId);
    
    // Connect husband to family
    edges.push({
      id: `${husbandId}-${familyNodeId}`,
      source: husbandId,
      target: familyNodeId,
      type: 'marriage'
    });
  }
  
  if (data.wife) {
    const wifeId = data.wife.id;
    nodes.push({
      id: wifeId,
      name: `${data.wife.first_name} ${data.wife.last_name}`,
      type: 'person',
      person: data.wife,
      gender: data.wife.sex
    });
    nodeIds.add(wifeId);
    
    // Connect wife to family
    edges.push({
      id: `${wifeId}-${familyNodeId}`,
      source: wifeId,
      target: familyNodeId,
      type: 'marriage'
    });
  }
  
  // Add children and their relationships
  data.children.forEach(child => {
    if (child.person) {
      const childId = child.person.id;
      
      // Add child node if not already added
      if (!nodeIds.has(childId)) {
        nodes.push({
          id: childId,
          name: `${child.person.first_name} ${child.person.last_name}`,
          type: 'person',
          person: child.person,
          gender: child.person.sex
        });
        nodeIds.add(childId);
      }
      
      // Connect child to family (parent-child relationship)
      edges.push({
        id: `${familyNodeId}-${childId}`,
        source: familyNodeId,
        target: childId,
        type: 'parent-child'
      });
      
      // Handle cross-family relationships (child's own family)
      if (child.person.has_own_family && child.person.own_families) {
        child.person.own_families.forEach(ownFamily => {
          if (ownFamily.spouse) {
            const spouseId = ownFamily.spouse.id;
            
            // Add spouse node if not already added
            if (!nodeIds.has(spouseId)) {
              nodes.push({
                id: spouseId,
                name: ownFamily.spouse.name,
                type: 'person',
                person: {
                  id: ownFamily.spouse.id,
                  first_name: ownFamily.spouse.name.split(' ')[0],
                  last_name: ownFamily.spouse.name.split(' ').slice(1).join(' '),
                  sex: ownFamily.spouse.sex,
                  has_own_family: false
                },
                gender: ownFamily.spouse.sex
              });
              nodeIds.add(spouseId);
            }
            
            // Create child's family node
            const childFamilyId = `family-${ownFamily.id}`;
            if (!nodeIds.has(childFamilyId)) {
              nodes.push({
                id: childFamilyId,
                name: 'Marriage',
                type: 'family',
                family: {
                  id: ownFamily.id,
                  marriage_date: ownFamily.marriage_date,
                  marriage_place: ownFamily.marriage_place
                }
              });
              nodeIds.add(childFamilyId);
            }
            
            // Connect child to their family
            edges.push({
              id: `${childId}-${childFamilyId}`,
              source: childId,
              target: childFamilyId,
              type: 'marriage'
            });
            
            // Connect spouse to child's family
            edges.push({
              id: `${spouseId}-${childFamilyId}`,
              source: spouseId,
              target: childFamilyId,
              type: 'marriage'
            });
          }
        });
      }
    }
  });
  
  return { nodes, edges };
};

const renderFamilyTree = () => {
  if (!cyElement.value || !treeContainer.value) {
    return;
  }
  
  // Destroy existing instance
  if (cy) {
    cy.destroy();
  }
  
  const containerRect = treeContainer.value.getBoundingClientRect();
  const width = containerRect.width;
  const height = Math.max(600, containerRect.height);
  
  // Build graph data
  const { nodes, edges } = buildFamilyGraph();
  
  // Create Cytoscape instance
  try {
    cy = cytoscape({
      container: cyElement.value,
      elements: [
        ...nodes.map(node => ({
          data: {
            id: node.id,
            name: node.name,
            type: node.type,
            gender: node.gender,
            person: node.person,
            family: node.family
          }
        })),
        ...edges.map(edge => ({
          data: {
            id: edge.id,
            source: edge.source,
            target: edge.target,
            type: edge.type
          }
        }))
      ],
    style: [
      {
        selector: 'node',
        style: {
          'background-color': '#4A90E2',
          'label': 'data(name)',
          'text-valign': 'bottom',
          'text-halign': 'center',
          'text-margin-y': 10,
          'font-size': '14px',
          'font-weight': '600',
          'color': '#2c3e50',
          'text-outline-width': 2,
          'text-outline-color': '#fff',
          'width': 60,
          'height': 60,
          'border-width': 3,
          'border-color': '#fff',
          'border-opacity': 1
        }
      },
      {
        selector: 'node[type="person"][gender="M"]',
        style: {
          'background-color': '#4A90E2',
          'shape': 'round-rectangle'
        }
      },
      {
        selector: 'node[type="person"][gender="F"]',
        style: {
          'background-color': '#E24A4A',
          'shape': 'round-rectangle'
        }
      },
      {
        selector: 'node[type="family"]',
        style: {
          'background-color': '#FF9500',
          'shape': 'diamond',
          'width': 40,
          'height': 40,
          'label': '💍'
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 3,
          'line-color': '#BDC3C7',
          'target-arrow-color': '#BDC3C7',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier'
        }
      },
      {
        selector: 'edge[type="marriage"]',
        style: {
          'line-color': '#FF9500',
          'target-arrow-color': '#FF9500',
          'width': 4,
          'line-style': 'solid'
        }
      },
      {
        selector: 'edge[type="parent-child"]',
        style: {
          'line-color': '#7ED321',
          'target-arrow-color': '#7ED321',
          'width': 3,
          'line-style': 'solid'
        }
      },
      {
        selector: 'node:selected',
        style: {
          'border-width': 5,
          'border-color': '#FF6B00'
        }
      },
      {
        selector: 'node:active',
        style: {
          'border-width': 5,
          'border-color': '#FF6B00',
          'width': 70,
          'height': 70
        }
      }
    ],
    layout: {
      name: 'dagre',
      rankDir: 'TB',
      rankSep: 100,
      nodeSep: 50,
      edgeSep: 20,
      ranker: 'tight-tree'
    },
    minZoom: 0.1,
    maxZoom: 3
  });
  
  // Add event listeners
  cy.on('mouseover', 'node', function(event) {
    const node = event.target;
    const data = node.data();
    
    // Create tooltip content
    let tooltipContent = `<div style="font-weight: 600; margin-bottom: 8px;">${data.name}</div>`;
    
    if (data.type === 'person' && data.person) {
      const p = data.person;
      
      if (p.birth_date) {
        const age = new Date().getFullYear() - new Date(p.birth_date).getFullYear();
        tooltipContent += `<div>📅 Born: ${formatDate(p.birth_date)} (Age: ${age})</div>`;
      }
      
      if (p.death_date) {
        tooltipContent += `<div>💀 Died: ${formatDate(p.death_date)}</div>`;
      }
      
      if (p.sex) {
        const genderIcon = p.sex === 'M' ? '👨' : '👩';
        tooltipContent += `<div>${genderIcon} ${p.sex === 'M' ? 'Male' : 'Female'}</div>`;
      }
      
      if (p.notes) {
        tooltipContent += `<div style="margin-top: 8px; font-style: italic; color: #ccc;">${p.notes}</div>`;
      }
    } else if (data.type === 'family' && data.family) {
      const f = data.family;
      tooltipContent += `<div>💍 Marriage</div>`;
      
      if (f.marriage_date) {
        tooltipContent += `<div>📅 ${formatDate(f.marriage_date)}</div>`;
      }
      
      if (f.marriage_place) {
        tooltipContent += `<div>📍 ${f.marriage_place}</div>`;
      }
    }
    
    // Show tooltip
    showTooltip(event.originalEvent, tooltipContent);
  });
  
  cy.on('mouseout', 'node', function() {
    hideTooltip();
  });
  
  cy.on('mousemove', 'node', function(event) {
    updateTooltipPosition(event.originalEvent);
  });
  
  // Fit the graph to the container
  cy.fit(undefined, 50);
  } catch (error) {
    console.error('Error creating Cytoscape instance:', error);
  }
};

// Tooltip management
let tooltip: HTMLElement | null = null;

const showTooltip = (event: MouseEvent, content: string) => {
  if (!tooltip) {
    tooltip = document.createElement('div');
    tooltip.className = 'family-tree-tooltip';
    tooltip.style.cssText = `
      position: absolute;
      background: rgba(0, 0, 0, 0.9);
      color: white;
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 14px;
      font-family: system-ui, -apple-system, sans-serif;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      pointer-events: none;
      opacity: 0;
      z-index: 1000;
      max-width: 250px;
      line-height: 1.4;
      transition: opacity 0.2s ease;
    `;
    document.body.appendChild(tooltip);
  }
  
  tooltip.innerHTML = content;
  tooltip.style.opacity = '1';
  updateTooltipPosition(event);
};

const updateTooltipPosition = (event: MouseEvent) => {
  if (tooltip) {
    tooltip.style.left = (event.pageX + 10) + 'px';
    tooltip.style.top = (event.pageY - 10) + 'px';
  }
};

const hideTooltip = () => {
  if (tooltip) {
    tooltip.style.opacity = '0';
  }
};

const resetZoom = () => {
  if (cy) {
    cy.fit(undefined, 50);
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

const handleResize = () => {
  if (familyData.value && cy) {
    cy.resize();
    cy.fit(undefined, 50);
  }
};

// Lifecycle
onMounted(() => {
  loadFamilyData();
  window.addEventListener('resize', handleResize);
});

onUnmounted(() => {
  window.removeEventListener('resize', handleResize);
  if (cy) {
    cy.destroy();
  }
  if (tooltip) {
    document.body.removeChild(tooltip);
  }
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
  overflow: hidden;
  position: relative;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.cy-container {
  width: 100%;
  height: 100%;
  background: transparent;
}

/* Cytoscape styles */
:deep(.cy-container) {
  font-family: system-ui, -apple-system, sans-serif;
}

:deep(.cy-container canvas) {
  outline: none;
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
}
</style>
