<script setup>
import { onMounted, onUnmounted } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

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
</template>

<style></style>
