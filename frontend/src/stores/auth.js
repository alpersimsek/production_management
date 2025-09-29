/**
 * Authentication store for the GDPR tool frontend using Pinia
 * 
 * This store manages user authentication state, including login/logout functionality,
 * token management, and session persistence. It handles JWT token validation,
 * automatic logout on token expiration, and axios header configuration.
 * 
 * Key Features:
 * - User authentication state management (user, token, isAuthenticated)
 * - Session persistence using localStorage (cross-window/tab support)
 * - JWT token validation and expiration checking
 * - Automatic axios header configuration for API requests
 * - Force logout functionality for token expiration scenarios
 * - Login/logout actions with proper state updates
 * 
 * State:
 * - user: Current user object with username and role
 * - token: JWT access token for API authentication
 * - isAuthenticated: Boolean flag indicating authentication status
 * 
 * Actions:
 * - setAuth(): Initializes auth state from localStorage and configures axios
 * - login(username, password): Authenticates user and stores session data
 * - logout(): Clears session data and resets auth state
 * - forceLogout(): Enhanced logout for token expiration scenarios
 * - isTokenExpired(): Validates JWT token expiration using payload decoding
 * 
 * Getters:
 * - getUser: Returns current user object
 * - getToken: Returns current JWT token
 * 
 * Usage:
 * ```javascript
 * import { useAuthStore } from '@/stores/auth'
 * 
 * const authStore = useAuthStore()
 * 
 * // Login
 * await authStore.login(username, password)
 * 
 * // Check authentication
 * if (authStore.isAuthenticated) { ... }
 * 
 * // Logout
 * authStore.logout()
 * ```
 */

import { defineStore } from 'pinia'
import axios from 'axios'
import ApiService from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: null,
    isAuthenticated: false,
  }),

  getters: {
    getUser: (state) => state.user,
    getToken: (state) => state.token,
  },

  actions: {
    setAuth() {
      const token = localStorage.getItem('token')
      const user = localStorage.getItem('user')

      this.token = token
      this.user = user ? JSON.parse(user) : null
      this.isAuthenticated = !!token

      if (token) {
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      } else {
        delete axios.defaults.headers.common['Authorization']
      }
    },

    async login(username, password) {
      const data = await ApiService.login({ username, password })
      const user = {
        username,
        role: data.role,
      }
      localStorage.setItem('token', data.access_token)
      localStorage.setItem('user', JSON.stringify(user))
      this.setAuth()
    },

    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.setAuth()
    },

    // Enhanced logout for token expiration
    forceLogout() {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      this.token = null
      this.user = null
      this.isAuthenticated = false
      delete axios.defaults.headers.common['Authorization']
    },

    // Check if token is expired (if we have JWT decode capability)
    isTokenExpired() {
      if (!this.token) return true

      try {
        // Basic JWT expiration check (payload.exp)
        const payload = JSON.parse(atob(this.token.split('.')[1]))
        const currentTime = Math.floor(Date.now() / 1000)
        return payload.exp < currentTime
      } catch (error) {
        // If we can't decode, assume it's expired
        return true
      }
    },
  },
})
