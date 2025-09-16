<!--
GDPR Tool Navigation Bar - Main Navigation Component

This component provides the main navigation bar for the GDPR compliance tool application.
It includes responsive navigation, user authentication, role-based menu items, and mobile support.

Key Features:
- Responsive Design: Desktop and mobile navigation with hamburger menu
- Role-Based Access: Shows different menu items based on user role (admin/user)
- User Authentication: Displays user information and logout functionality
- Active Route Highlighting: Highlights the current page in navigation
- Logo Integration: Custom logo with fallback support
- Mobile Menu: Collapsible mobile navigation with smooth animations

Navigation Items:
- Dashboard: Main dashboard for all authenticated users
- Files: File management and processing for all users
- Search: Data masking search for all users
- Users: User management (admin only)
- Presets: Preset configuration (admin only)

User Features:
- User Dropdown: Shows username, role, and logout option
- User Initials: Displays user initials in avatar
- Logout Functionality: Secure logout with route redirection
- Mobile User Info: User information display in mobile menu

The component provides comprehensive navigation functionality with proper
authentication and authorization for the GDPR compliance tool.
-->

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { Bars3Icon, XMarkIcon } from '@heroicons/vue/24/outline'
import logo from '../assets/ribbon-logo.svg' // Import the SVG logo

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Navigation state
const showMobileMenu = ref(false)
const showUserMenu = ref(false)
const useFallbackLogo = ref(false) // For fallback logo

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
  if (route.path === path) return true
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

<template>
  <nav class="bg-gray-100/80 backdrop-blur-sm border-b border-gray-200/60 sticky top-0 z-50">
    <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
      <div class="flex h-16 justify-between items-center">
        <!-- Logo and brand -->
        <div class="flex items-center">
          <router-link to="/" class="flex items-center space-x-3">
            <!-- Custom Logo -->
            <img :src="logo" alt="GDPR Processor Logo"
              class="h-16 w-auto transition-transform duration-200 hover:scale-105" @error="useFallbackLogo = true"
              v-if="!useFallbackLogo" />
            <!-- Fallback Logo -->
            <div v-else class="h-14 w-10 rounded-full bg-indigo-600 flex items-center justify-center">
              <span class="text-white font-bold">G</span>
            </div>
            <span class="text-lg font-bold text-gray-900 tracking-tight">GDPR Processor</span>
          </router-link>
        </div>

        <!-- Main navigation - Desktop -->
        <div class="hidden sm:ml-6 sm:flex sm:items-center">
          <div class="flex space-x-1">
            <router-link v-for="item in navigationItems" :key="item.name" :to="item.href" :class="[
              isActive(item.href)
                ? 'bg-gray-200/80 text-gray-800'
                : 'text-gray-600 hover:bg-gray-200/60 hover:text-gray-800',
              'px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 hover:scale-105 hover:shadow-md',
            ]" v-show="shouldShowItem(item)">
              {{ item.name }}
            </router-link>
          </div>
        </div>

        <!-- User dropdown menu -->
        <div class="hidden sm:ml-6 sm:flex sm:items-center">
          <div class="relative">
            <button @click="toggleUserMenu" type="button"
              class="flex items-center rounded-lg bg-gray-200/80 text-gray-800 hover:bg-gray-300/80 hover:scale-105 hover:shadow-md transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
              id="user-menu-button" :aria-expanded="showUserMenu" aria-haspopup="true">
              <span class="sr-only">Open user menu</span>
              <div class="h-9 w-9 rounded-full flex items-center justify-center text-sm font-semibold">
                {{ userInitials }}
              </div>
            </button>

            <!-- Dropdown menu -->
            <div v-if="showUserMenu"
              class="absolute right-0 z-20 mt-2 w-56 origin-top-right rounded-xl bg-gray-100/90 backdrop-blur-sm py-2 shadow-xl border border-gray-200/60 transform transition-all duration-300"
              :class="showUserMenu ? 'opacity-100 scale-100' : 'opacity-0 scale-95'" role="menu"
              aria-orientation="vertical" aria-labelledby="user-menu-button">
              <div class="px-4 py-2 text-sm text-gray-500 border-b border-gray-200/60">
                Signed in as <span class="font-semibold text-gray-700">{{ username }}</span>
              </div>
              <!-- Uncomment if profile page is needed -->
              <!-- <router-link
                to="/profile"
                class="block px-4 py-2 text-sm text-gray-700 hover:bg-indigo-50 hover:text-indigo-700"
                role="menuitem"
              >
                Your Profile
              </router-link> -->
              <button type="button" @click="handleLogout"
                class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-200/60 hover:text-gray-800 transition-all duration-200"
                role="menuitem">
                Sign out
              </button>
            </div>
          </div>
        </div>

        <!-- Mobile menu button -->
        <div class="-mr-2 flex items-center sm:hidden">
          <button @click="toggleMobileMenu" type="button"
            class="inline-flex items-center justify-center rounded-lg p-2 text-gray-500 hover:bg-gray-200/60 hover:text-gray-700 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 transition-all duration-200"
            aria-controls="mobile-menu" :aria-expanded="showMobileMenu">
            <span class="sr-only">Open main menu</span>
            <Bars3Icon v-if="!showMobileMenu" class="h-6 w-6" aria-hidden="true" />
            <XMarkIcon v-else class="h-6 w-6" aria-hidden="true" />
          </button>
        </div>
      </div>
    </div>

    <!-- Mobile menu -->
    <div v-if="showMobileMenu" class="sm:hidden bg-gray-100/90 backdrop-blur-sm border-b border-gray-200/60 shadow-md" id="mobile-menu">
      <div class="space-y-1 pt-2 pb-3">
        <router-link v-for="item in navigationItems" :key="item.name" :to="item.href" :class="[
          isActive(item.href)
            ? 'bg-gray-200/80 text-gray-800'
            : 'text-gray-600 hover:bg-gray-200/60 hover:text-gray-800',
          'block px-4 py-3 rounded-md text-base font-medium transition-all duration-200 hover:scale-105 hover:shadow-md',
        ]" @click="toggleMobileMenu" v-show="shouldShowItem(item)">
          {{ item.name }}
        </router-link>
      </div>
      <div class="border-t border-gray-200/60 pt-4 pb-3">
        <div class="flex items-center px-4">
          <div class="flex-shrink-0">
            <div
              class="h-10 w-10 rounded-full bg-gray-200/80 flex items-center justify-center text-gray-800 font-semibold">
              {{ userInitials }}
            </div>
          </div>
          <div class="ml-3">
            <div class="text-base font-medium text-gray-800">{{ username }}</div>
            <div class="text-sm font-medium text-gray-500">{{ userRole }}</div>
          </div>
        </div>
        <div class="mt-3 space-y-1">
          <!-- <router-link
            to="/profile"
            class="block px-4 py-2 text-base font-medium text-gray-500 hover:bg-indigo-50 hover:text-indigo-700"
            @click="toggleMobileMenu"
          >
            Your Profile
          </router-link> -->
          <button type="button" @click="handleLogout"
            class="block w-full text-left px-4 py-2 text-base font-medium text-gray-500 hover:bg-gray-200/60 hover:text-gray-800 transition-all duration-200">
            Sign out
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
/* Custom animations for dropdown and mobile menu */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

#mobile-menu {
  animation: slideDown 0.3s ease-out;
}
</style>
