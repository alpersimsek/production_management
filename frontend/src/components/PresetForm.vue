<template>
  <Dialog as="div" class="relative" style="z-index: 10;" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/50 transition-opacity" @mousedown.stop
      style="z-index: 10;" />
    <div class="fixed inset-0 overflow-y-auto" style="z-index: 10;">
      <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
          <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
            <button type="button"
              class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              @click="$emit('close')">
              <span class="sr-only">Close</span>
              <XMarkIcon class="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div>
            <div class="mt-3 text-center sm:mt-0 sm:text-left">
              <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                {{ editing ? 'Edit Preset' : 'Add New Preset' }}
              </DialogTitle>
              <div class="mt-4 space-y-4">
                <div>
                  <label for="preset-name" class="block text-sm font-medium text-gray-700">Name</label>
                  <div class="mt-1">
                    <input type="text" id="preset-name" v-model="form.name"
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      placeholder="Preset name" />
                  </div>
                </div>

                <div>
                  <label for="preset-header" class="block text-sm font-medium text-gray-700">Header</label>
                  <div class="mt-1">
                    <input type="text" id="preset-header" v-model="form.header"
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      placeholder="Preset header" />
                  </div>
                </div>

                <div>
                  <label for="preset-product" class="block text-sm font-medium text-gray-700">Product</label>
                  <div class="mt-1">
                    <select id="preset-product" v-model="form.productId"
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm">
                      <option v-for="product in products" :key="product.id" :value="product.id">
                        {{ product.name }}
                      </option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
            <button type="button"
              class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:ml-3 sm:w-auto"
              @click="savePreset" :disabled="saving">
              {{ editing ? 'Update' : 'Create' }}
            </button>
            <button type="button"
              class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
              @click="$emit('close')">
              Cancel
            </button>
          </div>
        </DialogPanel>
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'

const props = defineProps({
  open: {
    type: Boolean,
    required: true
  },
  preset: {
    type: Object,
    default: null
  },
  products: {
    type: Array,
    required: true
  },
  defaultProductId: {
    type: [String, Number],
    default: null
  }
})

const emit = defineEmits(['close', 'saved', 'error'])

// Form data
const form = ref({
  name: '',
  header: '',
  productId: null
})

// Computed values
const editing = computed(() => !!props.preset)
const saving = ref(false)

// Watch for changes to props
watch(() => props.open, (isOpen) => {
  if (isOpen) {
    initializeForm()
  }
})

// Initialize form data
const initializeForm = () => {
  if (props.preset) {
    // Edit mode
    form.value = {
      name: props.preset.name,
      header: props.preset.header,
      productId: props.preset.product_id
    }
  } else {
    // Create mode
    form.value = {
      name: '',
      header: '',
      productId: props.defaultProductId || (props.products.length > 0 ? props.products[0].id : null)
    }
  }
}

// Save preset
const savePreset = async () => {
  try {
    saving.value = true

    if (!form.value.name || !form.value.header || !form.value.productId) {
      emit('error', 'Please fill in all fields')
      return
    }

    const presetData = {
      name: form.value.name,
      header: form.value.header,
      product_id: form.value.productId
    }

    let response
    if (props.preset) {
      // Update existing preset
      response = await ApiService.updatePreset(props.preset.id, presetData)
    } else {
      // Create new preset
      response = await ApiService.createPreset(presetData)
    }

    emit('saved', response)
    emit('close')
  } catch (err) {
    emit('error', `Failed to ${props.preset ? 'update' : 'create'} preset: ${err.message || 'Unknown error'}`)
  } finally {
    saving.value = false
  }
}

// Initialize form when component is created
initializeForm()
</script>
