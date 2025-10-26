// typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, VueWrapper } from '@vue/test-utils'
import type { ComponentPublicInstance } from 'vue'
import CreatePersonModal from '../CreatePersonModal.vue'
import { personService } from '@/services/personService'

// Mock the service
vi.mock('@/services/personService', () => ({
  personService: {
    createPerson: vi.fn()
  }
}))

type Person = {
  id: string
  first_name: string
  last_name: string
  sex: 'M' | 'F' | 'U'
  birth_date: string | null
  birth_place: string | null
  death_date: string | null
  death_place: string | null
  notes: string | null
  occupation?: string | null
}

type ApiResponse<T> = { data: T }

describe('CreatePersonModal', () => {
  let wrapper: VueWrapper<ComponentPublicInstance>

  const defaultProps = {
    show: true,
    parentType: 'husband' as 'husband' | 'wife'
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('Rendering', () => {
    it('should not render when show prop is false', () => {
      wrapper = mount(CreatePersonModal, {
        props: {
          ...defaultProps,
          show: false
        }
      })

      expect(wrapper.find('.modal-overlay').exists()).toBe(false)
    })

    it('should render when show prop is true', () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      expect(wrapper.find('.modal-overlay').exists()).toBe(true)
      expect(wrapper.find('.modal').exists()).toBe(true)
      expect(wrapper.find('h3').text()).toBe('Create a New Person')
    })

    it('should render all form fields', () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      expect(wrapper.find('[data-cy="new-person-first-name"]').exists()).toBe(true)
      expect(wrapper.find('[data-cy="new-person-last-name"]').exists()).toBe(true)
      expect(wrapper.find('[data-cy="new-person-sex"]').exists()).toBe(true)
      expect(wrapper.find('[data-cy="new-person-birth-date"]').exists()).toBe(true)
      expect(wrapper.find('[data-cy="new-person-birth-place"]').exists()).toBe(true)
      expect(wrapper.find('[data-cy="new-person-death-date"]').exists()).toBe(true)
      expect(wrapper.find('[data-cy="new-person-death-place"]').exists()).toBe(true)
      expect(wrapper.find('[data-cy="new-person-notes"]').exists()).toBe(true)
    })

    it('should have required attribute on first name and last name fields', () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      expect(wrapper.find('[data-cy="new-person-first-name"]').attributes('required')).toBeDefined()
      expect(wrapper.find('[data-cy="new-person-last-name"]').attributes('required')).toBeDefined()
    })

    it('should render sex select with correct options', () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      const sexSelect = wrapper.find('[data-cy="new-person-sex"]')
      const options = sexSelect.findAll('option')

      expect(options).toHaveLength(3)
      expect(options[0].text()).toBe('Undefined')
      expect(options[0].attributes('value')).toBe('U')
      expect(options[1].text()).toBe('Male')
      expect(options[1].attributes('value')).toBe('M')
      expect(options[2].text()).toBe('Female')
      expect(options[2].attributes('value')).toBe('F')
    })
  })

  describe('User interactions', () => {
    it('should emit close event when clicking overlay', async () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('.modal-overlay').trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
      expect(wrapper.emitted('close')).toHaveLength(1)
    })

    it('should not emit close event when clicking modal content', async () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('.modal').trigger('click')

      expect(wrapper.emitted('close')).toBeFalsy()
    })

    it('should emit close event when clicking close button', async () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('.close-btn').trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
      expect(wrapper.emitted('close')).toHaveLength(1)
    })

    it('should emit close event when clicking cancel button', async () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('[data-cy="cancel-person-creation"]').trigger('click')

      expect(wrapper.emitted('close')).toBeTruthy()
      expect(wrapper.emitted('close')).toHaveLength(1)
    })

    it('should update form fields when user types', async () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      const firstNameInput = wrapper.find('[data-cy="new-person-first-name"]')
      const lastNameInput = wrapper.find('[data-cy="new-person-last-name"]')

      await firstNameInput.setValue('Jean')
      await lastNameInput.setValue('Dupont')

      expect((firstNameInput.element as HTMLInputElement).value).toBe('Jean')
      expect((lastNameInput.element as HTMLInputElement).value).toBe('Dupont')
    })
  })

  describe('Form validation', () => {
    it('should show error when submitting without required fields', async () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.find('.field-error').exists()).toBe(true)
      expect(wrapper.find('.field-error').text()).toBe('First name and last name are required')
    })

    it('should show error when submitting with only first name', async () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('[data-cy="new-person-first-name"]').setValue('Jean')
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.find('.field-error').exists()).toBe(true)
      expect(wrapper.find('.field-error').text()).toBe('First name and last name are required')
    })

    it('should show error when submitting with only last name', async () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('[data-cy="new-person-last-name"]').setValue('Dupont')
      await wrapper.find('form').trigger('submit.prevent')

      expect(wrapper.find('.field-error').exists()).toBe(true)
      expect(wrapper.find('.field-error').text()).toBe('First name and last name are required')
    })

    it('should not show error when both required fields are filled', async () => {
      const createdPerson: Person = {
        id: '123',
        first_name: 'Jean',
        last_name: 'Dupont',
        sex: 'M',
        birth_date: null,
        birth_place: null,
        death_date: null,
        death_place: null,
        notes: null,
        occupation: null
      }

      vi.mocked(personService.createPerson).mockResolvedValue({ data: createdPerson } as ApiResponse<Person>)

      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('[data-cy="new-person-first-name"]').setValue('Jean')
      await wrapper.find('[data-cy="new-person-last-name"]').setValue('Dupont')
      await wrapper.find('form').trigger('submit.prevent')

      // Wait for async operation
      await wrapper.vm.$nextTick()

      expect(wrapper.find('.field-error').exists()).toBe(false)
    })
  })

  describe('Person creation', () => {
    it('should call personService.createPerson with correct data', async () => {
      const mockPerson: Person = {
        id: '123',
        first_name: 'Jean',
        last_name: 'Dupont',
        sex: 'M',
        birth_date: '1980-01-01',
        birth_place: 'Paris',
        death_date: null,
        death_place: null,
        notes: 'Test notes'
      }

      vi.mocked(personService.createPerson).mockResolvedValue({ data: mockPerson } as ApiResponse<Person>)

      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('[data-cy="new-person-first-name"]').setValue('Jean')
      await wrapper.find('[data-cy="new-person-last-name"]').setValue('Dupont')
      await wrapper.find('[data-cy="new-person-sex"]').setValue('M')
      await wrapper.find('[data-cy="new-person-birth-date"]').setValue('1980-01-01')
      await wrapper.find('[data-cy="new-person-birth-place"]').setValue('Paris')
      await wrapper.find('[data-cy="new-person-notes"]').setValue('Test notes')

      await wrapper.find('form').trigger('submit.prevent')
      await wrapper.vm.$nextTick()

      expect(personService.createPerson).toHaveBeenCalledWith({
        first_name: 'Jean',
        last_name: 'Dupont',
        sex: 'M',
        birth_date: '1980-01-01',
        birth_place: 'Paris',
        death_date: null,
        death_place: null,
        notes: 'Test notes',
        occupation: null
      })
    })

    it('should emit personCreated event with created person data', async () => {
      const mockPerson: Person = {
        id: '123',
        first_name: 'Jean',
        last_name: 'Dupont',
        sex: 'M',
        birth_date: null,
        birth_place: null,
        death_date: null,
        death_place: null,
        notes: null
      }

      vi.mocked(personService.createPerson).mockResolvedValue({ data: mockPerson } as ApiResponse<Person>)

      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('[data-cy="new-person-first-name"]').setValue('Jean')
      await wrapper.find('[data-cy="new-person-last-name"]').setValue('Dupont')
      await wrapper.find('form').trigger('submit.prevent')

      // Wait for async operation
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(wrapper.emitted('personCreated')).toBeTruthy()
      expect(wrapper.emitted('personCreated')?.[0]).toEqual([mockPerson])
    })

    it('should show error message when person creation fails', async () => {
      const apiError = {
        response: {
          data: {
            detail: 'Erreur serveur'
          }
        }
      }

      vi.mocked(personService.createPerson).mockRejectedValue(apiError)

      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('[data-cy="new-person-first-name"]').setValue('Jean')
      await wrapper.find('[data-cy="new-person-last-name"]').setValue('Dupont')
      await wrapper.find('form').trigger('submit.prevent')

      // Wait for async operation
      await wrapper.vm.$nextTick()
      await new Promise(resolve => setTimeout(resolve, 0))

      expect(wrapper.find('.field-error').exists()).toBe(true)
      expect(wrapper.find('.field-error').text()).toBe('Erreur serveur')
    })

    it('should trim whitespace from text fields', async () => {
      const mockPerson: Person = {
        id: '123',
        first_name: 'Jean',
        last_name: 'Dupont',
        sex: 'U',
        birth_date: null,
        birth_place: null,
        death_date: null,
        death_place: null,
        notes: null
      }

      vi.mocked(personService.createPerson).mockResolvedValue({ data: mockPerson } as ApiResponse<Person>)

      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('[data-cy="new-person-first-name"]').setValue('  Jean  ')
      await wrapper.find('[data-cy="new-person-last-name"]').setValue('  Dupont  ')
      await wrapper.find('[data-cy="new-person-birth-place"]').setValue('  Paris  ')
      await wrapper.find('form').trigger('submit.prevent')

      await wrapper.vm.$nextTick()

      expect(personService.createPerson).toHaveBeenCalledWith({
        first_name: 'Jean',
        last_name: 'Dupont',
        sex: 'U',
        birth_date: null,
        birth_place: 'Paris',
        death_date: null,
        death_place: null,
        notes: null,
        occupation: null
      })
    })

    it('should disable submit button while creating person', async () => {
      const emptyPerson: Person = {
        id: '',
        first_name: '',
        last_name: '',
        sex: 'U',
        birth_date: null,
        birth_place: null,
        death_date: null,
        death_place: null,
        notes: null
      }

      vi.mocked(personService.createPerson).mockImplementation(
        () =>
          new Promise<ApiResponse<Person>>(resolve =>
            setTimeout(() => resolve({ data: emptyPerson }), 100)
          )
      )

      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('[data-cy="new-person-first-name"]').setValue('Jean')
      await wrapper.find('[data-cy="new-person-last-name"]').setValue('Dupont')

      const submitButton = wrapper.find('[data-cy="create-person-submit"]')
      expect(submitButton.attributes('disabled')).toBeUndefined()

      await wrapper.find('form').trigger('submit.prevent')
      await wrapper.vm.$nextTick()

      expect(submitButton.attributes('disabled')).toBeDefined()
    })
  })

  describe('Form reset', () => {
    it('should reset form when close event is triggered', async () => {
      wrapper = mount(CreatePersonModal, {
        props: defaultProps
      })

      await wrapper.find('[data-cy="new-person-first-name"]').setValue('Jean')
      await wrapper.find('[data-cy="new-person-last-name"]').setValue('Dupont')
      await wrapper.find('[data-cy="new-person-sex"]').setValue('M')

      await wrapper.find('.close-btn').trigger('click')
      await wrapper.vm.$nextTick()

      // Re-open modal
      await wrapper.setProps({ show: true })
      await wrapper.vm.$nextTick()

      const firstNameInput = wrapper.find('[data-cy="new-person-first-name"]')
      const lastNameInput = wrapper.find('[data-cy="new-person-last-name"]')
      const sexSelect = wrapper.find('[data-cy="new-person-sex"]')

      expect((firstNameInput.element as HTMLInputElement).value).toBe('')
      expect((lastNameInput.element as HTMLInputElement).value).toBe('')
      expect((sexSelect.element as HTMLSelectElement).value).toBe('U')
    })
  })
})
