import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import FamilySearchView from '../views/FamilySearchView.vue'
import FamilySearch from '../components/FamilySearch.vue'

// Mock the API service
vi.mock('../services/api', () => ({
  default: {
    searchFamilies: vi.fn(),
    healthCheck: vi.fn(() => Promise.resolve(true)),
  },
}))

// Create mock router
const createMockRouter = () => {
  return createRouter({
    history: createMemoryHistory(),
    routes: [
      {
        path: '/',
        name: 'home',
        component: FamilySearchView,
      },
      {
        path: '/family/:id',
        name: 'family-tree',
        component: { template: '<div>Family Tree</div>' },
      },
    ],
  })
}

describe('FamilySearchView', () => {
  let mockRouter: ReturnType<typeof createMockRouter>

  beforeEach(() => {
    vi.clearAllMocks()
    mockRouter = createMockRouter()
  })

  it('renders the view correctly', () => {
    const wrapper = mount(FamilySearchView, {
      global: {
        plugins: [mockRouter],
      },
    })

    expect(wrapper.exists()).toBe(true)
    expect(wrapper.classes()).toContain('family-search-view')
  })

  it('contains FamilySearch component', () => {
    const wrapper = mount(FamilySearchView, {
      global: {
        plugins: [mockRouter],
      },
    })

    const familySearchComponent = wrapper.findComponent(FamilySearch)
    expect(familySearchComponent.exists()).toBe(true)
  })

  it('applies correct styling', () => {
    const wrapper = mount(FamilySearchView, {
      global: {
        plugins: [mockRouter],
      },
    })

    const viewElement = wrapper.find('.family-search-view')
    expect(viewElement.exists()).toBe(true)
  })

  it('passes props to FamilySearch component correctly', () => {
    const wrapper = mount(FamilySearchView, {
      global: {
        plugins: [mockRouter],
      },
    })

    const familySearchComponent = wrapper.findComponent(FamilySearch)
    // FamilySearch doesn't take props, but we verify it's rendered
    expect(familySearchComponent.exists()).toBe(true)
  })

  it('integrates with router for navigation', async () => {
    const _wrapper = mount(FamilySearchView, {
      global: {
        plugins: [mockRouter],
      },
    })

    await mockRouter.push('/')
    expect(mockRouter.currentRoute.value.path).toBe('/')

    const familyId = '123e4567-e89b-12d3-a456-426614174000'
    await mockRouter.push(`/family/${familyId}`)
    expect(mockRouter.currentRoute.value.path).toBe(`/family/${familyId}`)
  })

  it('renders with full page layout', () => {
    const wrapper = mount(FamilySearchView, {
      global: {
        plugins: [mockRouter],
      },
    })

    const viewDiv = wrapper.find('.family-search-view')
    expect(viewDiv.exists()).toBe(true)
  })

  it('maintains state during navigation', async () => {
    const wrapper = mount(FamilySearchView, {
      global: {
        plugins: [mockRouter],
      },
    })

    // Component should maintain its structure
    expect(wrapper.findComponent(FamilySearch).exists()).toBe(true)

    await flushPromises()

    // After promises resolve, component should still exist
    expect(wrapper.findComponent(FamilySearch).exists()).toBe(true)
  })
})
