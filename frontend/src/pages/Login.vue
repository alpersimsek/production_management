<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50 flex items-center justify-center py-4 px-4 sm:px-6 lg:px-8">
    <!-- Background Pattern -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute -top-20 -right-20 w-40 h-40 sm:w-60 sm:h-60 lg:w-80 lg:h-80 bg-primary-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob"></div>
      <div class="absolute -bottom-20 -left-20 w-40 h-40 sm:w-60 sm:h-60 lg:w-80 lg:h-80 bg-secondary-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000"></div>
      <div class="absolute top-20 left-20 w-40 h-40 sm:w-60 sm:h-60 lg:w-80 lg:h-80 bg-success-100 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000"></div>
    </div>

    <!-- Login Card -->
    <div class="relative w-full max-w-sm sm:max-w-md lg:max-w-lg space-y-6 sm:space-y-8">
      <!-- Logo Section -->
      <div class="text-center">
        <div class="mx-auto h-16 w-16 sm:h-20 sm:w-20 bg-gradient-to-r from-primary-600 to-primary-800 rounded-2xl flex items-center justify-center shadow-2xl transform rotate-3 hover:rotate-0 transition-transform duration-300">
          <svg class="h-8 w-8 sm:h-12 sm:w-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
          </svg>
        </div>
        <h2 class="mt-4 sm:mt-6 text-2xl sm:text-3xl lg:text-4xl font-bold text-secondary-900">
          DEMO ERP
        </h2>
        <p class="mt-2 text-sm sm:text-base lg:text-lg text-secondary-600">
          {{ $t('auth.welcome_message') }}
        </p>
      </div>

      <!-- Login Form -->
      <div class="bg-white/80 backdrop-blur-sm rounded-2xl sm:rounded-3xl shadow-2xl border border-white/20 p-4 sm:p-6 lg:p-8 space-y-4 sm:space-y-6">
        <!-- Form Header -->
        <div class="text-center">
          <h3 class="text-xl sm:text-2xl font-bold text-secondary-900 mb-2">
            {{ $t('auth.login') }}
          </h3>
          <p class="text-sm sm:text-base text-secondary-600">
            {{ $t('auth.login_subtitle') }}
          </p>
        </div>

        <!-- Login Form -->
        <form class="space-y-4 sm:space-y-6" @submit.prevent="handleLogin">
          <!-- Email Field -->
          <div class="space-y-2">
            <label for="email" class="block text-sm font-semibold text-secondary-700">
              {{ $t('auth.email') }}
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 12a4 4 0 10-8 0 4 4 0 008 0zm0 0v1.5a2.5 2.5 0 005 0V12a9 9 0 10-9 9m4.5-1.206a8.959 8.959 0 01-4.5 1.207" />
                </svg>
              </div>
              <input
                id="email"
                v-model="form.email"
                type="email"
                :class="emailClasses"
                :placeholder="$t('auth.email_placeholder')"
                required
                @blur="validateEmail"
                @input="clearError('email')"
              />
            </div>
            <p v-if="errors.email" class="text-sm text-error-600 flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ errors.email }}
            </p>
          </div>

          <!-- Password Field -->
          <div class="space-y-2">
            <label for="password" class="block text-sm font-semibold text-secondary-700">
              {{ $t('auth.password') }}
            </label>
            <div class="relative">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg class="h-5 w-5 text-secondary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <input
                id="password"
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                :class="passwordClasses"
                :placeholder="$t('auth.password_placeholder')"
                required
                @blur="validatePassword"
                @input="clearError('password')"
              />
              <button
                type="button"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
                @click="togglePassword"
              >
                <svg v-if="showPassword" class="h-5 w-5 text-secondary-400 hover:text-secondary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
                <svg v-else class="h-5 w-5 text-secondary-400 hover:text-secondary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
            </div>
            <p v-if="errors.password" class="text-sm text-error-600 flex items-center">
              <svg class="w-4 h-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              {{ errors.password }}
            </p>
          </div>

          <!-- Remember Me & Forgot Password -->
          <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-2 sm:space-y-0">
            <div class="flex items-center">
              <input
                id="remember-me"
                v-model="form.rememberMe"
                type="checkbox"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-secondary-300 rounded"
              />
              <label for="remember-me" class="ml-2 block text-sm text-secondary-700">
                {{ $t('auth.remember_me') }}
              </label>
            </div>
            <div class="text-sm">
              <a href="#" class="font-medium text-primary-600 hover:text-primary-500 transition-colors duration-200">
                {{ $t('auth.forgot_password') }}
              </a>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="loginError" class="bg-error-50 border border-error-200 rounded-lg p-4">
            <div class="flex">
              <svg class="h-5 w-5 text-error-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="ml-3">
                <p class="text-sm text-error-800">{{ loginError }}</p>
              </div>
            </div>
          </div>

          <!-- Login Button -->
          <button
            type="submit"
            :disabled="isLoading || !isFormValid"
            :class="loginButtonClasses"
            class="group relative w-full flex justify-center py-3 sm:py-4 px-4 border border-transparent text-sm sm:text-base font-medium rounded-xl text-white focus:outline-none focus:ring-2 focus:ring-offset-2 transition-all duration-200"
          >
            <span class="absolute left-0 inset-y-0 flex items-center pl-3">
              <svg v-if="!isLoading" class="h-5 w-5 text-primary-500 group-hover:text-primary-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
              </svg>
              <svg v-else class="animate-spin h-5 w-5 text-primary-500" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </span>
            {{ isLoading ? $t('auth.logging_in') : $t('auth.login_button') }}
          </button>
        </form>

        <!-- Demo Users Section -->
        <div class="mt-8">
          <h3 class="text-lg font-semibold text-secondary-700 mb-4 text-center">
            {{ $t('auth.demo_users') }}
          </h3>
          <div class="grid grid-cols-1 gap-3">
            <!-- Admin User -->
            <div
              @click="fillCredentials('ahmet@olgahan.com', 'admin123')"
              class="p-3 bg-gradient-to-r from-primary-50 to-primary-100 rounded-lg border border-primary-200 cursor-pointer hover:from-primary-100 hover:to-primary-200 transition-all duration-200 hover:shadow-md group"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                    <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-secondary-900 group-hover:text-primary-700">Ahmet Yılmaz (Admin)</p>
                    <p class="text-sm text-secondary-600">ahmet@olgahan.com</p>
                  </div>
                </div>
                <div class="text-xs text-secondary-500 group-hover:text-primary-600">
                  {{ $t('auth.click_to_fill') }}
                </div>
              </div>
            </div>

            <!-- Manager User -->
            <div
              @click="fillCredentials('fatma@olgahan.com', 'manager123')"
              class="p-3 bg-gradient-to-r from-secondary-50 to-secondary-100 rounded-lg border border-secondary-200 cursor-pointer hover:from-secondary-100 hover:to-secondary-200 transition-all duration-200 hover:shadow-md group"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-secondary-600 rounded-full flex items-center justify-center">
                    <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-secondary-900 group-hover:text-secondary-700">Fatma Özkan (Manager)</p>
                    <p class="text-sm text-secondary-600">fatma@olgahan.com</p>
                  </div>
                </div>
                <div class="text-xs text-secondary-500 group-hover:text-secondary-600">
                  {{ $t('auth.click_to_fill') }}
                </div>
              </div>
            </div>

            <!-- Operator User -->
            <div
              @click="fillCredentials('mehmet@olgahan.com', 'operator123')"
              class="p-3 bg-gradient-to-r from-success-50 to-success-100 rounded-lg border border-success-200 cursor-pointer hover:from-success-100 hover:to-success-200 transition-all duration-200 hover:shadow-md group"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-3">
                  <div class="w-8 h-8 bg-success-600 rounded-full flex items-center justify-center">
                    <svg class="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                  <div>
                    <p class="font-medium text-secondary-900 group-hover:text-success-700">Mehmet Kaya (Operator)</p>
                    <p class="text-sm text-secondary-600">mehmet@olgahan.com</p>
                  </div>
                </div>
                <div class="text-xs text-secondary-500 group-hover:text-success-600">
                  {{ $t('auth.click_to_fill') }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Language Switcher -->
        <div class="flex justify-center pt-4 border-t border-secondary-200">
          <LanguageSwitcher />
        </div>
      </div>

            <!-- Footer -->
            <div class="text-center">
              <p class="text-sm text-secondary-500">
                © {{ currentYear }} DEMO ERP. All rights reserved.
              </p>
            </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/store/auth'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

// Form data
const form = reactive({
  email: '',
  password: '',
  rememberMe: false
})

// State
const isLoading = ref(false)
const showPassword = ref(false)
const loginError = ref('')

// Validation errors
const errors = reactive({
  email: '',
  password: ''
})

// Computed properties
const currentYear = computed(() => new Date().getFullYear())

// Computed properties
const emailClasses = computed(() => {
  const baseClasses = 'appearance-none rounded-xl relative block w-full pl-10 pr-3 py-3 border placeholder-secondary-400 text-secondary-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm transition-all duration-200'
  return errors.email
    ? `${baseClasses} border-error-300 bg-error-50`
    : `${baseClasses} border-secondary-300 bg-white/50 backdrop-blur-sm`
})

const passwordClasses = computed(() => {
  const baseClasses = 'appearance-none rounded-xl relative block w-full pl-10 pr-10 py-3 border placeholder-secondary-400 text-secondary-900 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 focus:z-10 sm:text-sm transition-all duration-200'
  return errors.password
    ? `${baseClasses} border-error-300 bg-error-50`
    : `${baseClasses} border-secondary-300 bg-white/50 backdrop-blur-sm`
})

const loginButtonClasses = computed(() => {
  if (isLoading.value || !isFormValid.value) {
    return 'bg-secondary-300 cursor-not-allowed'
  }
  return 'bg-gradient-to-r from-primary-600 to-primary-700 hover:from-primary-700 hover:to-primary-800 focus:ring-primary-500 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5'
})

const isFormValid = computed(() => {
  return form.email && form.password && !errors.email && !errors.password
})

// Methods
const validateEmail = () => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!form.email) {
    errors.email = t('auth.email_required')
  } else if (!emailRegex.test(form.email)) {
    errors.email = t('auth.email_invalid')
  } else {
    errors.email = ''
  }
}

const validatePassword = () => {
  if (!form.password) {
    errors.password = t('auth.password_required')
  } else if (form.password.length < 6) {
    errors.password = t('auth.password_min_length')
  } else {
    errors.password = ''
  }
}

const clearError = (field) => {
  errors[field] = ''
  loginError.value = ''
}

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

const handleLogin = async () => {
  // Validate form
  validateEmail()
  validatePassword()

  if (!isFormValid.value) {
    return
  }

  isLoading.value = true
  loginError.value = ''

  try {
    // Use real backend authentication
    const success = await authStore.login(form.email, form.password)

    if (success) {
      // Redirect to dashboard
      router.push('/')
    } else {
      loginError.value = t('auth.invalid_credentials')
    }
  } catch (error) {
    loginError.value = t('auth.login_error')
    console.error('Login error:', error)
  } finally {
    isLoading.value = false
  }
}

const fillCredentials = (email, password) => {
  form.email = email
  form.password = password
  form.rememberMe = true

  // Clear any existing errors
  errors.email = ''
  errors.password = ''
  loginError.value = ''

  // Validate the filled form
  validateEmail()
  validatePassword()
}
</script>

<style scoped>
@keyframes blob {
  0% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
  100% {
    transform: translate(0px, 0px) scale(1);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
}
</style>
