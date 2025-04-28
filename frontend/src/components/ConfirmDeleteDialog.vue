<template>
  <Dialog as="div" class="relative z-30" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/60 transition-opacity duration-300" />
    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-xl bg-white px-6 py-8 shadow-2xl transition-all duration-300 sm:w-full sm:max-w-lg">
          <div class="flex items-center">
            <ExclamationTriangleIcon class="h-6 w-6 text-red-600" />
            <DialogTitle as="h3" class="ml-2 text-lg font-semibold text-gray-900">Confirm Delete</DialogTitle>
          </div>
          <div class="mt-4">
            <p class="text-sm text-gray-500">Are you sure you want to delete this {{ itemType }}? This action cannot be
              undone.</p>
          </div>
          <div class="mt-6 flex justify-end gap-3">
            <button type="button"
              class="inline-flex rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-gray-300 hover:bg-gray-50"
              @click="$emit('close')" :disabled="loading">Cancel</button>
            <button type="button"
              class="inline-flex rounded-md bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 disabled:bg-red-400 hover:animate-shake"
              @click="handleConfirm" :disabled="loading">
              <svg v-if="loading" class="animate-spin h-5 w-5 mr-2 text-white" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8h8a8 8 0 01-8 8 8 8 0 01-8-8z">
                </path>
              </svg>
              Delete
            </button>
          </div>
        </DialogPanel>
      </div>
    </div>
  </Dialog>
</template>

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