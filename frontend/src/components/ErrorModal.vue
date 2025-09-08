<!--
GDPR Tool Error Modal - Professional Error Display Component

This component provides a professional-looking modal for displaying errors to users.
It handles various error types with appropriate icons, styling, and actions.

Key Features:
- Professional Error Display: Clean, modern error modal design
- Error Type Detection: Different styling for different error types
- Action Buttons: Retry, dismiss, and custom action options
- Detailed Information: Expandable error details for debugging
- Accessibility: Proper ARIA labels and keyboard navigation

Props:
- open: Whether the modal is open (boolean, default: false)
- error: Error object with type, message, and details (object, required)
- showRetry: Whether to show retry button (boolean, default: false)
- retryAction: Function to call when retry is clicked (function, optional)

Events:
- close: Emitted when modal is closed
- retry: Emitted when retry button is clicked
- dismiss: Emitted when dismiss button is clicked

Error Types:
- network: Network connectivity issues
- server: Server-side errors (5xx)
- validation: Client-side validation errors (4xx)
- auth: Authentication/authorization errors (401, 403)
- file: File processing errors
- unknown: Generic errors

The component provides a comprehensive interface for error management in the
GDPR compliance tool with professional styling and user experience.
-->

<script setup>
import { ref, computed } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { 
  ExclamationTriangleIcon, 
  XCircleIcon, 
  ExclamationCircleIcon,
  InformationCircleIcon,
  ArrowPathIcon,
  XMarkIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  open: { type: Boolean, default: false },
  error: { 
    type: Object, 
    default: () => ({
      type: 'unknown',
      message: 'An unknown error occurred',
      details: null,
      status: null,
      timestamp: new Date().toISOString()
    })
  },
  showRetry: { type: Boolean, default: false },
  retryAction: { type: Function, default: null },
  showCancel: { type: Boolean, default: false },
  cancelAction: { type: Function, default: null }
})

const emit = defineEmits(['close', 'retry', 'dismiss', 'cancel'])

const showDetails = ref(false)

const errorConfig = computed(() => {
  const configs = {
    network: {
      icon: XCircleIcon,
      iconColor: 'text-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      title: 'Connection Error',
      description: 'Unable to connect to the server'
    },
    server: {
      icon: ExclamationTriangleIcon,
      iconColor: 'text-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      title: 'Server Error',
      description: 'The server encountered an error processing your request'
    },
    validation: {
      icon: ExclamationCircleIcon,
      iconColor: 'text-yellow-500',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      title: 'Validation Error',
      description: 'Please check your input and try again'
    },
    auth: {
      icon: ExclamationTriangleIcon,
      iconColor: 'text-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      title: 'Authentication Error',
      description: 'You are not authorized to perform this action'
    },
    file: {
      icon: ExclamationCircleIcon,
      iconColor: 'text-orange-500',
      bgColor: 'bg-orange-50',
      borderColor: 'border-orange-200',
      title: 'File Processing Error',
      description: 'There was an error processing your file'
    },
    unknown: {
      icon: ExclamationCircleIcon,
      iconColor: 'text-gray-500',
      bgColor: 'bg-gray-50',
      borderColor: 'border-gray-200',
      title: 'Error',
      description: 'An unexpected error occurred'
    }
  }
  
  return configs[props.error.type] || configs.unknown
})

const formatTimestamp = (timestamp) => {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleString()
  } catch {
    return timestamp
  }
}

const handleRetry = () => {
  if (props.retryAction) {
    props.retryAction()
  }
  emit('retry')
}

const handleDismiss = () => {
  emit('dismiss')
}

const handleCancel = () => {
  if (props.cancelAction) {
    props.cancelAction()
  }
  emit('cancel')
}

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <Dialog :open="open" @close="handleClose" class="relative z-50">
    <div class="fixed inset-0 bg-black/50" aria-hidden="true" />
    <div class="fixed inset-0 flex items-center justify-center p-4">
      <DialogPanel class="mx-auto max-w-lg w-full bg-white rounded-xl shadow-2xl">
        <div class="p-6">
          <!-- Header -->
          <div class="flex items-start">
            <div class="flex-shrink-0">
              <component 
                :is="errorConfig.icon" 
                :class="['h-6 w-6', errorConfig.iconColor]" 
                aria-hidden="true" 
              />
            </div>
            <div class="ml-3 flex-1">
              <DialogTitle class="text-lg font-semibold text-gray-900">
                {{ errorConfig.title }}
              </DialogTitle>
              <p class="mt-1 text-sm text-gray-600">
                {{ errorConfig.description }}
              </p>
            </div>
            <button
              type="button"
              @click="handleClose"
              class="ml-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-lg p-1 transition-colors duration-200"
              aria-label="Close error modal"
            >
              <XMarkIcon class="h-5 w-5" />
            </button>
          </div>

          <!-- Error Message -->
          <div :class="['mt-4 p-4 rounded-lg border', errorConfig.bgColor, errorConfig.borderColor]">
            <p class="text-sm font-medium text-gray-900">
              {{ error.message }}
            </p>
            <p v-if="error.status" class="mt-1 text-xs text-gray-600">
              Error Code: {{ error.status }}
            </p>
          </div>

          <!-- Error Details (Expandable) -->
          <div v-if="error.details || error.timestamp" class="mt-4">
            <button
              type="button"
              @click="showDetails = !showDetails"
              class="flex items-center text-sm text-gray-600 hover:text-gray-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded-lg p-1 transition-colors duration-200"
            >
              <span>Error Details</span>
              <ChevronDownIcon v-if="!showDetails" class="ml-1 h-4 w-4" />
              <ChevronUpIcon v-else class="ml-1 h-4 w-4" />
            </button>
            
            <div v-if="showDetails" class="mt-2 p-3 bg-gray-50 rounded-lg border">
              <div v-if="error.details" class="text-xs text-gray-700 font-mono whitespace-pre-wrap">
                {{ typeof error.details === 'string' ? error.details : JSON.stringify(error.details, null, 2) }}
              </div>
              <div v-if="error.timestamp" class="mt-2 text-xs text-gray-500">
                Timestamp: {{ formatTimestamp(error.timestamp) }}
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              @click="handleDismiss"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors duration-200"
            >
              Dismiss
            </button>
            <button
              v-if="showCancel && cancelAction"
              type="button"
              @click="handleCancel"
              class="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors duration-200"
            >
              Cancel Processing
            </button>
            <button
              v-if="showRetry && retryAction"
              type="button"
              @click="handleRetry"
              class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors duration-200"
            >
              <ArrowPathIcon class="h-4 w-4 mr-2" />
              Retry
            </button>
            <button
              type="button"
              @click="handleClose"
              class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-colors duration-200"
            >
              Close
            </button>
          </div>
        </div>
      </DialogPanel>
    </div>
  </Dialog>
</template>

<style scoped>
/* Add any custom styles if needed */
</style>
