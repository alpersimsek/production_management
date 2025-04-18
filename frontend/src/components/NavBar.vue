<template>
  <nav class="bg-white shadow">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 justify-between">
        <!-- Logo and brand -->
        <div class="flex">
          <div class="flex flex-shrink-0 items-center">
            <router-link to="/" class="flex items-center">
              <!-- App logo -->
              <div class="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center">
                <span class="text-white font-bold">G</span>
              </div>
              <span class="ml-2 text-lg font-semibold text-gray-900">GDPR Tool</span>
            </router-link>
          </div>
        </div>

        <!-- Main navigation - Desktop -->
        <div class="hidden sm:ml-6 sm:flex sm:items-center">
          <div class="flex space-x-4">
            <router-link
              v-for="item in navigationItems"
              :key="item.name"
              :to="item.href"
              :class="[
                isActive(item.href)
                  ? 'bg-indigo-50 text-indigo-700'
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
                'px-3 py-2 rounded-md text-sm font-medium'
              ]"
              v-show="shouldShowItem(item)"
            >
              {{ item.name }}
            </router-link>
          </div>
        </div>

        <!-- User dropdown menu -->
        <div class="hidden sm:ml-6 sm:flex sm:items-center">
          <div class="relative ml-3">
            <div>
              <button
                @click="toggleUserMenu"
                type="button"
                class="flex rounded-full bg-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                id="user-menu-button"
                aria-expanded="false"
                aria-haspopup="true"
              >
                <span class="sr-only">Open user menu</span>
                <div class="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-800">
                  {{ userInitials }}
                </div>
              </button>
            </div>

            <!-- Dropdown menu -->
            <div
              v-if="showUserMenu"
              class="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-white py-1 shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none"
              role="menu"
              aria-orientation="vertical"
              aria-labelledby="user-menu-button"
            >
              <div class="px-4 py-2 text-sm text-gray-500 border-b">
                Signed in as <span class="font-semibold">{{ username }}</span>
              </div>
              <!-- <router-link
                to="/profile"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                role="menuitem"
              >
                Your Profile
              </router-link> -->
              <button
                type="button"
                @click="handleLogout"
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                role="menuitem"
              >
                Sign out
              </button>
            </div>
          </div>
        </div>

        <!-- Mobile menu button -->
        <div class="-mr-2 flex items-center sm:hidden">
          <button
            @click="toggleMobileMenu"
            type="button"
            class="inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-gray-100 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500"
            aria-controls="mobile-menu"
            :aria-expanded="showMobileMenu"
          >
            <span class="sr-only">Open main menu</span>
            <!-- Icon when menu is closed -->
            <Bars3Icon v-if="!showMobileMenu" class="h-6 w-6" aria-hidden="true" />
            <!-- Icon when menu is open -->
            <XMarkIcon v-else class="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu, show/hide based on menu state -->
    <div
      v-if="showMobileMenu"
      class="sm:hidden"
      id="mobile-menu"
    >
      <div class="space-y-1 pt-2 pb-3">
        <router-link
          v-for="item in navigationItems"
          :key="item.name"
          :to="item.href"
          :class="[
            isActive(item.href)
              ? 'bg-indigo-50 text-indigo-700'
              : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900',
            'block px-3 py-2 rounded-md text-base font-medium'
          ]"
          v-show="shouldShowItem(item)"
        >
          {{ item.name }}
        </router-link>
      </div>
      <div class="border-t border-gray-200 pt-4 pb-3">
        <div class="flex items-center px-4">
          <div class="flex-shrink-0">
            <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-800">
              {{ userInitials }}
            </div>
          </div>
          <div class="ml-3">
            <div class="text-base font-medium text-gray-800">{{ username }}</div>
            <div class="text-sm font-medium text-gray-500">{{ userRole }}</div>
          </div>
        </div>
        <div class="mt-3 space-y-1">
          <router-link
            to="/profile"
            class="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-800"
          >
            Your Profile
          </router-link>
          <button
            type="button"
            @click="handleLogout"
            class="block w-full text-left px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-100 hover:text-gray-800"
          >
            Sign out
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import {
  Bars3Icon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Navigation state
const showMobileMenu = ref(false)
const showUserMenu = ref(false)

// Navigation items
const navigationItems = [
  { name: 'Dashboard', href: '/dashboard', requiresAuth: true },
  { name: 'Files', href: '/files', requiresAuth: true },
  { name: 'Search', href: '/search', requiresAuth: true },
  { name: 'Users', href: '/users', requiresAuth: true, requiresAdmin: true },
  { name: 'Presets', href: '/presets', requiresAuth: true, requiresAdmin: true },
]

// User information
const username = computed(() => authStore.user?.username || 'User')
const userRole = computed(() => authStore.user?.role || 'user')
const userInitials = computed(() => {
  const name = username.value
  return name.charAt(0).toUpperCase()
})

// Check if a path is the active route
const isActive = (path) => {
  // For exact matches
  if (route.path === path) return true

  // For nested routes
  return route.path.startsWith(path) && path !== '/'
}

// Check if a navigation item should be shown based on user permissions
const shouldShowItem = (item) => {
  if (item.requiresAuth && !authStore.isAuthenticated) return false
  if (item.requiresAdmin && (!authStore.user || authStore.user.role !== 'admin')) return false
  return true
}

// Toggle mobile menu
const toggleMobileMenu = () => {
  showMobileMenu.value = !showMobileMenu.value
  // Close user menu when opening mobile menu
  if (showMobileMenu.value) {
    showUserMenu.value = false
  }
}

// Toggle user menu
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

// Handle logout
const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>
