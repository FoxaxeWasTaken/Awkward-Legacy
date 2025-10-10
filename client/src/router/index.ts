import { createRouter, createWebHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue'
import FamilyTreeView from '../views/FamilyTreeView.vue'
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
  }
})

// Global after hook - runs after navigation
router.afterEach((to, from) => {
  // Update page title
  document.title = to.meta.title || 'My Vue App'
})

export default router
