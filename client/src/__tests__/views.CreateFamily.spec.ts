// typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import CreateFamily from '@/views/CreateFamily.vue'
import { familyService } from '@/services/familyService'
import { personService } from '@/services/personService'
import type { AxiosResponse } from 'axios'

type CreateFamilyExposed = {
  loadPersonDetails: (type: 'husband' | 'wife', id: string) => Promise<void> | void
  validateMarriageDate: () => void
  submit: () => Promise<void>
  marriage_date: string
  marriageDateError: string
  husbandId: string
  wifeId: string
  error: string
  success: string
  queryHusband: string
  searchPersons: (q: string, type: 'husband' | 'wife' | 'child') => Promise<void> | void
  husbandOptions: Array<{ id: string; label: string }>
  openCreatePersonModal: (type: 'husband' | 'wife') => void
  showCreatePersonModal: boolean
  currentParentType: 'husband' | 'wife' | 'child'
}

// Mock the services
vi.mock('../services/familyService')
vi.mock('../services/personService')

describe('CreateFamily.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the form correctly', () => {
    const wrapper = mount(CreateFamily)

    expect(wrapper.find('h2').text()).toBe('👨\u200d👩\u200d👧\u200d👦 Create a Family')
    expect(wrapper.find('[data-cy="search-husband"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="search-wife"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="marriage-date"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="submit-family"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="back-to-home"]').exists()).toBe(true)
  })

  it('validates marriage date against parent birth dates', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    // Simulate parents with birth dates
    const mockHusband = {
      id: '1',
      first_name: 'John',
      last_name: 'Doe',
      birth_date: '1980-01-01',
      death_date: null
    }

    const mockWife = {
      id: '2',
      first_name: 'Jane',
      last_name: 'Smith',
      birth_date: '1985-05-15',
      death_date: null
    }

    // Mock API responses
    vi.mocked(personService.getPersonById)
      .mockResolvedValueOnce({ data: mockHusband } as AxiosResponse<unknown>)
      .mockResolvedValueOnce({ data: mockWife } as AxiosResponse<unknown>)

    // Select parents
    await vm.loadPersonDetails('husband', '1')
    await vm.loadPersonDetails('wife', '2')

    // Test a marriage date before husband's birth
    vm.marriage_date = '1979-12-31'
    vm.validateMarriageDate()

    expect(vm.marriageDateError).toBe("Marriage date cannot be before the husband's birth.")
  })

  it('validates marriage date against parent death dates', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    const mockHusband = {
      id: '1',
      first_name: 'John',
      last_name: 'Doe',
      birth_date: '1980-01-01',
      death_date: '2020-12-31'
    }

    vi.mocked(personService.getPersonById).mockResolvedValue({ data: mockHusband } as AxiosResponse<unknown>)
    await vm.loadPersonDetails('husband', '1')

    // Test a marriage date after death
    vm.marriage_date = '2021-01-01'
    vm.validateMarriageDate()

    expect(vm.marriageDateError).toBe("Marriage date cannot be after the husband's death.")
  })

  it('prevents future marriage dates', () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const tomorrowStr = tomorrow.toISOString().split('T')[0]

    vm.marriage_date = tomorrowStr
    vm.validateMarriageDate()

    expect(vm.marriageDateError).toBe('Marriage date cannot be in the future.')
  })

  it('requires at least one parent', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    // Don't select any parents
    vm.husbandId = ''
    vm.wifeId = ''

    await vm.submit()

    expect(vm.error).toBe('At least one parent is required.')
  })

  it('creates family successfully with valid data', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    const mockResponse = Promise.resolve({ data: { id: 'family-1' } } as AxiosResponse<{ id: string }>)
    vi.mocked(familyService.createFamily).mockReturnValue(mockResponse as unknown as ReturnType<typeof familyService.createFamily>)

    vm.husbandId = '1'
    vm.wifeId = '2'
    vm.marriage_date = '2005-06-20'

    await vm.submit()

    expect(familyService.createFamily).toHaveBeenCalledWith({
      husband_id: '1',
      wife_id: '2',
      marriage_date: '2005-06-20'
    })
    expect(vm.success).toBe('Family created.')
  })

  it('handles API errors gracefully', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    const mockError = {
      response: {
        data: { detail: 'Family with same spouses already exists' }
      }
    }
    vi.mocked(familyService.createFamily).mockRejectedValue(mockError)

    vm.husbandId = '1'
    vm.wifeId = '2'

    await vm.submit()

    expect(vm.error).toBe('Family with same spouses already exists')
  })

  it('searches for persons with debounce', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    const mockResponse = Promise.resolve({
      data: [
        { id: '1', first_name: 'John', last_name: 'Doe', sex: 'M', birth_date: '1980-01-01' }
      ]
    } as AxiosResponse<Array<unknown>>)
    vi.mocked(personService.searchPersonsByName).mockReturnValue(mockResponse as unknown as ReturnType<typeof personService.searchPersonsByName>)

    // Simulate the search
    vm.queryHusband = 'John'
    await vm.searchPersons('John', 'husband')

    expect(personService.searchPersonsByName).toHaveBeenCalledWith('John', { limit: 10 })
    expect(vm.husbandOptions).toHaveLength(1)
    expect(vm.husbandOptions[0].label).toContain('John Doe • n. 1980-01-01')
  })

  it('opens create person modal', () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    vm.openCreatePersonModal('husband')

    expect(vm.showCreatePersonModal).toBe(true)
    expect(vm.currentParentType).toBe('husband')
  })

  it('navigates to home when back to home button is clicked', async () => {
    const mockRouter = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'welcome', component: { template: '<div>Home</div>' } },
        { path: '/families/create', name: 'create-family', component: { template: '<div>Create Family</div>' } },
      ],
    })

    const wrapper = mount(CreateFamily, {
      global: {
        plugins: [mockRouter],
      },
    })

    // Check that the button exists
    const backButton = wrapper.find('[data-cy="back-to-home"]')
    expect(backButton.exists()).toBe(true)
    expect(backButton.text()).toContain('Go back to home')

    // Simulate clicking the button
    await backButton.trigger('click')

    // Check that navigation was called
    expect(mockRouter.currentRoute.value.path).toBe('/')
  })

})
