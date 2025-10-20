<template>
  <div class="min-h-screen bg-secondary-50">
    <!-- Sidebar -->
    <aside
      :class="sidebarClasses"
      class="fixed inset-y-0 left-0 z-40 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out"
    >
      <!-- Logo -->
      <div class="flex items-center justify-center h-16 px-4 border-b border-secondary-200">
        <div class="flex items-center">
          <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <svg class="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" />
            </svg>
          </div>
          <span class="ml-2 text-xl font-bold text-secondary-900">DEMO ERP</span>
        </div>
      </div>

      <!-- Navigation -->
      <nav class="mt-6 px-4">
        <ul class="space-y-2">
          <li v-for="item in navigationItems" :key="item.name">
            <router-link
              :to="item.href"
              :class="getNavItemClasses(item)"
              class="group flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-200"
              @click="closeMobileMenu"
            >
              <component
                :is="item.icon"
                :class="getNavIconClasses(item)"
                class="w-5 h-5 mr-3"
              />
              {{ item.name }}

              <!-- Badge -->
              <span
                v-if="item.badge"
                class="ml-auto bg-primary-100 text-primary-800 text-xs font-medium px-2 py-0.5 rounded-full"
              >
                {{ item.badge }}
              </span>
            </router-link>
          </li>
        </ul>
      </nav>

      <!-- User Section -->
      <div class="absolute bottom-0 left-0 right-0 p-4 border-t border-secondary-200">
        <div class="flex items-center">
          <div class="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
            <span class="text-sm font-medium text-white">{{ userInitials }}</span>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-secondary-900">{{ userName }}</p>
            <p class="text-xs text-secondary-500">{{ userRole }}</p>
          </div>
        </div>
      </div>
    </aside>

    <!-- Main Content -->
    <div class="lg:pl-64">
      <!-- Top Bar -->
      <header class="bg-white shadow-sm border-b border-secondary-200">
        <div class="flex items-center justify-between h-16 px-3 sm:px-6">
          <!-- Mobile Menu Button -->
          <button
            @click="toggleSidebar"
            class="lg:hidden p-2 rounded-md text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100"
          >
            <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>

          <!-- Page Title -->
          <div class="flex-1 min-w-0 mx-2 sm:mx-4">
            <h1 class="text-lg sm:text-xl lg:text-2xl font-semibold text-secondary-900 truncate">{{ currentPageTitle }}</h1>
          </div>

          <!-- Right Side Actions -->
          <div class="flex items-center space-x-1 sm:space-x-2 lg:space-x-4">
            <!-- Language Switcher - Mobile Icon Only -->
            <div class="lg:hidden">
              <LanguageSwitcher />
            </div>

            <!-- Language Switcher - Desktop Full -->
            <div class="hidden lg:block">
              <LanguageSwitcher />
            </div>

            <!-- Notifications -->
            <button class="p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-md">
              <svg class="w-5 h-5 sm:w-6 sm:h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
              </svg>
            </button>

            <!-- User Menu -->
            <div class="relative">
              <button
                @click="toggleUserMenu"
                class="flex items-center p-2 text-secondary-600 hover:text-secondary-900 hover:bg-secondary-100 rounded-md"
              >
                <div class="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center">
                  <span class="text-sm font-medium text-white">{{ userInitials }}</span>
                </div>
                <svg class="w-4 h-4 ml-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <!-- User Dropdown -->
              <div
                v-if="showUserMenu"
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg py-1 z-50"
              >
                <a href="#" class="block px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-100">Profile</a>
                <a href="#" class="block px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-100">Settings</a>
                <hr class="my-1">
                <a href="#" class="block px-4 py-2 text-sm text-secondary-700 hover:bg-secondary-100" @click="logout">Logout</a>
              </div>
            </div>
          </div>
        </div>
      </header>

      <!-- Page Content -->
      <main class="p-6">
        <router-view />
      </main>
    </div>

    <!-- Mobile Overlay -->
    <div
      v-if="isMobileMenuOpen"
      class="fixed inset-0 z-30 bg-black bg-opacity-50 lg:hidden"
      @click="closeMobileMenu"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import LanguageSwitcher from '@/components/LanguageSwitcher.vue'

const route = useRoute()
const router = useRouter()
const { t } = useI18n()

const isMobileMenuOpen = ref(false)
const showUserMenu = ref(false)
const userName = ref('Admin User')
const userRole = ref('Administrator')

const userInitials = computed(() => {
  return userName.value
    .split(' ')
    .map(name => name[0])
    .join('')
    .toUpperCase()
})

const currentPageTitle = computed(() => {
  const currentItem = navigationItems.value.find(item => item.current)
  return currentItem ? currentItem.name : t('nav.dashboard')
})

const navigationItems = computed(() => [
  {
    name: t('nav.dashboard'),
    href: '/',
    icon: 'HomeIcon',
    current: route.path === '/'
  },
  {
    name: t('nav.orders'),
    href: '/orders',
    icon: 'DocumentTextIcon',
    current: route.path.startsWith('/orders')
  },
  {
    name: t('nav.customers'),
    href: '/customers',
    icon: 'UsersIcon',
    current: route.path.startsWith('/customers')
  },
  {
    name: t('nav.products'),
    href: '/products',
    icon: 'CubeIcon',
    current: route.path.startsWith('/products')
  },
  {
    name: t('nav.production'),
    href: '/production-jobs',
    icon: 'CogIcon',
    current: route.path.startsWith('/production-jobs')
  },
  {
    name: t('nav.packaging'),
    href: '/packaging',
    icon: 'ArchiveBoxIcon',
    current: route.path.startsWith('/packaging')
  },
  {
    name: t('nav.warehouse'),
    href: '/warehouses',
    icon: 'BuildingOfficeIcon',
    current: route.path.startsWith('/warehouses')
  },
  {
    name: t('nav.shipments'),
    href: '/shipments',
    icon: 'TruckIcon',
    current: route.path.startsWith('/shipments')
  },
  {
    name: t('nav.analytics'),
    href: '/analytics',
    icon: 'ChartBarIcon',
    current: route.path.startsWith('/analytics')
  },
  {
    name: t('nav.settings'),
    href: '/settings',
    icon: 'Cog6ToothIcon',
    current: route.path.startsWith('/settings')
  }
])

const sidebarClasses = computed(() => {
  return isMobileMenuOpen.value ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
})

const getNavItemClasses = (item) => {
  if (item.current) {
    return 'bg-primary-100 text-primary-900'
  }
  return 'text-secondary-600 hover:bg-secondary-100 hover:text-secondary-900'
}

const getNavIconClasses = (item) => {
  if (item.current) {
    return 'text-primary-600'
  }
  return 'text-secondary-400 group-hover:text-secondary-600'
}

const toggleSidebar = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}

const logout = () => {
  // Implement logout logic
  router.push('/login')
}

// Close menus when clicking outside
const handleClickOutside = (event) => {
  if (!event.target.closest('.relative')) {
    showUserMenu.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
