import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import FamilySearch from '../components/FamilySearch.vue'
import apiService from '../services/api'

// Mock the API service
vi.mock('../services/api', () => ({
  default: {
    searchFamilies: vi.fn(),
    healthCheck: vi.fn(),
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

describe('FamilySearch Component', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.mocked(apiService.healthCheck).mockResolvedValue(true)
  })

  it('renders the search interface correctly', () => {
    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    expect(wrapper.find('h2').text()).toBe('Family Search')
    expect(wrapper.find('input[type="text"]').exists()).toBe(true)
    expect(wrapper.find('button').text()).toContain('Search')
    expect(wrapper.find('select').exists()).toBe(true) // Results limit selector
  })

  it('displays welcome state initially', () => {
    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    expect(wrapper.text()).toContain('Welcome to Family Search')
    expect(wrapper.text()).toContain('Enter a family name above to search')
    expect(wrapper.text()).toContain('Search Examples:')
  })

  it('disables search button when input is empty', async () => {
    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    const searchButton = wrapper.find('button')
    expect(searchButton.attributes('disabled')).toBeDefined()
  })

  it('enables search button when input has text', async () => {
    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    const input = wrapper.find('input[type="text"]')
    await input.setValue('Smith')
    await wrapper.vm.$nextTick()

    const searchButton = wrapper.find('button')
    expect(searchButton.attributes('disabled')).toBeUndefined()
  })

  it('performs search and displays results', async () => {
    const mockResults = [
      {
        id: '123e4567-e89b-12d3-a456-426614174000',
        husband_name: 'John Smith',
        wife_name: 'Jane Doe',
        marriage_date: '2005-06-20',
        marriage_place: 'Boston, MA',
        children_count: 2,
        summary: 'John Smith & Jane Doe (2005)',
      },
      {
        id: '223e4567-e89b-12d3-a456-426614174001',
        husband_name: 'Robert Smith',
        wife_name: 'Linda Wilson',
        marriage_date: '1970-09-15',
        marriage_place: 'New York, NY',
        children_count: 3,
        summary: 'Robert Smith & Linda Wilson (1970)',
      },
    ]

    vi.mocked(apiService.searchFamilies).mockResolvedValue(mockResults)

    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    // Enter search query
    const input = wrapper.find('input[type="text"]')
    await input.setValue('Smith')

    // Click search button
    const searchButton = wrapper.find('button')
    await searchButton.trigger('click')
    await flushPromises()

    // Check that search was called
    expect(apiService.searchFamilies).toHaveBeenCalledWith({
      q: 'Smith',
      limit: 20,
    })

    // Check results are displayed
    expect(wrapper.text()).toContain('Search Results (2)')
    expect(wrapper.text()).toContain('John Smith & Jane Doe (2005)')
    expect(wrapper.text()).toContain('Robert Smith & Linda Wilson (1970)')
  })

  it('displays no results message when search returns empty', async () => {
    vi.mocked(apiService.searchFamilies).mockResolvedValue([])

    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    const input = wrapper.find('input[type="text"]')
    await input.setValue('NonExistentFamily')

    const searchButton = wrapper.find('button')
    await searchButton.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('No Families Found')
    expect(wrapper.text()).toContain('No families match your search criteria')
  })

  it('displays error message on search failure', async () => {
    const errorMessage = 'Network error occurred'
    vi.mocked(apiService.searchFamilies).mockRejectedValue({
      response: { data: { detail: errorMessage } },
    })

    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    const input = wrapper.find('input[type="text"]')
    await input.setValue('Smith')

    const searchButton = wrapper.find('button')
    await searchButton.trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Search Error')
    expect(wrapper.text()).toContain(errorMessage)
  })

  it('shows loading state during search', async () => {
    vi.mocked(apiService.searchFamilies).mockImplementation(
      () => new Promise((resolve) => setTimeout(() => resolve([]), 100)),
    )

    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    const input = wrapper.find('input[type="text"]')
    await input.setValue('Smith')

    const searchButton = wrapper.find('button')
    await searchButton.trigger('click')

    // Should show loading state
    expect(wrapper.text()).toContain('Searching families...')

    await flushPromises()
  })

  it('updates results limit', async () => {
    const mockResults = [
      {
        id: '123',
        husband_name: 'John Smith',
        wife_name: 'Jane Doe',
        marriage_date: '2005-06-20',
        marriage_place: 'Boston, MA',
        children_count: 2,
        summary: 'John Smith & Jane Doe (2005)',
      },
    ]

    vi.mocked(apiService.searchFamilies).mockResolvedValue(mockResults)

    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    // Change limit to 50
    const select = wrapper.find('select')
    await select.setValue('50')

    // Perform search
    const input = wrapper.find('input[type="text"]')
    await input.setValue('Smith')
    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(apiService.searchFamilies).toHaveBeenCalledWith({
      q: 'Smith',
      limit: '50',
    })
  })

  it('clears results when typing a new search after previous results', async () => {
    const mockResults = [
      {
        id: '123',
        husband_name: 'John Smith',
        wife_name: 'Jane Doe',
        marriage_date: '2005-06-20',
        marriage_place: 'Boston, MA',
        children_count: 2,
        summary: 'John Smith & Jane Doe (2005)',
      },
    ]

    vi.mocked(apiService.searchFamilies).mockResolvedValue(mockResults)

    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    // First search
    const input = wrapper.find('input[type="text"]')
    await input.setValue('Smith')
    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('John Smith & Jane Doe')

    // Start typing new search
    await input.setValue('Johnson')
    await wrapper.vm.$nextTick()

    // Results should be cleared (welcome state should show again)
    expect(wrapper.text()).not.toContain('John Smith & Jane Doe')
  })

  it('allows retry after error', async () => {
    vi.mocked(apiService.searchFamilies).mockRejectedValueOnce({
      response: { data: { detail: 'Network error' } },
    })

    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    const input = wrapper.find('input[type="text"]')
    await input.setValue('Smith')
    await wrapper.find('button').trigger('click')
    await flushPromises()

    expect(wrapper.text()).toContain('Search Error')

    // Click Try Again button
    const retryButton = wrapper.find('button.retry-button')
    await retryButton.trigger('click')

    // Error should be cleared
    expect(wrapper.text()).not.toContain('Search Error')
  })

  it('supports search on Enter key press', async () => {
    const mockResults = [
      {
        id: '123',
        husband_name: 'John Smith',
        wife_name: 'Jane Doe',
        marriage_date: '2005-06-20',
        marriage_place: 'Boston, MA',
        children_count: 2,
        summary: 'John Smith & Jane Doe (2005)',
      },
    ]

    vi.mocked(apiService.searchFamilies).mockResolvedValue(mockResults)

    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    const input = wrapper.find('input[type="text"]')
    await input.setValue('Smith')
    await input.trigger('keyup.enter')
    await flushPromises()

    expect(apiService.searchFamilies).toHaveBeenCalled()
    expect(wrapper.text()).toContain('John Smith & Jane Doe')
  })

  it('shows server connection error on mount if health check fails', async () => {
    vi.mocked(apiService.healthCheck).mockResolvedValue(false)

    const wrapper = mount(FamilySearch, {
      global: {
        plugins: [mockRouter],
      },
    })

    await flushPromises()

    expect(wrapper.text()).toContain('Unable to connect to the server')
  })
})
