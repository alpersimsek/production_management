import { createRouter, createWebHistory } from 'vue-router'
import { authGuard } from './guards'

const Login = () => import('@/pages/Login.vue')
const Dashboard = () => import('@/pages/Dashboard.vue')
const Orders = () => import('@/pages/Orders.vue')
const Customers = () => import('@/pages/Customers.vue')
const Products = () => import('@/pages/Products.vue')
const ProductionJobs = () => import('@/pages/ProductionJobs.vue')
const Packaging = () => import('@/pages/Packaging.vue')
const Warehouses = () => import('@/pages/Warehouses.vue')
const Shipments = () => import('@/pages/Shipments.vue')
const Analytics = () => import('@/pages/Analytics.vue')
const Settings = () => import('@/pages/Settings.vue')

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: Login },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      beforeEnter: authGuard,
      children: [
        { path: '', redirect: { name: 'dashboard' } },
        { path: 'dashboard', name: 'dashboard', component: Dashboard },
        { path: 'customers', name: 'customers', component: Customers },
        { path: 'products', name: 'products', component: Products },
        { path: 'orders', name: 'orders', component: Orders },
        { path: 'production-jobs', name: 'production-jobs', component: ProductionJobs },
        { path: 'packaging', name: 'packaging', component: Packaging },
        { path: 'warehouses', name: 'warehouses', component: Warehouses },
        { path: 'shipments', name: 'shipments', component: Shipments },
        { path: 'analytics', name: 'analytics', component: Analytics },
        { path: 'settings', name: 'settings', component: Settings }
      ]
    }
  ]
})

export default router
