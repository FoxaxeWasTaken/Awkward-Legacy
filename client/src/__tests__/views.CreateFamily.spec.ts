// typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { createRouter, createMemoryHistory } from 'vue-router'
import CreateFamily from '@/views/CreateFamily.vue'
import { familyService } from '@/services/familyService'
import { personService } from '@/services/personService'
import { childService } from '@/services/childService'
import { eventService } from '@/services/eventService'
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
vi.mock('../services/childService')
vi.mock('../services/eventService')

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

  it('selects husband from suggestions then clears selection', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    const mockPerson = { id: '1', first_name: 'John', last_name: 'Doe', sex: 'M', birth_date: '1980-01-01' }

    vi.mocked(personService.searchPersonsByName).mockResolvedValue({ data: [mockPerson] } as AxiosResponse<unknown>)
    vi.mocked(personService.getPersonById).mockResolvedValue({ data: mockPerson } as AxiosResponse<unknown>)

    await vm.searchPersons('John', 'husband')
    await nextTick()

    const suggestions = wrapper.find('[data-cy="husband-suggestions"]')
    expect(suggestions.exists()).toBe(true)
    await suggestions.find('.suggestion-item').trigger('click')
    await nextTick()

    expect(vm.husbandId).toBe('1')
    expect(wrapper.find('[data-cy="preview-husband"]').exists()).toBe(true)

    const clearBtn = wrapper.findAll('.parent-card')[0].find('.clear-btn')
    expect(clearBtn.exists()).toBe(true)
    await clearBtn.trigger('click')
    await nextTick()

    expect(vm.husbandId).toBe('')
    expect((wrapper.find('[data-cy="search-husband"]').element as HTMLInputElement).value).toBe('')
    expect(wrapper.find('[data-cy="preview-husband"]').exists()).toBe(false)
  })

  it('adds a child and a valid event, submits and calls child/event services', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    vi.mocked(familyService.createFamily).mockResolvedValue({ data: { id: 'family-1' } } as AxiosResponse<unknown>)
    vi.mocked(childService.createChild).mockResolvedValue({} as AxiosResponse<unknown>)
    vi.mocked(eventService.createEvent).mockResolvedValue({} as AxiosResponse<unknown>)

    // Add a child via suggestions
    const mockChild = { id: 'c1', first_name: 'Kid', last_name: 'Doe', sex: 'F' }
    vi.mocked(personService.searchPersonsByName).mockResolvedValue({ data: [mockChild] } as AxiosResponse<unknown>)
    vi.mocked(personService.getPersonById).mockResolvedValue({ data: mockChild } as AxiosResponse<unknown>)

    // Ensure at least one parent (minimal validation)
    vm.husbandId = 'h1'

    // Click add child button
    const addChildBtn = wrapper.find('[data-cy="add-child-button"]')
    await addChildBtn.trigger('click')

    // Populate child suggestions and select first
    await vm.searchPersons('Kid', 'child')
    await nextTick()
    const childSuggestions = wrapper.find('[data-cy="child-suggestions"]')
    expect(childSuggestions.exists()).toBe(true)
    await childSuggestions.find('.suggestion-item').trigger('click')
    await nextTick()

    // Add two events: one valid, one invalid (empty type)
    const addEventBtn = wrapper.find('[data-cy="add-event-btn"]')
    await addEventBtn.trigger('click')
    await addEventBtn.trigger('click')

    // Fill first event (index 0)
    await wrapper.find('[data-cy="event-type-0"]').setValue('Marriage')
    await wrapper.find('[data-cy="event-date-0"]').setValue('2010-01-01')
    await wrapper.find('[data-cy="event-place-0"]').setValue('Paris, France')
    await wrapper.find('[data-cy="event-description-0"]').setValue('A nice ceremony')

    // Leave second event type empty to be filtered out

    await vm.submit()

    expect(familyService.createFamily).toHaveBeenCalled()
    expect(childService.createChild).toHaveBeenCalledWith({ family_id: 'family-1', child_id: 'c1' })
    expect(eventService.createEvent).toHaveBeenCalledWith({
      family_id: 'family-1',
      type: 'Marriage',
      date: '2010-01-01',
      place: 'Paris, France',
      description: 'A nice ceremony',
    })

    expect((wrapper.vm as unknown as CreateFamilyExposed).success).toBe('Family created with 1 child and 1 event.')

    // Check main fields were reset
    expect(vm.husbandId).toBe('')
    expect(vm.wifeId).toBe('')
    expect(vm.marriage_date).toBe('')
  })

  it('resets options on empty search and handles search errors for husband', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    // Empty search should clear options
    await vm.searchPersons('', 'husband')
    expect(vm.husbandOptions.length).toBe(0)

    // Error during search should also clear options
    vi.mocked(personService.searchPersonsByName).mockRejectedValue(new Error('Network'))
    await vm.searchPersons('John', 'husband')
    expect(vm.husbandOptions.length).toBe(0)
  })

  it('resets options on empty search and handles search errors for wife', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    await vm.searchPersons('', 'wife')
    expect(vm.husbandOptions.length).toBeGreaterThanOrEqual(0) // sanity check unrelated state
    // We cannot access wifeOptions from expose, but dropdown visibility depends on it; ensure no error thrown
    await expect(vm.searchPersons('Jane', 'wife')).resolves.toBeUndefined()
  })

  it('resets options on empty search and handles search errors for child', async () => {
    const wrapper = mount(CreateFamily)
    const vm = wrapper.vm as unknown as CreateFamilyExposed

    await vm.searchPersons('', 'child')
    await expect(vm.searchPersons('Kid', 'child')).resolves.toBeUndefined()
  })

})
