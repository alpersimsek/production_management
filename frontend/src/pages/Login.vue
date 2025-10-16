<template>
  <div class="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
    <div class="sm:mx-auto sm:w-full sm:max-w-md">
      <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
        Olgahan Kimya ERP
      </h2>
      <p class="mt-2 text-center text-sm text-gray-600">
        {{ $t('auth.login') }}
      </p>
    </div>

    <div class="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
      <div class="card py-8 px-4 shadow sm:rounded-lg sm:px-10">
        <form @submit.prevent="doLogin" class="space-y-6">
          <div>
            <label for="email" class="block text-sm font-medium text-gray-700">
              {{ $t('auth.email') }}
            </label>
            <div class="mt-1">
              <input
                id="email"
                v-model="email"
                name="email"
                type="email"
                autocomplete="email"
                required
                class="input-field"
                placeholder="Enter your email"
              />
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700">
              {{ $t('auth.password') }}
            </label>
            <div class="mt-1">
              <input
                id="password"
                v-model="password"
                name="password"
                type="password"
                autocomplete="current-password"
                required
                class="input-field"
                placeholder="Enter your password"
              />
            </div>
          </div>

          <div v-if="authStore.error" class="rounded-md bg-red-50 p-4">
            <div class="flex">
              <div class="flex-shrink-0">
                <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                </svg>
              </div>
              <div class="ml-3">
                <p class="text-sm text-red-800">{{ authStore.error }}</p>
              </div>
              <div class="ml-auto pl-3">
                <div class="-mx-1.5 -my-1.5">
                  <button
                    type="button"
                    @click="authStore.error = null"
                    class="inline-flex bg-red-50 rounded-md p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-red-50 focus:ring-red-600"
                  >
                    <span class="sr-only">Dismiss</span>
                    <svg class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div>
            <button
              type="submit"
              :disabled="authStore.loading || !email || !password"
              class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <svg v-if="authStore.loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              {{ authStore.loading ? $t('common.loading') : $t('auth.login_button') }}
            </button>
          </div>
        </form>
      </div>

      <!-- Demo Users -->
      <div class="mt-6 card p-4">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Demo Users - Click to Auto-Fill</h3>
        <div class="space-y-3">
          <!-- Admin Users -->
          <div class="border-l-4 border-red-500 pl-3">
            <h4 class="text-sm font-semibold text-red-700 mb-2">Admin Users</h4>
            <div class="grid grid-cols-1 gap-2">
              <button
                @click="selectUser('ahmet@olgahan.com', 'admin123')"
                class="flex items-center justify-between p-2 text-left bg-red-50 hover:bg-red-100 rounded-md transition-colors"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">Ahmet Yılmaz</div>
                  <div class="text-xs text-gray-600">ahmet@olgahan.com • Admin • Üretim</div>
                </div>
                <div class="text-xs text-red-600 font-medium">Select</div>
              </button>
            </div>
          </div>

          <!-- Manager Users -->
          <div class="border-l-4 border-blue-500 pl-3">
            <h4 class="text-sm font-semibold text-blue-700 mb-2">Manager Users</h4>
            <div class="grid grid-cols-1 gap-2">
              <button
                @click="selectUser('fatma@olgahan.com', 'manager123')"
                class="flex items-center justify-between p-2 text-left bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">Fatma Özkan</div>
                  <div class="text-xs text-gray-600">fatma@olgahan.com • Manager • Üretim</div>
                </div>
                <div class="text-xs text-blue-600 font-medium">Select</div>
              </button>
              <button
                @click="selectUser('elif@olgahan.com', 'manager123')"
                class="flex items-center justify-between p-2 text-left bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">Elif Korkmaz</div>
                  <div class="text-xs text-gray-600">elif@olgahan.com • Manager • Paketleme</div>
                </div>
                <div class="text-xs text-blue-600 font-medium">Select</div>
              </button>
              <button
                @click="selectUser('selin@olgahan.com', 'manager123')"
                class="flex items-center justify-between p-2 text-left bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">Selin Aktaş</div>
                  <div class="text-xs text-gray-600">selin@olgahan.com • Manager • Sevkiyat</div>
                </div>
                <div class="text-xs text-blue-600 font-medium">Select</div>
              </button>
              <button
                @click="selectUser('gulay@olgahan.com', 'manager123')"
                class="flex items-center justify-between p-2 text-left bg-blue-50 hover:bg-blue-100 rounded-md transition-colors"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">Gülay Yılmaz</div>
                  <div class="text-xs text-gray-600">gulay@olgahan.com • Manager • Plasiyer</div>
                </div>
                <div class="text-xs text-blue-600 font-medium">Select</div>
              </button>
            </div>
          </div>

          <!-- Operator Users -->
          <div class="border-l-4 border-green-500 pl-3">
            <h4 class="text-sm font-semibold text-green-700 mb-2">Operator Users</h4>
            <div class="grid grid-cols-1 gap-2">
              <button
                @click="selectUser('mehmet@olgahan.com', 'operator123')"
                class="flex items-center justify-between p-2 text-left bg-green-50 hover:bg-green-100 rounded-md transition-colors"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">Mehmet Kaya</div>
                  <div class="text-xs text-gray-600">mehmet@olgahan.com • Operator • Paketleme</div>
                </div>
                <div class="text-xs text-green-600 font-medium">Select</div>
              </button>
              <button
                @click="selectUser('ali@olgahan.com', 'operator123')"
                class="flex items-center justify-between p-2 text-left bg-green-50 hover:bg-green-100 rounded-md transition-colors"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">Ali Çelik</div>
                  <div class="text-xs text-gray-600">ali@olgahan.com • Operator • Üretim</div>
                </div>
                <div class="text-xs text-green-600 font-medium">Select</div>
              </button>
              <button
                @click="selectUser('zeynep@olgahan.com', 'operator123')"
                class="flex items-center justify-between p-2 text-left bg-green-50 hover:bg-green-100 rounded-md transition-colors"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">Zeynep Arslan</div>
                  <div class="text-xs text-gray-600">zeynep@olgahan.com • Operator • Depo</div>
                </div>
                <div class="text-xs text-green-600 font-medium">Select</div>
              </button>
              <button
                @click="selectUser('mustafa@olgahan.com', 'operator123')"
                class="flex items-center justify-between p-2 text-left bg-green-50 hover:bg-green-100 rounded-md transition-colors"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">Mustafa Yıldız</div>
                  <div class="text-xs text-gray-600">mustafa@olgahan.com • Operator • Sevkiyat</div>
                </div>
                <div class="text-xs text-green-600 font-medium">Select</div>
              </button>
              <button
                @click="selectUser('burak@olgahan.com', 'operator123')"
                class="flex items-center justify-between p-2 text-left bg-green-50 hover:bg-green-100 rounded-md transition-colors"
              >
                <div>
                  <div class="text-sm font-medium text-gray-900">Burak Şahin</div>
                  <div class="text-xs text-gray-600">burak@olgahan.com • Operator • Üretim</div>
                </div>
                <div class="text-xs text-green-600 font-medium">Select</div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

const email = ref('')
const password = ref('')

function selectUser (userEmail, userPassword) {
  email.value = userEmail
  password.value = userPassword
}

async function doLogin () {
  const success = await authStore.login(email.value, password.value)
  if (success) {
    // Check if there's a redirect query parameter, otherwise go to dashboard
    const redirect = router.currentRoute.value.query.redirect || '/dashboard'
    router.push(redirect)
  }
}
</script>
