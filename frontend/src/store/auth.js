import { defineStore } from 'pinia'
import { jwtDecode } from 'jwt-decode'
import { authAPI } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    tokens: null,
    loading: false,
    error: null
  }),
  getters: {
    isAuthenticated: (s) => !!(s.tokens && s.tokens.access_token)
  },
  actions: {
    async login (email, password) {
      this.loading = true
      this.error = null

      try {
        const tokens = await authAPI.login(email, password)
        this.tokens = tokens

        // Store tokens in localStorage
        localStorage.setItem('access_token', tokens.access_token)
        localStorage.setItem('refresh_token', tokens.refresh_token)

        // Decode token to get user info
        const payload = jwtDecode(tokens.access_token)
        this.user = {
          id: payload.sub,
          email: payload.email,
          role: payload.role
        }

        return true
      } catch (error) {
        this.error = error.response?.data?.detail || 'Login failed'
        return false
      } finally {
        this.loading = false
      }
    },

    async logout () {
      try {
        await authAPI.logout()
      } catch (error) {
        console.error('Logout error:', error)
      } finally {
        this.tokens = null
        this.user = null
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
      }
    },

    async getCurrentUser () {
      try {
        const user = await authAPI.getCurrentUser()
        this.user = user
        return user
      } catch (error) {
        console.error('Get current user error:', error)
        this.logout()
        return null
      }
    },

    async initializeAuth () {
      const token = localStorage.getItem('access_token')
      if (token) {
        try {
          const payload = jwtDecode(token)
          this.user = {
            id: payload.sub,
            email: payload.email,
            role: payload.role
          }
          this.tokens = { access_token: token }

          // Verify token is still valid by getting current user
          await this.getCurrentUser()
        } catch (error) {
          console.error('Token validation error:', error)
          this.logout()
        }
      }
    }
  }
})
