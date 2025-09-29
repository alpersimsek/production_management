<!--
GDPR Tool Product Form - Product Creation Modal Component

This component provides a modal dialog for creating new products in the GDPR compliance tool.
It allows administrators to add new products to the system for preset management.

Key Features:
- Product Creation: Form for creating new products
- Form Validation: Required field validation with error handling
- Success Feedback: Clear success messages and error handling
- Modal Interface: Full-screen modal with backdrop and transitions

Props:
- open: Whether the modal is open (boolean, default: false)

Events:
- close: Emitted when modal is closed
- saved: Emitted when product is successfully saved
- error: Emitted when an error occurs

Features:
- Product Name: Text input for product name
- Form Validation: Ensures product name is provided
- Success Messages: Clear feedback for successful operations
- Error Handling: Comprehensive error handling and display

The component provides a comprehensive interface for product management in the
GDPR compliance tool with proper validation and user feedback.
-->

<script setup>
import { ref, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { XMarkIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'
import InputField from './InputField.vue'

const props = defineProps({
  open: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'saved', 'error'])

const form = ref({ name: '' })
const saving = ref(false)
const successMessage = ref('')

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    initializeForm()
    successMessage.value = ''
  }
})

const initializeForm = () => {
  form.value = { name: '' }
}

const saveProduct = async () => {
  try {
    saving.value = true
    if (!form.value.name.trim()) {
      emit('error', 'Product name is required')
      return
    }

    const productData = {
      name: form.value.name.trim()
    }

    await ApiService.createProduct(productData)
    successMessage.value = 'Product created successfully!'
    
    // Reset form
    form.value = { name: '' }
    
    // Emit saved event after a short delay to show success message
    setTimeout(() => {
      emit('saved')
    }, 1000)
  } catch (err) {
    const errorMessage = err.message || err.data?.detail || 'Failed to create product'
    emit('error', errorMessage)
  } finally {
    saving.value = false
  }
}

const closeModal = () => {
  if (!saving.value) {
    emit('close')
  }
}
</script>

<template>
  <Dialog :open="open" @close="closeModal" class="relative z-50">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/60 transition-opacity duration-300" aria-hidden="true" />
    <div class="fixed inset-0 flex items-center justify-center p-4">
      <DialogPanel class="mx-auto max-w-md w-full bg-white/90 backdrop-blur-sm border border-slate-200/60 rounded-2xl shadow-2xl">
        <div class="p-6">
          <div class="flex items-center justify-between mb-6">
            <div>
              <DialogTitle class="text-2xl font-bold text-slate-900">
                Add New Product
              </DialogTitle>
              <p class="mt-1 text-sm text-slate-600">Create a new product category for organizing presets and masking rules</p>
            </div>
            <button
              type="button"
              @click="closeModal"
              :disabled="saving"
              class="text-slate-400 hover:text-slate-600 focus:outline-none focus:ring-2 focus:ring-gray-400 rounded-lg p-1 transition-all duration-200 disabled:opacity-50"
              aria-label="Close modal"
            >
              <XMarkIcon class="h-6 w-6" />
            </button>
          </div>

          <div v-if="successMessage" class="mb-6 p-4 bg-green-50/80 backdrop-blur-sm border border-green-200/60 rounded-2xl">
            <div class="flex items-center">
              <CheckCircleIcon class="h-5 w-5 text-green-400 mr-3" />
              <p class="text-sm font-medium text-green-800">{{ successMessage }}</p>
            </div>
          </div>

          <form @submit.prevent="saveProduct" class="space-y-6">
            <InputField
              id="product-name"
              v-model="form.name"
              label="Product Name"
              type="text"
              placeholder="Enter product name"
              required
              :disabled="saving"
              :maxlength="100"
            />

            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="closeModal"
                :disabled="saving"
                class="px-4 py-2 text-sm font-semibold text-gray-700 bg-white/80 backdrop-blur-sm border border-gray-200/60 rounded-2xl hover:bg-gray-100/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                :disabled="saving || !form.name.trim()"
                class="px-4 py-2 text-sm font-semibold text-white bg-gradient-to-r from-gray-500 to-slate-600 rounded-2xl hover:from-gray-600 hover:to-slate-700 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:from-gray-400 disabled:to-slate-500 disabled:cursor-not-allowed transition-all duration-200"
              >
                <span v-if="saving" class="flex items-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creating...
                </span>
                <span v-else>Create Product</span>
              </button>
            </div>
          </form>
        </div>
      </DialogPanel>
    </div>
  </Dialog>
</template>

<style scoped>
/* Add any custom styles if needed */
</style>

