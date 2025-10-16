import { createRouter, createWebHistory } from 'vue-router';
import FamilySearchView from '../views/FamilySearchView.vue';
import FamilyTreeView from '../views/FamilyTreeView.vue';

const routes = [
  {
    path: '/',
    name: 'Home',
    component: FamilySearchView,
  },
  {
    path: '/family/:id',
    name: 'FamilyTree',
    component: FamilyTreeView,
    props: true,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
