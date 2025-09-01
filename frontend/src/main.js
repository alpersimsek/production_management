import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import axios from 'axios'
import App from './App.vue'
import router from './router'

// Configure axios defaults
axios.defaults.baseURL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
axios.defaults.headers.common['Content-Type'] = 'application/json'

// Add response interceptor to handle expired tokens
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - clear auth and redirect to login
      // Clear session storage and redirect
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('user')
      
      // Show user-friendly message
      if (window.location.pathname !== '/login') {
        alert('Your session has expired. Please log in again.')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)
const pinia = createPinia()
app.use(pinia)
app.use(router)

app.mount('#app')
