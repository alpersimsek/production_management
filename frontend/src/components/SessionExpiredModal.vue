<!--
GDPR Tool Session Expired Modal - Styled Session Expiration Component

This component provides a professional, styled modal for displaying session expiration
notifications. It replaces the basic browser alert with a modern, branded interface.

Key Features:
- Professional Design: Clean, modern modal design with GDPR tool branding
- Clear Messaging: Clear explanation of session expiration and required actions
- Action Buttons: Login redirect and dismiss options
- Animation Effects: Smooth entrance and exit animations
- Accessibility: Proper ARIA attributes and keyboard navigation
- Responsive: Mobile-first responsive design

Props:
- open: Whether the modal is open (boolean, required)

Events:
- close: Emitted when modal is closed
- login: Emitted when user clicks login button

Features:
- Warning Icon: Visual warning indicator
- Clear Message: User-friendly explanation of session expiration
- Action Buttons: Login and dismiss options
- Backdrop Blur: Blurred background for focus
- Auto Focus: Automatic focus on login button for accessibility
- Keyboard Support: ESC key to close, Enter to login
-->

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { ExclamationTriangleIcon, ArrowRightOnRectangleIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  open: { type: Boolean, required: true }
})

const emit = defineEmits(['close', 'login'])

const handleLogin = () => {
  emit('login')
  emit('close')
}

const handleClose = () => {
  emit('close')
}

const handleKeydown = (event) => {
  if (event.key === 'Escape') {
    handleClose()
  } else if (event.key === 'Enter') {
    handleLogin()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<template>
  <Dialog as="div" class="relative z-50" @close="handleClose" :open="open">
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/60 backdrop-blur-sm transition-opacity duration-300" />
    
    <!-- Modal Container -->
    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-2xl bg-white px-6 py-8 shadow-2xl transition-all duration-300 sm:w-full sm:max-w-md"
        >
          <!-- Header -->
          <div class="flex items-center justify-center mb-6">
            <div class="flex items-center justify-center w-16 h-16 bg-red-100 rounded-full">
              <ExclamationTriangleIcon class="h-8 w-8 text-red-600" />
            </div>
          </div>

          <!-- Title -->
          <DialogTitle as="h3" class="text-center text-2xl font-bold text-gray-900 mb-4">
            Session Expired
          </DialogTitle>

          <!-- Message -->
          <div class="text-center mb-8">
            <p class="text-gray-600 text-lg leading-relaxed">
              Your session has expired for security reasons. Please log in again to continue using the GDPR Tool.
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-3 sm:gap-4">
            <button
              type="button"
              @click="handleClose"
              class="flex-1 inline-flex items-center justify-center rounded-lg bg-gray-100 px-6 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors duration-200"
            >
              Dismiss
            </button>
            <button
              type="button"
              @click="handleLogin"
              class="flex-1 inline-flex items-center justify-center rounded-lg bg-indigo-600 px-6 py-3 text-sm font-semibold text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors duration-200"
            >
              <ArrowRightOnRectangleIcon class="h-4 w-4 mr-2" />
              Log In Again
            </button>
          </div>

          <!-- Footer Info -->
          <div class="mt-6 text-center">
            <p class="text-xs text-gray-500">
              For security, sessions expire after a period of inactivity
            </p>
          </div>
        </DialogPanel>
      </div>
    </div>
  </Dialog>
</template>

<style scoped>
/* Custom animations */
.transition-all {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Focus styles for better accessibility */
button:focus {
  outline: none;
}

/* Hover effects */
button:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

/* Active state */
button:active {
  transform: translateY(0);
}
</style>
