// typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import CreateFamily from '../views/CreateFamily.vue'
import { familyService } from '../services/familyService'
import { personService } from '../services/personService'

// Mock the services
vi.mock('../services/familyService')
vi.mock('../services/personService')

describe('CreateFamily.vue', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the form correctly', () => {
    const wrapper = mount(CreateFamily)

    expect(wrapper.find('h2').text()).toBe('👨\u200d👩\u200d👧\u200d👦 Créer une famille')
    expect(wrapper.find('[data-cy="search-husband"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="search-wife"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="marriage-date"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="submit-family"]').exists()).toBe(true)
    expect(wrapper.find('[data-cy="back-to-home"]').exists()).toBe(true)
  })

  it('validates marriage date against parent birth dates', async () => {
    const wrapper = mount(CreateFamily)

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
      .mockResolvedValueOnce({ data: mockHusband })
      .mockResolvedValueOnce({ data: mockWife })

    // Select parents
    await wrapper.vm.loadPersonDetails('1', 'husband')
    await wrapper.vm.loadPersonDetails('2', 'wife')

    // Test a marriage date before husband's birth
    wrapper.vm.marriage_date = '1979-12-31'
    wrapper.vm.validateMarriageDate()

    expect(wrapper.vm.marriageDateError).toBe('La date de mariage ne peut pas être antérieure à la naissance de la femme.')
  })

  it('validates marriage date against parent death dates', async () => {
    const wrapper = mount(CreateFamily)

    const mockHusband = {
      id: '1',
      first_name: 'John',
      last_name: 'Doe',
      birth_date: '1980-01-01',
      death_date: '2020-12-31'
    }

    vi.mocked(personService.getPersonById).mockResolvedValue({ data: mockHusband })
    await wrapper.vm.loadPersonDetails('1', 'husband')

    // Test a marriage date after death
    wrapper.vm.marriage_date = '2021-01-01'
    wrapper.vm.validateMarriageDate()

    expect(wrapper.vm.marriageDateError).toBe('La date de mariage ne peut pas être postérieure au décès de la femme.')
  })

  it('prevents future marriage dates', () => {
    const wrapper = mount(CreateFamily)

    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    const tomorrowStr = tomorrow.toISOString().split('T')[0]

    wrapper.vm.marriage_date = tomorrowStr
    wrapper.vm.validateMarriageDate()

    expect(wrapper.vm.marriageDateError).toBe('La date de mariage ne peut pas être dans le futur.')
  })

  it('requires at least one parent', async () => {
    const wrapper = mount(CreateFamily)

    // Don't select any parents
    wrapper.vm.husbandId = ''
    wrapper.vm.wifeId = ''

    await wrapper.vm.submit()

    expect(wrapper.vm.error).toBe('Au moins un parent est requis.')
  })

  it('creates family successfully with valid data', async () => {
    const wrapper = mount(CreateFamily)

    const mockResponse = { data: { id: 'family-1' } }
    vi.mocked(familyService.createFamily).mockResolvedValue(mockResponse)

    wrapper.vm.husbandId = '1'
    wrapper.vm.wifeId = '2'
    wrapper.vm.marriage_date = '2005-06-20'

    await wrapper.vm.submit()

    expect(familyService.createFamily).toHaveBeenCalledWith({
      husband_id: '1',
      wife_id: '2',
      marriage_date: '2005-06-20'
    })
    expect(wrapper.vm.success).toBe('Famille créée.')
  })

  it('handles API errors gracefully', async () => {
    const wrapper = mount(CreateFamily)

    const mockError = {
      response: {
        data: { detail: 'Family with same spouses already exists' }
      }
    }
    vi.mocked(familyService.createFamily).mockRejectedValue(mockError)

    wrapper.vm.husbandId = '1'
    wrapper.vm.wifeId = '2'

    await wrapper.vm.submit()

    expect(wrapper.vm.error).toBe('Family with same spouses already exists')
  })

  it('searches for persons with debounce', async () => {
    const wrapper = mount(CreateFamily)

    const mockResponse = {
      data: [
        { id: '1', first_name: 'John', last_name: 'Doe', sex: 'M', birth_date: '1980-01-01' }
      ]
    }
    vi.mocked(personService.searchPersonsByName).mockResolvedValue(mockResponse)

    // Simulate the search
    wrapper.vm.queryHusband = 'John'
    await wrapper.vm.searchPersons('John', 'husband')

    expect(personService.searchPersonsByName).toHaveBeenCalledWith('John', { limit: 10 })
    expect(wrapper.vm.husbandOptions).toHaveLength(1)
    expect(wrapper.vm.husbandOptions[0].label).toContain('John Doe • n. 1980-01-01')
  })

  it('opens create person modal', () => {
    const wrapper = mount(CreateFamily)

    wrapper.vm.openCreatePersonModal('husband')

    expect(wrapper.vm.showCreatePersonModal).toBe(true)
    expect(wrapper.vm.currentParentType).toBe('husband')
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
    expect(backButton.text()).toContain('Retour à l\'accueil')

    // Simulate clicking the button
    await backButton.trigger('click')

    // Check that navigation was called
    expect(mockRouter.currentRoute.value.path).toBe('/')
  })

})
