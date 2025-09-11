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
import { onMounted, onUnmounted, ref } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import { globalErrorHandler } from './composables/useErrorHandler'
import { globalNotifications } from './composables/useNotifications'
import ErrorModal from './components/ErrorModal.vue'
import SessionExpiredModal from './components/SessionExpiredModal.vue'
import NotificationContainer from './components/NotificationContainer.vue'

const authStore = useAuthStore()
const router = useRouter()
const { error, showErrorModal, handleRetry, handleDismiss, handleCancel } = globalErrorHandler
const { showLoginExpired } = globalNotifications

const showSessionExpiredModal = ref(false)

let tokenCheckInterval = null

onMounted(() => {
  authStore.setAuth()
  
  // Check token expiration every minute
  tokenCheckInterval = setInterval(() => {
    if (authStore.isAuthenticated && authStore.isTokenExpired()) {
      console.log('Token expired, logging out user')
      // Show styled session expired modal instead of basic alert
      showSessionExpiredModal.value = true
    }
  }, 60000) // Check every minute
})

onUnmounted(() => {
  if (tokenCheckInterval) {
    clearInterval(tokenCheckInterval)
  }
})

const handleSessionExpiredLogin = () => {
  authStore.forceLogout()
  router.push('/login')
  showSessionExpiredModal.value = false
}

const handleSessionExpiredClose = () => {
  showSessionExpiredModal.value = false
  // Force logout since user cannot communicate with backend
  authStore.forceLogout()
  router.push('/login')
}
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

  <!-- Session Expired Modal -->
  <SessionExpiredModal
    :open="showSessionExpiredModal"
    @close="handleSessionExpiredClose"
    @login="handleSessionExpiredLogin"
  />

  <!-- Notification Container -->
  <NotificationContainer />
</template>

<style></style>
