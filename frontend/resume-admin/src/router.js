import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'layout',
    component: () => import('./views/Layout.vue'),
    children: [
      {
        path: '',
        name: 'resume-list',
        component: () => import('./views/ResumeList.vue')
      },
      {
        path: 'upload',
        name: 'resume-upload',
        component: () => import('./views/ResumeUpload.vue')
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
