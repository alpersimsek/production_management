<!--
GDPR Tool Login View - User Authentication Interface

This component provides the login interface for the GDPR compliance tool.
It handles user authentication with secure form validation and error handling.

Key Features:
- Secure Authentication: Username and password login with JWT tokens
- Form Validation: Required field validation and error display
- Error Handling: User-friendly error messages for various scenarios
- Loading States: Visual feedback during authentication process
- Responsive Design: Mobile-first responsive layout
- Accessibility: Proper ARIA labels and form structure
- Branding: GDPR-themed logo and consistent styling

Authentication Features:
- Username/Password: Standard credential authentication
- JWT Tokens: Secure token-based session management
- Error Mapping: Backend errors mapped to user-friendly messages
- Auto-redirect: Automatic redirect to dashboard on successful login
- Loading Indicators: Visual feedback during authentication

Security Features:
- Input Validation: Client-side validation for required fields
- Error Sanitization: Safe error message display
- Secure Routing: Protected route redirection
- Session Management: Automatic token handling

The component provides a secure and user-friendly authentication interface
for the GDPR compliance tool with proper error handling and accessibility.
-->

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
    class="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 via-gray-50 to-slate-100 py-8 sm:py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
    <!-- Background Pattern -->
    <div class="absolute inset-0 dot-pattern opacity-40"></div>
    
    <div
      class="w-full max-w-sm sm:max-w-md md:max-w-lg bg-white/90 backdrop-blur-sm rounded-2xl shadow-2xl p-8 sm:p-10 space-y-8 border border-slate-200/60 relative z-10 hover:shadow-3xl transition-all duration-300">
      <!-- Header with Logo and Branding -->
      <div class="flex flex-col items-center space-y-6">
        <div class="relative">
          <div class="absolute inset-0 bg-gradient-to-br from-gray-500 to-slate-600 rounded-2xl blur-lg opacity-20 scale-110"></div>
          <img :src="gdprLogo" alt="GDPR Processor Compliance"
            class="h-32 sm:h-36 md:h-40 w-auto transition-all duration-500 relative z-10" />
        </div>
        <div class="text-center space-y-2">
          <h1 class="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight">
            GDPR Processor
          </h1>
          <p class="text-sm sm:text-base text-slate-600 leading-relaxed">
            Securely access compliance dashboard
          </p>
        </div>
      </div>

      <!-- Form -->
      <form class="space-y-6" @submit.prevent="handleSubmit" aria-label="Sign in to GDPR Processor">
        <div class="space-y-5">
          <InputField id="username" v-model="username" label="Username" type="text" required :error="''"
            placeholder="Enter your username" aria-describedby="username-error" />

          <InputField id="password" v-model="password" label="Password" type="password" required :error="errorMessage"
            placeholder="Enter your password" aria-describedby="password-error" />
        </div>

        <AppButton type="submit" variant="primary" size="lg" :loading="isLoading" :disabled="isLoading"
          class="w-full bg-gradient-to-r from-gray-500 to-slate-600 hover:from-gray-600 hover:to-slate-700 hover:scale-105 hover:shadow-lg focus:ring-gray-400 text-white transition-all duration-300"
          aria-label="Sign in">
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
    <footer class="absolute bottom-4 left-0 right-0 text-center text-sm text-slate-500 px-4 sm:px-0 z-10">
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl px-4 py-2 inline-block border border-slate-200/60 shadow-lg">
        © {{ new Date().getFullYear() }} GDPR Processor. All rights reserved.
        <a href="/privacy" class="text-slate-600 hover:text-slate-800 ml-2 transition-colors duration-200 font-medium">Privacy Policy</a>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.dot-pattern {
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%239ca3af' fill-opacity='0.03'%3E%3Ccircle cx='30' cy='30' r='2'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}
</style>