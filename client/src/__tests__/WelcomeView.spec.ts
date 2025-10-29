import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import WelcomeView from '@/views/WelcomeView.vue'

describe('WelcomeView.vue', () => {
  let mockRouter: ReturnType<typeof createRouter>

  beforeEach(() => {
    mockRouter = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/', name: 'welcome', component: { template: '<div>Home</div>' } },
        { path: '/upload', name: 'upload', component: { template: '<div>Upload</div>' } },
        { path: '/manage', name: 'manage', component: { template: '<div>Manage</div>' } },
        { path: '/families/create', name: 'create-family', component: { template: '<div>Create Family</div>' } },
      ],
    })
  })

  it('renders all action cards correctly', () => {
    const wrapper = mount(WelcomeView, {
      global: {
        plugins: [mockRouter],
      },
    })

    // Check that all 3 cards are present
    const actionCards = wrapper.findAll('.action-card')
    expect(actionCards).toHaveLength(3)

    // Check card content
    expect(wrapper.text()).toContain('Upload Family File')
    expect(wrapper.text()).toContain('Search & Manage Families')
    expect(wrapper.text()).toContain('Create a family')
  })

  it('has navigation functions available', () => {
    const wrapper = mount(WelcomeView, {
      global: {
        plugins: [mockRouter],
      },
    })
    const vm = wrapper.vm as unknown as {
      navigateToUpload: () => void
      navigateToManage: () => void
      navigateToCreateFamily: () => void
    }

    // Check that navigation functions exist
    expect(typeof vm.navigateToUpload).toBe('function')
    expect(typeof vm.navigateToManage).toBe('function')
    expect(typeof vm.navigateToCreateFamily).toBe('function')
  })

  it('calls navigation functions without errors', async () => {
    const wrapper = mount(WelcomeView, {
      global: {
        plugins: [mockRouter],
      },
    })
    const vm = wrapper.vm as unknown as {
      navigateToUpload: () => void
      navigateToManage: () => void
      navigateToCreateFamily: () => void
    }

    // Check that functions can be called without errors
    expect(() => vm.navigateToUpload()).not.toThrow()
    expect(() => vm.navigateToManage()).not.toThrow()
    expect(() => vm.navigateToCreateFamily()).not.toThrow()
  })

  it('displays correct content for create family card', () => {
    const wrapper = mount(WelcomeView, {
      global: {
        plugins: [mockRouter],
      },
    })

    const createFamilyCard = wrapper.find('.create-family-card')
    expect(createFamilyCard.text()).toContain('Create a family')
    expect(createFamilyCard.text()).toContain('Create a new family by adding parents, marriage information and more')
    expect(createFamilyCard.text()).toContain('Adding parents')
    expect(createFamilyCard.text()).toContain('Marriage information')
    expect(createFamilyCard.text()).toContain('Children handling')
    expect(createFamilyCard.text()).toContain('Family events')
  })

  it('applies correct CSS classes to create family card', () => {
    const wrapper = mount(WelcomeView, {
      global: {
        plugins: [mockRouter],
      },
    })

    const createFamilyCard = wrapper.find('.create-family-card')
    expect(createFamilyCard.classes()).toContain('action-card')
    expect(createFamilyCard.classes()).toContain('create-family-card')
  })
})
