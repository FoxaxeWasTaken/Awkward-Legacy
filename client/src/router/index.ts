// typescript
import { createRouter, createWebHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue'
import FamilyTreeView from '../views/FamilyTreeView.vue'
import CreateFamily from '../views/CreateFamily.vue'
import FileUploadView from '../views/FileUploadView.vue'
import FamilyManagementView from '../views/FamilyManagementView.vue'

const routes = [
  {
    path: '/',
    name: 'welcome',
    component: WelcomeView,
  },
  {
    path: '/search',
    redirect: '/manage',
  },
  {
    path: '/upload',
    name: 'upload',
    component: FileUploadView,
  },
  {
    path: '/manage',
    name: 'manage',
    component: FamilyManagementView,
  },
  {
    path: '/family/:id',
    name: 'family-tree',
    component: FamilyTreeView,
    props: true,
  },
  {
    path: '/families/create',
    name: 'create-family',
    component: CreateFamily,
    meta: { requiresAuth: false, title: 'Créer une famille' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  // Scroll behavior
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  },
})

// Global after hook - runs after navigation
router.afterEach((to, _from) => {
  // Ensure meta.title is a string before assigning to document.title
  const title = typeof to.meta?.title === 'string' ? to.meta.title : 'My Vue App'
  document.title = title
})

export default router
