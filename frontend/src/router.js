import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('./pages/StudioHome.vue'),
  },
  {
    path: '/editor',
    name: 'editor',
    component: () => import('./pages/EditorPage.vue'),
  },
  {
    path: '/merge',
    name: 'merge',
    component: () => import('./pages/MergePage.vue'),
  },
  {
    path: '/split',
    name: 'split',
    component: () => import('./pages/SplitPage.vue'),
  },
  {
    path: '/compress',
    name: 'compress',
    component: () => import('./pages/CompressPage.vue'),
  },
  {
    path: '/convert',
    name: 'convert',
    component: () => import('./pages/ConvertPage.vue'),
  },
  {
    path: '/templates',
    name: 'templates',
    component: () => import('./pages/TemplatePage.vue'),
  },
  {
    path: '/templates/new',
    name: 'template-new',
    component: () => import('./components/template/TemplateEditor.vue'),
  },
  {
    path: '/templates/:name/edit',
    name: 'template-edit',
    component: () => import('./components/template/TemplateEditor.vue'),
  },
  {
    path: '/templates/:name/generate',
    name: 'template-generate',
    component: () => import('./components/template/TemplateGenerator.vue'),
  },
  {
    path: '/batch',
    name: 'batch',
    component: () => import('./pages/BatchPage.vue'),
  },
]

const router = createRouter({
  history: createWebHistory('/pdf-studio'),
  routes,
})

export default router
