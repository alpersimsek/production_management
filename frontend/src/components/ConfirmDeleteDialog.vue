<!--
GDPR Tool Confirm Delete Dialog - Confirmation Modal Component

This component provides a confirmation dialog for delete operations in the GDPR compliance tool.
It ensures users confirm destructive actions with proper warnings and loading states.

Key Features:
- Confirmation Dialog: Modal dialog for confirming delete operations
- Warning Display: Clear warning message about irreversible actions
- Loading States: Visual feedback during delete operations
- Accessibility: Proper ARIA attributes and keyboard navigation
- Animation Effects: Smooth transitions and hover animations
- Responsive Design: Mobile-first responsive layout

Props:
- open: Whether the dialog is open (boolean, required)
- itemType: Type of item being deleted (string, default: 'item')

Events:
- close: Emitted when dialog is closed
- confirm: Emitted when delete is confirmed

Features:
- Warning Icon: Visual warning indicator
- Confirmation Message: Clear message about irreversible action
- Action Buttons: Cancel and Delete buttons with proper styling
- Loading State: Spinner animation during delete operation
- Hover Effects: Shake animation on delete button hover
- Backdrop Blur: Blurred background for focus

The component provides a safe and user-friendly confirmation interface for
destructive operations in the GDPR compliance tool.
-->

<script setup>
import { ref } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { ExclamationTriangleIcon } from '@heroicons/vue/24/outline'

defineProps({ open: { type: Boolean, required: true }, itemType: { type: String, default: 'item' } })
const emit = defineEmits(['close', 'confirm'])
const loading = ref(false)

const handleConfirm = () => {
  loading.value = true
  emit('confirm')
  loading.value = false
}
</script>

<template>
  <Dialog as="div" class="relative z-30" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/60 transition-opacity duration-300" />
    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-2xl bg-white px-8 py-10 shadow-2xl transition-all duration-300 sm:w-full sm:max-w-lg">
          <!-- Header with Icon -->
          <div class="flex items-center justify-center mb-6">
            <div class="flex items-center justify-center w-16 h-16 bg-red-100 rounded-full">
              <ExclamationTriangleIcon class="h-8 w-8 text-red-600" />
            </div>
          </div>

          <!-- Title -->
          <DialogTitle as="h3" class="text-center text-2xl font-bold text-gray-900 mb-4">
            Confirm Delete
          </DialogTitle>

          <!-- Message -->
          <div class="text-center mb-8">
            <p class="text-gray-600 text-lg leading-relaxed">
              Are you sure you want to delete this <span class="font-semibold text-gray-900">{{ itemType }}</span>? 
              This action cannot be undone.
            </p>
          </div>

          <!-- Action Buttons -->
          <div class="flex flex-col sm:flex-row gap-3 sm:gap-4">
            <button 
              type="button"
              class="flex-1 inline-flex items-center justify-center rounded-lg bg-gray-100 px-6 py-3 text-sm font-semibold text-gray-700 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              @click="$emit('close')" 
              :disabled="loading"
            >
              Cancel
            </button>
            <button 
              type="button"
              class="flex-1 inline-flex items-center justify-center rounded-lg bg-red-600 px-6 py-3 text-sm font-semibold text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200 disabled:bg-red-400 disabled:cursor-not-allowed hover:animate-shake"
              @click="handleConfirm" 
              :disabled="loading"
            >
              <svg v-if="loading" class="animate-spin h-4 w-4 mr-2 text-white" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8h8a8 8 0 01-8 8 8 8 0 01-8-8z"></path>
              </svg>
              {{ loading ? 'Deleting...' : 'Delete' }}
            </button>
          </div>

          <!-- Warning Footer -->
          <div class="mt-6 text-center">
            <p class="text-xs text-red-500 font-medium">
              ⚠️ This action is permanent and cannot be reversed
            </p>
          </div>
        </DialogPanel>
      </div>
    </div>
  </Dialog>
</template>

<style scoped>
.transition-all {
  transition: all 0.3s ease-in-out;
}

@keyframes shake {

  0%,
  100% {
    transform: translateX(0);
  }

  10%,
  30%,
  50%,
  70%,
  90% {
    transform: translateX(-2px);
  }

  20%,
  40%,
  60%,
  80% {
    transform: translateX(2px);
  }
}

.animate-shake {
  animation: shake 0.5s cubic-bezier(.36, .07, .19, .97) both;
}
</style>