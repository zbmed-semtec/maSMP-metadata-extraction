import { createRouter, createWebHistory } from 'vue-router';
import HomePage from '../components/HomePage.vue';
import MetadataDisplay from '@/components/MetadataDisplay.vue';

const routes = [
  {
    path: '/',
    name: 'HomePage',
    component: HomePage,
  },
  {
    path: '/metadata',
    name: 'MetadataDisplay',
    component: MetadataDisplay,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;