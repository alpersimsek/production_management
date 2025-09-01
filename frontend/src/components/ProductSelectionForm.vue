<template>
  <TransitionRoot as="template" :show="isOpen">
    <Dialog class="relative z-30" :open="isOpen" @close="handleCancel">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
        leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/60 transition-opacity" />
      </TransitionChild>
      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel
              class="relative transform overflow-hidden rounded-xl bg-white px-6 py-8 shadow-2xl sm:my-8 sm:w-full sm:max-w-lg">
              <button type="button"
                class="absolute right-4 top-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                @click="handleCancel" aria-label="Close modal">
                <XMarkIcon class="h-6 w-6" />
              </button>
              <DialogTitle as="h3" class="text-lg font-bold text-gray-900">
                Select Product for Processing
              </DialogTitle>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  Choose a product to apply specific processing rules.
                </p>
              </div>
              
              <form @submit.prevent="handleProcess" class="mt-6 space-y-6">
                <!-- File Info -->
                <div class="p-3 bg-gray-50 rounded-md">
                  <div class="text-sm">
                    <p><span class="font-medium">File:</span> {{ file?.filename }}</p>
                    <p><span class="font-medium">Type:</span> {{ fileType }}</p>
                    <p><span class="font-medium">Size:</span> {{ formatFileSize(file?.file_size) }}</p>
                  </div>
                </div>

                <!-- Product Selection -->
                <div>
                  <label for="product-select" class="block text-sm font-medium text-gray-700 mb-2">
                    Product *
                  </label>
                                  <select
                  id="product-select"
                  v-model="selectedProduct"
                  :disabled="productsLoading"
                  class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  :class="{ 'border-red-300 focus:border-red-500 focus:ring-red-500': showError }"
                >
                  <option value="">Select a product...</option>
                  <option v-for="product in products" :key="product.id" :value="product.id">
                    {{ product.name }}
                  </option>
                </select>
                  <p v-if="showError" class="mt-1 text-sm text-red-600">
                    Please select a product to continue.
                  </p>
                </div>
              </form>


              
              <!-- Action buttons -->
              <div class="mt-8 flex flex-row-reverse gap-3">
                <AppButton
                  type="button"
                  variant="primary"
                  :loading="processing"
                  :disabled="!selectedProduct || processing"
                  @click="handleProcess"
                  aria-label="Process file"
                >
                  <span v-if="processing" class="flex items-center">
                    <svg class="animate-spin h-5 w-5 mr-2 text-white" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                      <path class="opacity-75" fill="currentColor"
                        d="M4 12a8 8 0 018-8v8h8a8 8 0 01-8 8 8 8 0 01-8-8z" />
                    </svg>
                    Processing...
                  </span>
                  <span v-else>Process File</span>
                </AppButton>
                <AppButton
                  type="button"
                  variant="secondary"
                  @click="handleCancel"
                  :disabled="processing"
                  aria-label="Cancel"
                >
                  Cancel
                </AppButton>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'
import AppButton from './AppButton.vue'
import ApiService from '../services/api'

const props = defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  file: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'process'])

// State
const selectedProduct = ref('')
const productsLoading = ref(false)
const products = ref([])
const processing = ref(false)
const showError = ref(false)

// Computed
const isTextFile = computed(() => {
  return props.file?.content_type === 'text' || 
         props.file?.filename?.toLowerCase().endsWith('.txt') ||
         props.file?.filename?.toLowerCase().endsWith('.csv') ||
         props.file?.filename?.toLowerCase().endsWith('.json')
})

const fileType = computed(() => {
  if (props.file?.content_type) {
    return props.file.content_type.charAt(0).toUpperCase() + props.file.content_type.slice(1)
  }
  const filename = props.file?.filename?.toLowerCase() || ''
  if (filename.endsWith('.txt') || filename.endsWith('.csv') || filename.endsWith('.json')) {
    return 'Text'
  }
  if (filename.endsWith('.pcap') || filename.endsWith('.pcapng')) {
    return 'PCAP'
  }
  return 'Unknown'
})

// Methods
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const loadProducts = async () => {
  productsLoading.value = true
  try {
    const result = await ApiService.getProducts()
    products.value = result || []
  } catch (error) {
    console.error('Failed to load products:', error)
    products.value = []
  } finally {
    productsLoading.value = false
  }
}

const handleProcess = async () => {
  if (!selectedProduct.value) {
    showError.value = true
    return
  }

  showError.value = false
  processing.value = true

  try {
    const processOptions = {
      productId: selectedProduct.value
    }

    emit('process', processOptions)
  } catch (error) {
    console.error('Processing failed:', error)
  } finally {
    processing.value = false
  }
}

const handleCancel = () => {
  if (!processing.value) {
    emit('close')
  }
}

const resetForm = () => {
  selectedProduct.value = ''
  showError.value = false
  processing.value = false
}

// Watchers
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    resetForm()
    loadProducts()
  }
})

// Lifecycle
onMounted(() => {
  if (props.isOpen) {
    loadProducts()
  }
})
</script>

<style scoped>
.transition-all {
  transition: all 0.3s ease-in-out;
}
</style>
