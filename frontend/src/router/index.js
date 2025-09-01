/**
 * Vue Router configuration for the GDPR tool frontend
 * 
 * This file defines the application's routing structure, including route definitions,
 * navigation guards, and authentication checks. It handles route protection based on
 * user authentication status and admin privileges.
 * 
 * Key Features:
 * - Route definitions for all application views (login, dashboard, files, users, search, presets)
 * - Authentication guards that check for valid JWT tokens
 * - Admin role protection for sensitive routes (presets management)
 * - Automatic redirection based on authentication status
 * - Token expiration handling during navigation
 * 
 * Routes:
 * - / (redirects to /dashboard)
 * - /login: Login page (no auth required)
 * - /dashboard: Main dashboard (auth required)
 * - /files: File management (auth required)
 * - /users: User management (auth required)
 * - /search: Search masking records (auth required)
 * - /presets: Preset management (auth + admin required)
 * 
 * Navigation Guards:
 * - beforeEach: Checks authentication, token expiration, and admin privileges
 * - Redirects unauthenticated users to login
 * - Redirects authenticated users away from login page
 * - Handles token expiration with automatic logout
 */

import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue'),
      meta: { requiresAuth: false },
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/DashboardView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/files',
      name: 'files',
      component: () => import('../views/FilesView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/users',
      name: 'users',
      component: () => import('../views/UsersView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/search',
      name: 'search',
      component: () => import('../views/SearchView.vue'),
      meta: { requiresAuth: true },
    },
    {
      path: '/presets',
      name: 'presets',
      component: () => import('../views/PresetsView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some((record) => record.meta.requiresAdmin)

  // Check if user is authenticated and token is not expired
  if (requiresAuth) {
    if (!authStore.isAuthenticated) {
      next('/login')
      return
    }
    
    // Additional check for token expiration
    if (authStore.isTokenExpired()) {
      console.log('Token expired during navigation, logging out user')
      authStore.forceLogout()
      next('/login')
      return
    }
  }

  if (requiresAdmin && (!authStore.user || authStore.user.role !== 'admin')) {
    next('/')
    return
  }

  if (to.path === '/login' && authStore.isAuthenticated && !authStore.isTokenExpired()) {
    next('/')
    return
  }

  next()
})

export default router
