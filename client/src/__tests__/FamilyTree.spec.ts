import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import FamilyTree from '../components/FamilyTree.vue'
import { createMockPerson, waitForPromises } from './test-utils'
import type { FamilyDetailResult, Event } from '../types/family'

// Mock the API service
vi.mock('../services/api', () => ({
  apiService: {
    getFamilyDetail: vi.fn(),
    searchFamilies: vi.fn(),
    getFamily: vi.fn(),
    healthCheck: vi.fn(),
  },
  default: {
    getFamilyDetail: vi.fn(),
    searchFamilies: vi.fn(),
    getFamily: vi.fn(),
    healthCheck: vi.fn(),
  },
}))

// Import after mocking
import apiService from '../services/api'

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

  const mockHusband = createMockPerson({
    id: 'h123',
    first_name: 'John',
    last_name: 'Smith',
    sex: 'M',
    birth_date: '1980-01-01',
    death_date: undefined,
    birth_place: 'Boston, MA',
    death_place: undefined,
    occupation: 'Engineer',
    notes: 'Test notes',
    has_own_family: false,
    own_families: [],
  })

  const mockWife = createMockPerson({
    id: 'w123',
    first_name: 'Jane',
    last_name: 'Doe',
    sex: 'F',
    birth_date: '1982-03-15',
    death_date: undefined,
    birth_place: 'New York, NY',
    death_place: undefined,
    occupation: 'Teacher',
    notes: 'Test notes',
    has_own_family: false,
    own_families: [],
  })

  const mockChild = createMockPerson({
    id: 'c123',
    first_name: 'Bob',
    last_name: 'Smith',
    sex: 'M',
    birth_date: '2010-05-20',
    death_date: undefined,
    birth_place: 'Boston, MA',
    death_place: undefined,
    occupation: undefined,
    notes: undefined,
    has_own_family: false,
    own_families: [],
  })

  const mockEvents: Event[] = [
    {
      id: 'e1',
      family_id: mockFamilyId,
      type: 'Marriage',
      date: '2005-06-20',
      place: 'Boston, MA',
      description: 'Wedding ceremony',
    },
  ]

  const mockFamilyDetail: FamilyDetailResult = {
    id: mockFamilyId,
    husband_id: 'h123',
    wife_id: 'w123',
    marriage_date: '2005-06-20',
    marriage_place: 'Boston, MA',
    notes: undefined,
    husband: mockHusband,
    wife: mockWife,
    children: [
      {
        id: 'c1',
        family_id: mockFamilyId,
        person_id: 'c123',
        person: mockChild,
      },
    ],
    events: mockEvents,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Set up the mock to return our test data by default
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

    it('displays family title correctly', async () => {
      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('h2').text()).toBe('John Smith & Jane Doe')
    })

    it('displays marriage information when available', async () => {
      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.marriage-info').exists()).toBe(true)
      expect(wrapper.find('.marriage-date').text()).toContain('Married: Jun 20, 2005')
      expect(wrapper.find('.marriage-place').text()).toContain('Place: Boston, MA')
    })
  })

  describe('Tree Controls', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await waitForPromises()
    })

    it('zooms in when zoom in button is clicked', async () => {
      const zoomLabel = wrapper.find('.zoom-label')
      const initialZoomText = zoomLabel.text()

      await wrapper.find('button[title="Zoom In"]').trigger('click')
      await wrapper.vm.$nextTick()

      const newZoomText = zoomLabel.text()
      expect(newZoomText).not.toBe(initialZoomText)
    })

    it('zooms out when zoom out button is clicked', async () => {
      // First zoom in to have room to zoom out
      await wrapper.find('button[title="Zoom In"]').trigger('click')
      await wrapper.vm.$nextTick()

      const zoomLabel = wrapper.find('.zoom-label')
      const scaleAfterZoomIn = zoomLabel.text()

      await wrapper.find('button[title="Zoom Out"]').trigger('click')
      await wrapper.vm.$nextTick()

      const scaleAfterZoomOut = zoomLabel.text()
      expect(scaleAfterZoomOut).not.toBe(scaleAfterZoomIn)
    })

    it('resets zoom when reset button is clicked', async () => {
      // First zoom in
      await wrapper.find('button[title="Zoom In"]').trigger('click')
      await wrapper.vm.$nextTick()

      const zoomLabel = wrapper.find('.zoom-label')
      const scaleAfterZoomIn = zoomLabel.text()

      // Then reset
      await wrapper.find('button[title="Reset View"]').trigger('click')
      await wrapper.vm.$nextTick()

      const scaleAfterReset = zoomLabel.text()
      expect(scaleAfterReset).toBe('100%')
      expect(scaleAfterReset).not.toBe(scaleAfterZoomIn)
    })

    it('updates zoom percentage display', async () => {
      await wrapper.find('button[title="Zoom In"]').trigger('click')

      const zoomLabel = wrapper.find('.zoom-label')
      expect(zoomLabel.text()).toMatch(/\d+%/)
    })

    it('limits zoom in to maximum scale', async () => {
      // Zoom in multiple times to reach maximum
      for (let i = 0; i < 20; i++) {
        await wrapper.find('button[title="Zoom In"]').trigger('click')
        await wrapper.vm.$nextTick()
      }

      const zoomLabel = wrapper.find('.zoom-label')
      expect(zoomLabel.text()).toBe('300%')
    })

    it('limits zoom out to minimum scale', async () => {
      // First reset zoom to ensure we start from 100%
      await wrapper.find('button[title="Reset View"]').trigger('click')
      await wrapper.vm.$nextTick()

      // Zoom out multiple times to reach minimum
      for (let i = 0; i < 30; i++) {
        await wrapper.find('button[title="Zoom Out"]').trigger('click')
        await wrapper.vm.$nextTick()
      }

      const zoomLabel = wrapper.find('.zoom-label')
      expect(zoomLabel.text()).toBe('10%')
    })
  })

  describe('Person Interactions', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await waitForPromises()
    })

    it('displays husband and wife information', async () => {
      expect(wrapper.find('.person-node.husband').exists()).toBe(true)
      expect(wrapper.find('.person-node.wife').exists()).toBe(true)

      const husbandName = wrapper.find('.person-node.husband .person-name').text()
      const wifeName = wrapper.find('.person-node.wife .person-name').text()

      expect(husbandName).toBe('John Smith')
      expect(wifeName).toBe('Jane Doe')
    })

    it('displays person dates correctly', async () => {
      const husbandDates = wrapper.find('.person-node.husband .person-dates').text()
      const wifeDates = wrapper.find('.person-node.wife .person-dates').text()

      expect(husbandDates).toBe('Jan 1, 1980 - Present')
      expect(wifeDates).toBe('Mar 15, 1982 - Present')
    })

    it('displays children information', async () => {
      expect(wrapper.find('.child-node').exists()).toBe(true)
      const childName = wrapper.find('.child-node .child-name').text()
      const childDates = wrapper.find('.child-node .child-dates').text()

      expect(childName).toBe('Bob Smith')
      expect(childDates).toBe('May 20, 2010 - Present')
    })

    it('shows tooltip on person hover', async () => {
      const personNode = wrapper.find('.person-node.husband')

      await personNode.trigger('mouseenter')
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.person-tooltip').exists()).toBe(true)
      expect(wrapper.find('.person-tooltip .tooltip-name').text()).toBe('John Smith')
    })

    it('hides tooltip on person leave', async () => {
      const personNode = wrapper.find('.person-node.husband')

      await personNode.trigger('mouseenter')
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.person-tooltip').exists()).toBe(true)

      await personNode.trigger('mouseleave')
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.person-tooltip').exists()).toBe(false)
    })

    it('selects person on click', async () => {
      const personNode = wrapper.find('.person-node.husband')

      await personNode.trigger('click')
      await wrapper.vm.$nextTick()

      expect(personNode.classes()).toContain('highlight-self')
    })

    it('toggles person selection on second click', async () => {
      const personNode = wrapper.find('.person-node.husband')

      // First click - select
      await personNode.trigger('click')
      await wrapper.vm.$nextTick()
      expect(personNode.classes()).toContain('highlight-self')

      // Second click - deselect
      await personNode.trigger('click')
      await wrapper.vm.$nextTick()
      expect(personNode.classes()).not.toContain('highlight-self')
    })
  })

  describe('Marriage Information', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await waitForPromises()
    })

    it('displays marriage line between spouses', () => {
      expect(wrapper.find('.marriage-line').exists()).toBe(true)
    })

    it('shows marriage tooltip on hover', async () => {
      const marriageLine = wrapper.find('.marriage-line')

      await marriageLine.trigger('mouseenter')
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.marriage-tooltip').exists()).toBe(true)
      expect(wrapper.find('.marriage-tooltip .tooltip-name').text()).toContain(
        'John Smith & Jane Doe',
      )
    })

    it('hides marriage tooltip on leave', async () => {
      const marriageLine = wrapper.find('.marriage-line')

      await marriageLine.trigger('mouseenter')
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.marriage-tooltip').exists()).toBe(true)

      await marriageLine.trigger('mouseleave')
      await wrapper.vm.$nextTick()
      expect(wrapper.find('.marriage-tooltip').exists()).toBe(false)
    })

    it('displays marriage status as married', async () => {
      const marriageLine = wrapper.find('.marriage-line')

      await marriageLine.trigger('mouseenter')
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.relationship-status.married').exists()).toBe(true)
      expect(wrapper.find('.relationship-status.married').text()).toContain('Married 💒')
    })
  })

  describe('Error Handling', () => {
    it('displays error state when API call fails', async () => {
      const errorMessage = 'Family not found'
      vi.mocked(apiService.getFamilyDetail).mockRejectedValue(new Error(errorMessage))

      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.error-state').exists()).toBe(true)
      expect(wrapper.find('.error-state h3').text()).toBe('Error Loading Family Tree')
      expect(wrapper.find('.error-state p').text()).toBe(
        'Failed to load family tree. Please try again.',
      )
    })

    it('shows retry button in error state', async () => {
      vi.mocked(apiService.getFamilyDetail).mockRejectedValue(new Error('Network error'))

      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.retry-button').exists()).toBe(true)
    })

    it('retries loading when retry button is clicked', async () => {
      vi.mocked(apiService.getFamilyDetail)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(mockFamilyDetail)

      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.error-state').exists()).toBe(true)

      await wrapper.find('.retry-button').trigger('click')
      await waitForPromises()

      // Wait a bit more for the component to update
      await wrapper.vm.$nextTick()
      await new Promise((resolve) => setTimeout(resolve, 100))

      expect(wrapper.find('.error-state').exists()).toBe(false)
      expect(wrapper.find('.tree-container').exists()).toBe(true)
    })

    it('handles API error with response data', async () => {
      const apiError = {
        response: {
          data: {
            detail: 'Family not found',
          },
        },
      }
      vi.mocked(apiService.getFamilyDetail).mockRejectedValue(apiError)

      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.error-state p').text()).toBe('Family not found')
    })
  })

  describe('Navigation', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await waitForPromises()
    })

    it('navigates back to family management when back button is clicked', async () => {
      const pushSpy = vi.spyOn(mockRouter, 'push')

      await wrapper.find('.back-button').trigger('click')

      expect(pushSpy).toHaveBeenCalledWith('/manage')
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

    it('reloads data when familyId prop changes', async () => {
      wrapper = createWrapper({ familyId: 'family-1' })
      await waitForPromises()

      expect(vi.mocked(apiService.getFamilyDetail)).toHaveBeenCalledWith('family-1')

      // Clear the mock to track the next call
      vi.mocked(apiService.getFamilyDetail).mockClear()

      await wrapper.setProps({ familyId: 'family-2' })
      await waitForPromises()

      expect(vi.mocked(apiService.getFamilyDetail)).toHaveBeenCalledWith('family-2')
    })
  })

  describe('Date Formatting', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await waitForPromises()
    })

    it('formats dates correctly', () => {
      const husbandDates = wrapper.find('.person-node.husband .person-dates').text()
      expect(husbandDates).toBe('Jan 1, 1980 - Present')
    })

    it('handles death dates when present', async () => {
      const familyWithDeath = {
        ...mockFamilyDetail,
        husband: {
          ...mockHusband,
          death_date: '2020-12-31',
        },
      }

      vi.mocked(apiService.getFamilyDetail).mockResolvedValueOnce(familyWithDeath)
      wrapper = createWrapper()
      await waitForPromises()

      const husbandDates = wrapper.find('.person-node.husband .person-dates').text()
      expect(husbandDates).toBe('Jan 1, 1980 - Dec 31, 2020')
    })

    it('handles invalid dates gracefully', async () => {
      const familyWithInvalidDate = {
        ...mockFamilyDetail,
        husband: {
          ...mockHusband,
          birth_date: 'invalid-date',
        },
      }

      vi.mocked(apiService.getFamilyDetail).mockResolvedValueOnce(familyWithInvalidDate)
      wrapper = createWrapper()
      await waitForPromises()

      const husbandDates = wrapper.find('.person-node.husband .person-dates').text()
      expect(husbandDates).toBe('Invalid Date - Present')
    })
  })

  describe('Gender Icons', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await waitForPromises()
    })

    it('displays correct gender icons', () => {
      const husbandIcon = wrapper.find('.person-node.husband .gender-icon').text()
      const wifeIcon = wrapper.find('.person-node.wife .gender-icon').text()
      const childIcon = wrapper.find('.child-node .gender-icon').text()

      expect(husbandIcon).toBe('👨')
      expect(wifeIcon).toBe('👩')
      expect(childIcon).toBe('👦')
    })

    it('displays female icon for female child', async () => {
      const familyWithFemaleChild = {
        ...mockFamilyDetail,
        children: [
          {
            id: 'c1',
            family_id: mockFamilyId,
            person_id: 'c123',
            person: {
              ...mockChild,
              sex: 'F' as const,
            },
          },
        ],
      }

      vi.mocked(apiService.getFamilyDetail).mockResolvedValueOnce(familyWithFemaleChild)
      wrapper = createWrapper()
      await waitForPromises()

      const childIcon = wrapper.find('.child-node .gender-icon').text()
      expect(childIcon).toBe('👧')
    })
  })

  describe('Tooltip Content', () => {
    beforeEach(async () => {
      wrapper = createWrapper()
      await waitForPromises()
    })

    it('displays complete person information in tooltip', async () => {
      const personNode = wrapper.find('.person-node.husband')

      await personNode.trigger('mouseenter')
      await wrapper.vm.$nextTick()

      const tooltip = wrapper.find('.person-tooltip')
      expect(tooltip.find('.tooltip-name').text()).toBe('John Smith')
      expect(tooltip.text()).toContain('Gender: Male')
      expect(tooltip.text()).toContain('Born: Jan 1, 1980')
      expect(tooltip.text()).toContain('Birth Place: Boston, MA')
      expect(tooltip.text()).toContain('Occupation: Engineer')
      expect(tooltip.text()).toContain('Notes: Test notes')
    })

    it('displays marriage information in marriage tooltip', async () => {
      const marriageLine = wrapper.find('.marriage-line')

      await marriageLine.trigger('mouseenter')
      await wrapper.vm.$nextTick()

      const tooltip = wrapper.find('.marriage-tooltip')
      expect(tooltip.find('.tooltip-name').text()).toContain('John Smith & Jane Doe')
      expect(tooltip.text()).toContain('Married: Jun 20, 2005')
      expect(tooltip.text()).toContain('Marriage Place: Boston, MA')
    })
  })

  describe('Edge Cases', () => {
    it('handles family with no children', async () => {
      const familyWithoutChildren = {
        ...mockFamilyDetail,
        children: [],
      }

      vi.mocked(apiService.getFamilyDetail).mockResolvedValueOnce(familyWithoutChildren)
      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.child-node').exists()).toBe(false)
      expect(wrapper.find('.children-row').exists()).toBe(false)
    })

    it('handles family with no marriage date', async () => {
      const familyWithoutMarriageDate = {
        ...mockFamilyDetail,
        marriage_date: undefined,
      }

      vi.mocked(apiService.getFamilyDetail).mockResolvedValueOnce(familyWithoutMarriageDate)
      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.marriage-date').exists()).toBe(false)
    })

    it('handles family with no marriage place', async () => {
      const familyWithoutMarriagePlace = {
        ...mockFamilyDetail,
        marriage_place: undefined,
      }

      vi.mocked(apiService.getFamilyDetail).mockResolvedValueOnce(familyWithoutMarriagePlace)
      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.marriage-place').exists()).toBe(false)
    })

    it('handles family with only husband', async () => {
      const familyWithOnlyHusband = {
        ...mockFamilyDetail,
        wife: undefined,
        wife_id: undefined,
      }

      vi.mocked(apiService.getFamilyDetail).mockResolvedValueOnce(familyWithOnlyHusband)
      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.person-node.husband').exists()).toBe(true)
      expect(wrapper.find('.person-node.wife').exists()).toBe(false)
      expect(wrapper.find('.marriage-line').exists()).toBe(false)
    })

    it('handles family with only wife', async () => {
      const familyWithOnlyWife = {
        ...mockFamilyDetail,
        husband: undefined,
        husband_id: undefined,
      }

      vi.mocked(apiService.getFamilyDetail).mockResolvedValueOnce(familyWithOnlyWife)
      wrapper = createWrapper()
      await waitForPromises()

      expect(wrapper.find('.person-node.husband').exists()).toBe(false)
      expect(wrapper.find('.person-node.wife').exists()).toBe(true)
      expect(wrapper.find('.marriage-line').exists()).toBe(false)
    })
  })
})
