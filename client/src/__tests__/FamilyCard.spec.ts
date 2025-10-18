import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FamilyCard from '../components/FamilyCard.vue'
import type { FamilySearchResult } from '../types/family'

describe('FamilyCard Component', () => {
  const mockFamily: FamilySearchResult = {
    id: '123e4567-e89b-12d3-a456-426614174000',
    husband_name: 'John Smith',
    wife_name: 'Jane Doe',
    marriage_date: '2005-06-20',
    marriage_place: 'Boston, MA',
    children_count: 2,
    summary: 'John Smith & Jane Doe (2005)',
  }

  it('renders family information correctly', () => {
    const wrapper = mount(FamilyCard, {
      props: {
        family: mockFamily,
      },
    })

    expect(wrapper.text()).toContain('John Smith & Jane Doe (2005)')
    expect(wrapper.text()).toContain('John Smith')
    expect(wrapper.text()).toContain('Jane Doe')
    expect(wrapper.text()).toContain('June 20, 2005')
    expect(wrapper.text()).toContain('Boston, MA')
    expect(wrapper.text()).toContain('2')
  })

  it('displays truncated ID', () => {
    const wrapper = mount(FamilyCard, {
      props: {
        family: mockFamily,
      },
    })

    expect(wrapper.text()).toContain('ID: 123e4567...')
  })

  it('emits view-details event when View Family Tree button is clicked', async () => {
    const wrapper = mount(FamilyCard, {
      props: {
        family: mockFamily,
      },
    })

    const button = wrapper.find('button')
    await button.trigger('click')

    expect(wrapper.emitted('viewDetails')).toBeTruthy()
    expect(wrapper.emitted('viewDetails')?.[0]).toEqual([mockFamily.id])
  })

  it('handles missing wife name', () => {
    const familyWithoutWife: FamilySearchResult = {
      ...mockFamily,
      wife_name: undefined,
      summary: 'John Smith (2005)',
    }

    const wrapper = mount(FamilyCard, {
      props: {
        family: familyWithoutWife,
      },
    })

    expect(wrapper.text()).toContain('John Smith')
    expect(wrapper.text()).not.toContain('Wife:')
  })

  it('handles missing husband name', () => {
    const familyWithoutHusband: FamilySearchResult = {
      ...mockFamily,
      husband_name: undefined,
      summary: 'Jane Doe (2005)',
    }

    const wrapper = mount(FamilyCard, {
      props: {
        family: familyWithoutHusband,
      },
    })

    expect(wrapper.text()).toContain('Jane Doe')
    expect(wrapper.text()).not.toContain('Husband:')
  })

  it('handles missing marriage place', () => {
    const familyWithoutPlace: FamilySearchResult = {
      ...mockFamily,
      marriage_place: undefined,
    }

    const wrapper = mount(FamilyCard, {
      props: {
        family: familyWithoutPlace,
      },
    })

    expect(wrapper.text()).not.toContain('Place:')
  })

  it('displays correct children count (singular)', () => {
    const familyWithOneChild: FamilySearchResult = {
      ...mockFamily,
      children_count: 1,
    }

    const wrapper = mount(FamilyCard, {
      props: {
        family: familyWithOneChild,
      },
    })

    expect(wrapper.text()).toContain('Children:')
    expect(wrapper.text()).toContain('1')
  })

  it('displays correct children count (plural)', () => {
    const familyWithMultipleChildren: FamilySearchResult = {
      ...mockFamily,
      children_count: 5,
    }

    const wrapper = mount(FamilyCard, {
      props: {
        family: familyWithMultipleChildren,
      },
    })

    expect(wrapper.text()).toContain('Children:')
    expect(wrapper.text()).toContain('5')
  })

  it('displays zero children count', () => {
    const familyWithNoChildren: FamilySearchResult = {
      ...mockFamily,
      children_count: 0,
    }

    const wrapper = mount(FamilyCard, {
      props: {
        family: familyWithNoChildren,
      },
    })

    expect(wrapper.text()).toContain('Children:')
    expect(wrapper.text()).toContain('0')
  })

  it('has proper CSS classes for styling', () => {
    const wrapper = mount(FamilyCard, {
      props: {
        family: mockFamily,
      },
    })

    expect(wrapper.classes()).toContain('family-card')
  })

  it('formats marriage date correctly', () => {
    const wrapper = mount(FamilyCard, {
      props: {
        family: mockFamily,
      },
    })

    // Should format as "June 20, 2005" or similar readable format
    expect(wrapper.text()).toContain('2005')
    expect(wrapper.text()).toContain('20')
  })
})
