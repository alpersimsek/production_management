/**
 * Main application entry point for the GDPR tool frontend
 * 
 * This file serves as the bootstrap for the Vue.js application, configuring
 * the core dependencies, global settings, and application initialization.
 * It sets up the Vue app instance, state management, routing, and HTTP client
 * with proper error handling and authentication interceptors.
 * 
 * Key Features:
 * - Vue 3 application initialization with Composition API
 * - Pinia state management setup
 * - Vue Router configuration
 * - Axios HTTP client configuration with base URL and headers
 * - Global response interceptor for handling authentication errors
 * - Automatic session cleanup on token expiration
 * - User-friendly error messaging for expired sessions
 * 
 * Configuration:
 * - Base API URL from environment variables (VITE_API_URL) or localhost fallback
 * - Default Content-Type header for JSON requests
 * - Response interceptor for 401 (Unauthorized) error handling
 * - Automatic redirection to login page on session expiration
 * 
 * Dependencies:
 * - Vue 3: Core framework
 * - Pinia: State management
 * - Vue Router: Client-side routing
 * - Axios: HTTP client for API communication
 * - App.vue: Root component
 * - main.css: Global styles
 * 
 * Error Handling:
 * - 401 responses trigger automatic logout and redirect
 * - Session storage cleanup on authentication failure
 * - User notification for expired sessions
 * - Graceful handling of navigation during logout
 * 
 * Environment Variables:
 * - VITE_API_URL: Backend API base URL (defaults to http://localhost:8000/api/v1)
 */

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
