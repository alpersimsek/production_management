import { createRouter, createWebHistory } from 'vue-router'
import { authGuard } from './guards'

const Login = () => import('@/pages/Login.vue')
const Dashboard = () => import('@/pages/Dashboard.vue')
const Orders = () => import('@/pages/Orders.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: Login },
    {
      path: '/',
      component: () => import('@/layouts/DefaultLayout.vue'),
      beforeEnter: authGuard,
      children: [
        { path: '', redirect: { name: 'dashboard' } },
        { path: 'dashboard', name: 'dashboard', component: Dashboard },
        { path: 'orders', name: 'orders', component: Orders }
      ]
    }
  ]
})

export default router
