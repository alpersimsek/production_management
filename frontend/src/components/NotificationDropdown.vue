<template>
  <div class="relative">
    <!-- Notification Bell -->
    <button
      @click="toggleDropdown"
      class="relative p-2 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
    >
      <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-5 5v-5zM4 19h5l-5-5v5zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/>
      </svg>

      <!-- Unread Badge -->
      <span
        v-if="notificationStore.unreadCount > 0"
        class="absolute -top-1 -right-1 h-5 w-5 bg-red-500 text-white text-xs rounded-full flex items-center justify-center"
      >
        {{ notificationStore.unreadCount > 99 ? '99+' : notificationStore.unreadCount }}
      </span>
    </button>

    <!-- Dropdown -->
    <div
      v-if="showDropdown"
      class="absolute right-0 mt-2 w-80 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 z-50"
    >
      <div class="p-4 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h3 class="text-lg font-medium text-gray-900">Notifications</h3>
          <div class="flex space-x-2">
            <button
              v-if="notificationStore.unreadCount > 0"
              @click="markAllAsRead"
              class="text-sm text-primary-600 hover:text-primary-800"
            >
              Mark all read
            </button>
            <button
              @click="refreshNotifications"
              class="text-sm text-gray-600 hover:text-gray-800"
            >
              Refresh
            </button>
          </div>
        </div>
      </div>

      <div class="max-h-96 overflow-y-auto">
        <div v-if="notificationStore.loading" class="p-4 text-center">
          <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
          <p class="mt-2 text-sm text-gray-600">Loading...</p>
        </div>

        <div v-else-if="notificationStore.notifications.length === 0" class="p-4 text-center text-gray-500">
          No notifications
        </div>

        <div v-else>
          <div
            v-for="notification in notificationStore.notifications.slice(0, 10)"
            :key="notification.id"
            :class="[
              'p-4 border-b border-gray-100 hover:bg-gray-50 cursor-pointer',
              !notification.is_read ? 'bg-blue-50' : ''
            ]"
            @click="handleNotificationClick(notification)"
          >
            <div class="flex items-start space-x-3">
              <div class="flex-shrink-0">
                <div
                  :class="[
                    'h-2 w-2 rounded-full mt-2',
                    getNotificationColor(notification.notification_type)
                  ]"
                ></div>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 truncate">
                  {{ notification.title }}
                </p>
                <p class="text-sm text-gray-500 mt-1 line-clamp-2">
                  {{ notification.message }}
                </p>
                <p class="text-xs text-gray-400 mt-1">
                  {{ formatTime(notification.created_at) }}
                </p>
              </div>
              <div class="flex-shrink-0">
                <button
                  @click.stop="deleteNotification(notification.id)"
                  class="text-gray-400 hover:text-gray-600"
                >
                  <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="notificationStore.notifications.length > 10" class="p-4 border-t border-gray-200">
        <button
          @click="viewAllNotifications"
          class="w-full text-center text-sm text-primary-600 hover:text-primary-800"
        >
          View all notifications
        </button>
      </div>
    </div>

    <!-- Click outside to close -->
    <div
      v-if="showDropdown"
      @click="showDropdown = false"
      class="fixed inset-0 z-40"
    ></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/store/notifications'

const router = useRouter()
const notificationStore = useNotificationStore()

const showDropdown = ref(false)

// Methods
function toggleDropdown () {
  showDropdown.value = !showDropdown.value
  if (showDropdown.value) {
    notificationStore.fetchNotifications()
  }
}

function getNotificationColor (type) {
  const colors = {
    info: 'bg-blue-500',
    warning: 'bg-yellow-500',
    error: 'bg-red-500',
    success: 'bg-green-500'
  }
  return colors[type] || 'bg-gray-500'
}

function formatTime (dateString) {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  if (diff < 60000) return 'Just now'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
  return date.toLocaleDateString()
}

async function handleNotificationClick (notification) {
  if (!notification.is_read) {
    await notificationStore.markAsRead(notification.id)
  }

  // Handle notification action if data contains route
  if (notification.data && notification.data.route) {
    router.push(notification.data.route)
  }

  showDropdown.value = false
}

async function markAllAsRead () {
  await notificationStore.markAllAsRead()
}

async function refreshNotifications () {
  await notificationStore.fetchNotifications()
}

async function deleteNotification (id) {
  await notificationStore.deleteNotification(id)
}

function viewAllNotifications () {
  // TODO: Navigate to full notifications page
  showDropdown.value = false
}

// Lifecycle
onMounted(() => {
  notificationStore.initialize()
})

onUnmounted(() => {
  showDropdown.value = false
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>
