import { describe, it, expect } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import routes from '../router/index'

describe('Router', () => {
  it('has correct route definitions', () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: routes.options.routes,
    })

    const routeMap = router.getRoutes()

    // Check that essential routes exist
    const routePaths = routeMap.map((route) => route.path)

    expect(routePaths).toContain('/')
    expect(routePaths).toContain('/family/:id')
  })

  it('navigates to home route', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: routes.options.routes,
    })

    await router.push('/')

    expect(router.currentRoute.value.path).toBe('/')
    expect(router.currentRoute.value.name).toBe('welcome')
  })

  it('navigates to family tree route with id parameter', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: routes.options.routes,
    })

    const familyId = '123e4567-e89b-12d3-a456-426614174000'
    await router.push(`/family/${familyId}`)

    expect(router.currentRoute.value.path).toBe(`/family/${familyId}`)
    expect(router.currentRoute.value.name).toBe('family-tree')
    expect(router.currentRoute.value.params.id).toBe(familyId)
  })

  it('has correct route names', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: routes.options.routes,
    })

    // Navigate by name
    await router.push({ name: 'welcome' })
    expect(router.currentRoute.value.name).toBe('welcome')

    await router.push({
      name: 'family-tree',
      params: { id: '123' },
    })
    expect(router.currentRoute.value.name).toBe('family-tree')
  })

  it('supports navigation guards', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: routes.options.routes,
    })

    let guardCalled = false

    router.beforeEach((to, from, next) => {
      guardCalled = true
      next()
    })

    await router.push('/')

    expect(guardCalled).toBe(true)
  })
})
