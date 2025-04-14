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
  },
})
