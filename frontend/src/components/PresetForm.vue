<!--
GDPR Tool Preset Form - Preset Creation and Editing Modal Component

This component provides a modal dialog for creating and editing presets in the GDPR compliance tool.
It allows users to define presets with names, headers, and product associations.

Key Features:
- Preset Creation: Form for creating new presets
- Preset Editing: Edit existing presets with pre-populated data
- Product Association: Link presets to specific products
- Form Validation: Required field validation with error handling
- Success Feedback: Clear success messages and error handling
- Modal Interface: Full-screen modal with backdrop and transitions

Props:
- open: Whether the modal is open (boolean, default: false)
- editPreset: Preset object for editing (object, optional)
- products: Array of available products (array, default: [])
- defaultProductId: Default product ID for new presets (string/number, optional)

Events:
- close: Emitted when modal is closed
- saved: Emitted when preset is successfully saved
- error: Emitted when an error occurs

Features:
- Preset Name: Text input for preset name
- Header Input: Text input for preset header
- Product Selection: Dropdown for product association
- Form Validation: Ensures all required fields are filled
- Success Messages: Clear feedback for successful operations
- Error Handling: Comprehensive error handling and display

The component provides a comprehensive interface for preset management in the
GDPR compliance tool with proper validation and user feedback.
-->

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { XMarkIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'

const props = defineProps({
  open: { type: Boolean, default: false },
  editPreset: { type: Object, default: null },
  products: { type: Array, default: () => [] },
  defaultProductId: { type: [String, Number], default: null }
})

const emit = defineEmits(['close', 'saved', 'error'])

const form = ref({ name: '', header: '', productId: null })
const saving = ref(false)
const successMessage = ref('')
const editing = computed(() => {
  const isEditing = !!props.editPreset && typeof props.editPreset === 'object'
  console.log('PresetForm - editPreset prop:', props.editPreset)
  console.log('PresetForm - editing computed:', isEditing)
  return isEditing
})

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    initializeForm()
    successMessage.value = ''
  }
})

const initializeForm = () => {
  console.log('PresetForm - initializeForm called')
  console.log('PresetForm - props.editPreset:', props.editPreset)
  console.log('PresetForm - props.defaultProductId:', props.defaultProductId)
  
  if (props.editPreset && typeof props.editPreset === 'object') {
    console.log('PresetForm - Initializing form for EDITING')
    form.value = {
      name: props.editPreset.name || '',
      header: props.editPreset.header || '',
      productId: props.editPreset.product_id || null
    }
  } else {
    console.log('PresetForm - Initializing form for ADDING NEW')
    form.value = {
      name: '',
      header: '',
      productId: props.defaultProductId || (props.products && props.products.length > 0 ? props.products[0].id : null)
    }
  }
  
  console.log('PresetForm - Form initialized with:', form.value)
}

const savePreset = async () => {
  try {
    saving.value = true
    if (!form.value.name || !form.value.header || !form.value.productId) {
      emit('error', 'Please fill in all fields')
      return
    }
    const presetData = { name: form.value.name, header: form.value.header, product_id: form.value.productId }
    const response = editing.value
      ? await ApiService.updatePreset(props.editPreset.id, presetData)
      : await ApiService.createPreset(presetData)
    successMessage.value = editing.value ? 'Preset updated successfully' : 'Preset created successfully'
    setTimeout(() => {
      emit('saved', response)
      emit('close')
    }, 1000)
  } catch (err) {
    emit('error', `Failed to ${editing.value ? 'update' : 'create'} preset: ${err.message || err.data?.detail || 'Unknown error'}`)
  } finally {
    saving.value = false
  }
}

initializeForm()
</script>

<template>
  <Dialog as="div" class="relative z-10" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/60 transition-opacity duration-300" />
    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-xl bg-white px-6 py-8 shadow-2xl transition-all duration-300 sm:max-w-lg sm:w-full sm:scale-100">
          <button type="button"
            class="absolute right-4 top-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            @click="$emit('close')" aria-label="Close">
            <XMarkIcon class="h-6 w-6" />
          </button>
          <DialogTitle as="h3" class="text-lg font-semibold text-gray-900">
            {{ editing ? 'Edit Preset' : 'Add New Preset' }}
          </DialogTitle>
          <div v-if="successMessage" class="mt-4 rounded-md bg-green-50 p-3 flex items-center">
            <CheckCircleIcon class="h-5 w-5 text-green-400" />
            <p class="ml-2 text-sm text-green-800">{{ successMessage }}</p>
          </div>
          <div class="mt-6 space-y-6">
            <div>
              <label for="preset-name" class="block text-sm font-medium text-gray-700">Name</label>
              <input type="text" id="preset-name" v-model="form.name"
                class="mt-2 block w-full rounded-md border-gray-300 py-2.5 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                placeholder="Preset name" required />
            </div>
            <div>
              <label for="preset-header" class="block text-sm font-medium text-gray-700">Header</label>
              <input type="text" id="preset-header" v-model="form.header"
                class="mt-2 block w-full rounded-md border-gray-300 py-2.5 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                placeholder="Preset header" required />
            </div>
            <div>
              <label for="preset-product" class="block text-sm font-medium text-gray-700">Product</label>
              <select id="preset-product" v-model="form.productId"
                class="mt-2 block w-full rounded-md border-gray-300 py-2.5 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500">
                <option v-for="product in products" :key="product.id" :value="product.id">{{ product.name }}</option>
              </select>
            </div>
          </div>
          <div class="mt-8 flex justify-end gap-3">
            <button type="button"
              class="inline-flex rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-gray-300 hover:bg-gray-50"
              @click="$emit('close')" :disabled="saving">Cancel</button>
            <button type="button"
              class="inline-flex rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-indigo-400"
              @click="savePreset" :disabled="saving">
              <svg v-if="saving" class="animate-spin h-5 w-5 mr-2 text-white" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor"
                  d="M4 12a8 8 0 018-8v8h8a8 8 0 01-8 8 8 8 0 01-8-8z"></path>
              </svg>
              {{ editing ? 'Update' : 'Create' }}
            </button>
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
</style>