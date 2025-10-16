<template>
  <div class="min-h-screen bg-gray-100">
    <!-- Main Navigation Bar -->
    <nav class="bg-primary-700 shadow-md">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex items-center justify-between h-16">
          <!-- Logo -->
          <div class="flex-shrink-0 text-white text-2xl font-bold">
            Olgahan ERP
          </div>

          <!-- User Info and Actions -->
          <div class="flex items-center space-x-4">
            <LanguageSwitcher />
            <NotificationDropdown />
            <span class="text-white text-sm">{{ authStore.user?.email }}</span>
            <span class="text-white text-xs bg-primary-600 px-2 py-1 rounded">{{ authStore.user?.role }}</span>
            <button
              @click="doLogout"
              class="bg-primary-600 hover:bg-primary-500 text-white px-3 py-2 rounded-md text-sm font-medium"
            >
              {{ $t('nav.logout') }}
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Tab Navigation -->
    <div class="bg-white shadow-sm border-b">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <nav class="flex space-x-8" aria-label="Tabs">
          <router-link
            v-for="module in availableModules"
            :key="module"
            :to="getModuleRoute(module)"
            :class="[
              'py-4 px-1 border-b-2 font-medium text-sm transition-colors',
              $route.path === getModuleRoute(module) || ($route.path === '/' && module === 'dashboard')
                ? 'border-primary-500 text-primary-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            ]"
          >
            {{ $t(`nav.${module}`) }}
          </router-link>
        </nav>
      </div>
    </div>

    <!-- Main Content -->
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useRBAC } from '@/composables/useRBAC'
import NotificationDropdown from '@/components/NotificationDropdown.vue'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const router = useRouter()
const authStore = useAuthStore()
const { getAvailableModules } = useRBAC()

const availableModules = getAvailableModules()

function getModuleRoute (module) {
  const routes = {
    dashboard: '/dashboard',
    orders: '/orders',
    customers: '/customers',
    products: '/products',
    production: '/production-jobs',
    packaging: '/packaging',
    warehouse: '/warehouses',
    shipments: '/shipments',
    analytics: '/analytics',
    settings: '/settings'
  }
  return routes[module] || '/'
}

async function doLogout () {
  await authStore.logout()
  router.push('/login')
}
</script>
