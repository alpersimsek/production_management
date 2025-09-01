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
      const token = sessionStorage.getItem('token')
      const user = sessionStorage.getItem('user')

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
      sessionStorage.setItem('token', data.access_token)
      sessionStorage.setItem('user', JSON.stringify(user))
      this.setAuth()
    },

    logout() {
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('user')
      this.setAuth()
    },

    // Enhanced logout for token expiration
    forceLogout() {
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('user')
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
