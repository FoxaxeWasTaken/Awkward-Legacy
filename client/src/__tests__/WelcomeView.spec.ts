import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue'

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

    // Vérifier que les 3 cartes sont présentes
    const actionCards = wrapper.findAll('.action-card')
    expect(actionCards).toHaveLength(3)

    // Vérifier le contenu des cartes
    expect(wrapper.text()).toContain('Upload Family File')
    expect(wrapper.text()).toContain('Search & Manage Families')
    expect(wrapper.text()).toContain('Créer une famille')
  })

  it('has navigation functions available', () => {
    const wrapper = mount(WelcomeView, {
      global: {
        plugins: [mockRouter],
      },
    })

    // Vérifier que les fonctions de navigation existent
    expect(typeof wrapper.vm.navigateToUpload).toBe('function')
    expect(typeof wrapper.vm.navigateToManage).toBe('function')
    expect(typeof wrapper.vm.navigateToCreateFamily).toBe('function')
  })

  it('calls navigation functions without errors', async () => {
    const wrapper = mount(WelcomeView, {
      global: {
        plugins: [mockRouter],
      },
    })

    // Vérifier que les fonctions peuvent être appelées sans erreur
    expect(() => wrapper.vm.navigateToUpload()).not.toThrow()
    expect(() => wrapper.vm.navigateToManage()).not.toThrow()
    expect(() => wrapper.vm.navigateToCreateFamily()).not.toThrow()
  })

  it('displays correct content for create family card', () => {
    const wrapper = mount(WelcomeView, {
      global: {
        plugins: [mockRouter],
      },
    })

    const createFamilyCard = wrapper.find('.create-family-card')
    expect(createFamilyCard.text()).toContain('Créer une famille')
    expect(createFamilyCard.text()).toContain('Créez une nouvelle famille en ajoutant les parents et les informations de mariage')
    expect(createFamilyCard.text()).toContain('Ajout de parents')
    expect(createFamilyCard.text()).toContain('Informations de mariage')
    expect(createFamilyCard.text()).toContain('Gestion des enfants')
    expect(createFamilyCard.text()).toContain('Événements familiaux')
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
