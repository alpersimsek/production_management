<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import InputField from '../components/InputField.vue'
import AppButton from '../components/AppButton.vue'
import gdprLogo from '../assets/ribbon-logo.svg' // GDPR-themed image

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  try {
    error.value = ''
    isLoading.value = true
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}

// Map backend errors to user-friendly messages
const errorMessage = computed(() => {
  if (!error.value) return ''
  switch (error.value.toLowerCase()) {
    case 'unauthorized':
    case 'invalid credentials':
      return 'Invalid username or password'
    case 'network error':
      return 'Unable to connect. Please check your network.'
    default:
      return 'An error occurred. Please try again.'
  }
})
</script>

<template>
  <div
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-100 via-white to-gray-50 py-8 sm:py-12 px-4 sm:px-6 lg:px-8">
    <div
      class="w-full max-w-sm sm:max-w-md md:max-w-lg bg-white/95 rounded-xl shadow-lg p-8 sm:p-10 space-y-8 backdrop-blur-sm border border-gray-200">
      <!-- Header with Logo and Branding -->
      <div class="flex flex-col items-center space-y-4">
        <img :src="gdprLogo" alt="GDPR Processor Compliance"
          class="h-32 sm:h-36 md:h-40 w-auto transition-transform duration-300 hover:scale-105" />
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 tracking-tight">
          GDPR Processor
        </h1>
        <p class="text-sm sm:text-base text-gray-600 text-center leading-relaxed">
          Securely access compliance dashboard
        </p>
      </div>

      <!-- Form -->
      <form class="space-y-6" @submit.prevent="handleSubmit" aria-label="Sign in to GDPR Processor">
        <InputField id="username" v-model="username" label="Username" type="text" required :error="''"
          class="text-base transition-all duration-200 focus:ring-primary focus:border-primary"
          placeholder="Enter your username" aria-describedby="username-error" />

        <InputField id="password" v-model="password" label="Password" type="password" required :error="errorMessage"
          class="text-base transition-all duration-200 focus:ring-primary focus:border-primary"
          placeholder="Enter your password" aria-describedby="password-error" />

        <AppButton type="submit" variant="primary" size="lg" :loading="isLoading" :disabled="isLoading"
          class="w-full bg-primary hover:bg-primary-hover focus:ring-primary text-white" aria-label="Sign in">
          <span v-if="isLoading" class="flex items-center justify-center">
            <svg class="animate-spin h-5 w-5 mr-2 text-white" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            Signing in...
          </span>
          <span v-else>Sign in</span>
        </AppButton>
      </form>
    </div>

    <!-- Footer Branding -->
    <footer class="absolute bottom-4 text-center text-sm text-gray-500 px-4 sm:px-0">
      © {{ new Date().getFullYear() }} GDPR Processor. All rights reserved.
      <a href="/privacy" class="text-primary hover:text-primary-hover ml-2 transition-colors duration-200">Privacy
        Policy</a>
    </footer>
  </div>
</template>