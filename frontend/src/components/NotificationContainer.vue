<!--
GDPR Tool Notification Container - Toast Notification Display Component

This component provides a container for displaying multiple toast notifications
in different positions on the screen. It manages the layout and stacking of notifications.

Key Features:
- Multiple Positions: Support for top/bottom, left/right positioning
- Stack Management: Automatic stacking of multiple notifications
- Responsive Layout: Mobile-first responsive design
- Z-Index Management: Proper layering of notifications
- Animation Support: Smooth animations for notification appearance/disappearance

Positions:
- top-left: Top left corner
- top-right: Top right corner (default)
- bottom-left: Bottom left corner
- bottom-right: Bottom right corner
- top-center: Top center (for important notifications like login expired)

The component automatically groups notifications by position and provides
proper spacing and animation for a smooth user experience.
-->

<script setup>
import { computed } from 'vue'
import ToastNotification from './ToastNotification.vue'
import { globalNotifications } from '@/composables/useNotifications'

const { notifications, dismiss } = globalNotifications

// Group notifications by position
const notificationsByPosition = computed(() => {
  const groups = {}
  
  notifications.value.forEach(notification => {
    if (!groups[notification.position]) {
      groups[notification.position] = []
    }
    groups[notification.position].push(notification)
  })
  
  return groups
})

const handleDismiss = (id) => {
  dismiss(id)
}

const positionStyles = {
  'top-left': 'top-4 left-4',
  'top-right': 'top-4 right-4',
  'top-center': 'top-4 left-1/2 transform -translate-x-1/2',
  'bottom-left': 'bottom-4 left-4',
  'bottom-right': 'bottom-4 right-4'
}
</script>

<template>
  <div class="fixed inset-0 pointer-events-none z-50">
    <!-- Top Left Notifications -->
    <div
      v-if="notificationsByPosition['top-left']?.length"
      :class="['absolute', positionStyles['top-left']]"
      class="space-y-2"
    >
      <ToastNotification
        v-for="notification in notificationsByPosition['top-left']"
        :key="notification.id"
        :open="notification.open"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :duration="notification.duration"
        :position="notification.position"
        @close="handleDismiss(notification.id)"
        @dismiss="handleDismiss(notification.id)"
      />
    </div>

    <!-- Top Right Notifications -->
    <div
      v-if="notificationsByPosition['top-right']?.length"
      :class="['absolute', positionStyles['top-right']]"
      class="space-y-2"
    >
      <ToastNotification
        v-for="notification in notificationsByPosition['top-right']"
        :key="notification.id"
        :open="notification.open"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :duration="notification.duration"
        :position="notification.position"
        @close="handleDismiss(notification.id)"
        @dismiss="handleDismiss(notification.id)"
      />
    </div>

    <!-- Top Center Notifications (for important messages like login expired) -->
    <div
      v-if="notificationsByPosition['top-center']?.length"
      :class="['absolute', positionStyles['top-center']]"
      class="space-y-2 w-full max-w-sm"
    >
      <ToastNotification
        v-for="notification in notificationsByPosition['top-center']"
        :key="notification.id"
        :open="notification.open"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :duration="notification.duration"
        :position="notification.position"
        @close="handleDismiss(notification.id)"
        @dismiss="handleDismiss(notification.id)"
      />
    </div>

    <!-- Bottom Left Notifications -->
    <div
      v-if="notificationsByPosition['bottom-left']?.length"
      :class="['absolute', positionStyles['bottom-left']]"
      class="space-y-2"
    >
      <ToastNotification
        v-for="notification in notificationsByPosition['bottom-left']"
        :key="notification.id"
        :open="notification.open"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :duration="notification.duration"
        :position="notification.position"
        @close="handleDismiss(notification.id)"
        @dismiss="handleDismiss(notification.id)"
      />
    </div>

    <!-- Bottom Right Notifications -->
    <div
      v-if="notificationsByPosition['bottom-right']?.length"
      :class="['absolute', positionStyles['bottom-right']]"
      class="space-y-2"
    >
      <ToastNotification
        v-for="notification in notificationsByPosition['bottom-right']"
        :key="notification.id"
        :open="notification.open"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :duration="notification.duration"
        :position="notification.position"
        @close="handleDismiss(notification.id)"
        @dismiss="handleDismiss(notification.id)"
      />
    </div>
  </div>
</template>

<style scoped>
/* Ensure notifications don't interfere with page content */
.pointer-events-none > * {
  pointer-events: auto;
}

/* Smooth transitions for notification groups */
.space-y-2 > * {
  transition: all 0.3s ease-in-out;
}
</style>
