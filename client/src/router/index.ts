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
  history: createWebHistory(),
  routes,
})

export default router
