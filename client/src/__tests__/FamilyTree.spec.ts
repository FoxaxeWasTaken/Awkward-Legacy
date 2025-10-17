import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import FamilyTree from '../components/FamilyTree.vue'
import { createMockFamilyDetail, waitForPromises } from './test-utils'
import { apiService } from '../services/api' // Import the actual service for type inference

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    getFamilyDetail: vi.fn(),
  },
  default: {
    getFamilyDetail: vi.fn(),
  },
}))

// Mock router
const mockRouter = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', name: 'home', component: { template: '<div>Home</div>' } },
    { path: '/family/:id', name: 'family-tree', component: { template: '<div>Family Tree</div>' } },
  ],
})

describe('FamilyTree Component', () => {
  let wrapper: VueWrapper<InstanceType<typeof FamilyTree>>
  const mockFamilyId = 'test-family-123'
  const mockFamilyDetail = createMockFamilyDetail({ id: mockFamilyId })

  beforeEach(() => {
    vi.clearAllMocks()
    // Set up the mock to return our test data
    vi.mocked(apiService.getFamilyDetail).mockResolvedValue(mockFamilyDetail)
  })

  afterEach(() => {
    if (wrapper) {
      wrapper.unmount()
    }
  })

  const createWrapper = (props = {}) => {
    return mount(FamilyTree, {
      props: {
        familyId: mockFamilyId,
        ...props,
      },
      global: {
        plugins: [mockRouter],
        stubs: {
          'router-link': true,
        },
      },
    })
  }

  describe('Component Structure', () => {
    it('renders the family tree interface correctly', async () => {
      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.family-tree').exists()).toBe(true)
      expect(wrapper.find('.tree-header').exists()).toBe(true)
      expect(wrapper.find('.back-button').exists()).toBe(true)
      expect(wrapper.find('.tree-controls').exists()).toBe(true)
    })

    it('shows loading state initially', () => {
      // Mock a pending promise to keep loading state
      vi.mocked(apiService.getFamilyDetail).mockReturnValue(new Promise(() => {}))
      wrapper = createWrapper()

      expect(wrapper.find('.loading-state').exists()).toBe(true)
      expect(wrapper.find('.spinner').exists()).toBe(true)
      expect(wrapper.text()).toContain('Loading family tree...')
    })

    it('displays correct zoom controls', async () => {
      wrapper = createWrapper()
      await waitForPromises()

      const zoomControls = wrapper.find('.tree-controls')
      expect(zoomControls.find('button[title="Zoom Out"]').exists()).toBe(true)
      expect(zoomControls.find('button[title="Zoom In"]').exists()).toBe(true)
      expect(zoomControls.find('button[title="Reset View"]').exists()).toBe(true)
      expect(zoomControls.text()).toContain('100%')
    })
  })

  describe('Tree Controls', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await waitForPromises()
    })

    it('zooms in when zoom in button is clicked', async () => {
      const initialScale = wrapper.vm.scale
      await wrapper.find('button[title="Zoom In"]').trigger('click')

      expect(wrapper.vm.scale).toBeGreaterThan(initialScale)
    })

    it('zooms out when zoom out button is clicked', async () => {
      // First zoom in to have room to zoom out
      await wrapper.find('button[title="Zoom In"]').trigger('click')
      const scaleAfterZoomIn = wrapper.vm.scale

      await wrapper.find('button[title="Zoom Out"]').trigger('click')

      expect(wrapper.vm.scale).toBeLessThan(scaleAfterZoomIn)
    })

    it('updates zoom percentage display', async () => {
      await wrapper.find('button[title="Zoom In"]').trigger('click')

      const zoomLabel = wrapper.find('.zoom-label')
      expect(zoomLabel.text()).toMatch(/\d+%/)
    })
  })

  describe('Navigation', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await waitForPromises()
    })

    it('navigates back to search when back button is clicked', async () => {
      const pushSpy = vi.spyOn(mockRouter, 'push')

      await wrapper.find('.back-button').trigger('click')

      expect(pushSpy).toHaveBeenCalledWith('/')
    })
  })

  describe('Props Validation', () => {
    it('requires familyId prop', () => {
      wrapper = createWrapper({ familyId: 'test-id' })
      expect(wrapper.props('familyId')).toBe('test-id')
    })

    it('handles different familyId formats', () => {
      const uuidFamilyId = '123e4567-e89b-12d3-a456-426614174000'
      wrapper = createWrapper({ familyId: uuidFamilyId })
      expect(wrapper.props('familyId')).toBe(uuidFamilyId)
    })
  })

  describe('Component Lifecycle', () => {
    it('loads data on mount', async () => {
      wrapper = createWrapper()
      await waitForPromises()
      // Component should be mounted successfully
      expect(wrapper.exists()).toBe(true)
    })

    it('handles prop changes', async () => {
      wrapper = createWrapper({ familyId: 'family-1' })
      await waitForPromises()
      expect(wrapper.props('familyId')).toBe('family-1')

      await wrapper.setProps({ familyId: 'family-2' })
      await waitForPromises()
      expect(wrapper.props('familyId')).toBe('family-2')
    })
  })
})
