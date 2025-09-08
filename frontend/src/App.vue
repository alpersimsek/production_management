<!--
GDPR Tool Application - Root Component

This is the root Vue component for the GDPR compliance tool frontend application.
It provides the main application structure with authentication management and routing.

Key Features:
- Authentication Management: Handles user authentication state and token validation
- Token Expiration Monitoring: Periodic checks for token expiration with automatic logout
- Router Integration: Provides the main routing outlet for the application
- Session Management: Automatic session cleanup and user redirection

Authentication Features:
- Token Validation: Checks JWT token expiration every minute
- Automatic Logout: Logs out users when tokens expire
- User Notifications: Shows alert messages for expired sessions
- Route Protection: Redirects to login page on authentication failure

The component serves as the entry point for the Vue application and manages
global authentication state and routing for the GDPR compliance tool.
-->

<script setup>
import { onMounted, onUnmounted, computed } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import { globalErrorHandler } from './composables/useErrorHandler'
import ErrorModal from './components/ErrorModal.vue'

const authStore = useAuthStore()
const router = useRouter()
const { error, showErrorModal, handleRetry, handleDismiss, handleCancel } = globalErrorHandler

let tokenCheckInterval = null

onMounted(() => {
  authStore.setAuth()
  
  // Check token expiration every minute
  tokenCheckInterval = setInterval(() => {
    if (authStore.isAuthenticated && authStore.isTokenExpired()) {
      console.log('Token expired, logging out user')
      // Show user-friendly message
      alert('Your session has expired. Please log in again.')
      authStore.forceLogout()
      router.push('/login')
    }
  }, 60000) // Check every minute
})

onUnmounted(() => {
  if (tokenCheckInterval) {
    clearInterval(tokenCheckInterval)
  }
})
</script>

<template>
  <RouterView />
  
  <!-- Global Error Modal -->
  <ErrorModal 
    :open="showErrorModal" 
    :error="error"
    :show-retry="!!error.retryAction"
    :retry-action="error.retryAction"
    :show-cancel="!!error.cancelAction"
    :cancel-action="error.cancelAction"
    @close="globalErrorHandler.clearError"
    @retry="handleRetry"
    @dismiss="handleDismiss"
    @cancel="handleCancel"
  />
</template>

<style></style>
