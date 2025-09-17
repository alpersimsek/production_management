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
  <div class="min-h-screen bg-gradient-to-br from-slate-900 via-gray-900 to-slate-800 relative overflow-hidden">
    <!-- Animated Background -->
    <div class="absolute inset-0">
      <!-- Geometric Shapes -->
      <div class="absolute top-0 left-0 w-full h-full">
        <div class="absolute top-20 left-20 w-72 h-72 bg-gradient-to-br from-blue-500/10 to-purple-600/10 rounded-full blur-3xl animate-float"></div>
        <div class="absolute bottom-20 right-20 w-96 h-96 bg-gradient-to-br from-purple-500/10 to-pink-600/10 rounded-full blur-3xl animate-float-delayed"></div>
        <div class="absolute top-1/2 left-1/4 w-64 h-64 bg-gradient-to-br from-cyan-500/10 to-blue-600/10 rounded-full blur-3xl animate-float-slow"></div>
      </div>
      
      <!-- Grid Pattern -->
      <div class="absolute inset-0 grid-pattern opacity-20"></div>
      
      <!-- Floating Particles -->
      <div class="absolute inset-0">
        <div class="particle absolute top-1/4 left-1/4 w-2 h-2 bg-blue-400/30 rounded-full animate-pulse"></div>
        <div class="particle absolute top-3/4 right-1/4 w-1 h-1 bg-purple-400/40 rounded-full animate-pulse"></div>
        <div class="particle absolute top-1/2 left-3/4 w-1.5 h-1.5 bg-cyan-400/30 rounded-full animate-pulse"></div>
        <div class="particle absolute top-1/3 right-1/3 w-1 h-1 bg-pink-400/40 rounded-full animate-pulse"></div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="relative z-10 min-h-screen flex flex-col items-center justify-center px-4 sm:px-6 lg:px-8">
      <!-- Logo Section - Top -->
      <div class="flex justify-center mb-12">
        <div class="relative group">
          <!-- Logo Container -->
          <div class="relative bg-white/10 backdrop-blur-xl rounded-2xl p-6 border border-white/20 shadow-2xl group-hover:shadow-3xl transition-all duration-500">
            <img :src="gdprLogo" alt="GDPR Processor" class="h-16 sm:h-20 lg:h-24 w-auto mx-auto" />
          </div>
        </div>
      </div>

      <!-- Login Form -->
      <div class="w-full max-w-md">
        <!-- Login Card -->
        <div class="bg-white/10 backdrop-blur-xl rounded-3xl p-8 border border-white/20 shadow-2xl hover:shadow-3xl transition-all duration-500 group">
          <!-- Header -->
          <div class="text-center mb-8">
            <h2 class="text-3xl font-bold text-white mb-2">Welcome back</h2>
            <p class="text-gray-300">Sign in to continue</p>
          </div>

          <!-- Form -->
          <form class="space-y-6" @submit.prevent="handleSubmit" aria-label="Sign in">
            <div class="space-y-5">
              <div>
                <label for="username" class="block text-sm font-semibold text-white mb-2">Username</label>
                <div class="relative">
                  <input
                    id="username"
                    v-model="username"
                    type="text"
                    required
                    class="w-full px-4 py-4 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 backdrop-blur-sm"
                    placeholder="Enter your username"
                  />
                  <div class="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/20 to-purple-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                </div>
              </div>

              <div>
                <label for="password" class="block text-sm font-semibold text-white mb-2">Password</label>
                <div class="relative">
                  <input
                    id="password"
                    v-model="password"
                    type="password"
                    required
                    class="w-full px-4 py-4 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-300 backdrop-blur-sm"
                    placeholder="Enter your password"
                  />
                  <div class="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-500/20 to-pink-500/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                </div>
                <p v-if="errorMessage" class="mt-2 text-sm text-red-400 flex items-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ errorMessage }}
                </p>
              </div>
            </div>

            <button
              type="submit"
              :disabled="isLoading"
              class="w-full bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 hover:from-blue-700 hover:via-purple-700 hover:to-pink-700 text-white font-bold py-4 px-6 rounded-2xl transition-all duration-300 transform hover:scale-[1.02] hover:shadow-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden group"
            >
              <div class="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <span v-if="isLoading" class="relative flex items-center justify-center">
                <svg class="animate-spin h-5 w-5 mr-2 text-white" viewBox="0 0 24 24">
                  <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                  <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Signing in...
              </span>
              <span v-else class="relative">Sign in</span>
            </button>
          </form>

          <!-- Footer -->
          <div class="mt-8 pt-6 border-t border-white/20 text-center">
            <p class="text-sm text-gray-400">
              © {{ new Date().getFullYear() }} All rights reserved.
            </p>
            <a href="/privacy" class="text-blue-400 hover:text-blue-300 text-sm transition-colors duration-200 font-medium">
              Privacy Policy
            </a>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.grid-pattern {
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Ccircle cx='30' cy='30' r='1'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

@keyframes float {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(5deg); }
}

@keyframes float-delayed {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-30px) rotate(-5deg); }
}

@keyframes float-slow {
  0%, 100% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-15px) rotate(3deg); }
}

@keyframes gradient {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.animate-float {
  animation: float 6s ease-in-out infinite;
}

.animate-float-delayed {
  animation: float-delayed 8s ease-in-out infinite;
}

.animate-float-slow {
  animation: float-slow 10s ease-in-out infinite;
}

.animate-gradient {
  background-size: 200% 200%;
  animation: gradient 3s ease infinite;
}

.particle {
  animation-duration: 2s;
  animation-iteration-count: infinite;
  animation-timing-function: ease-in-out;
}

.particle:nth-child(1) { animation-delay: 0s; }
.particle:nth-child(2) { animation-delay: 0.5s; }
.particle:nth-child(3) { animation-delay: 1s; }
.particle:nth-child(4) { animation-delay: 1.5s; }
</style>