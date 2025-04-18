<template>
  <Dialog as="div" class="relative" style="z-index: 30;" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/50 transition-opacity" @mousedown.stop style="z-index: 30;" />
    <div class="fixed inset-0 overflow-y-auto" style="z-index: 30;">
      <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6"
        >
          <div>
            <div class="mt-3 text-center sm:mt-0 sm:text-left">
              <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                Confirm Delete
              </DialogTitle>
              <div class="mt-2">
                <p class="text-sm text-gray-500">
                  Are you sure you want to delete this {{ itemType }}? This action cannot be undone.
                </p>
              </div>
            </div>
          </div>
          <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              class="inline-flex w-full justify-center rounded-md bg-red-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-500 sm:ml-3 sm:w-auto"
              @click="handleConfirm"
              :disabled="loading"
            >
              Delete
            </button>
            <button
              type="button"
              class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
              @click="$emit('close')"
            >
              Cancel
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

defineProps({
  open: {
    type: Boolean,
    required: true
  },
  itemType: {
    type: String,
    default: 'item'
  }
})

const emit = defineEmits(['close', 'confirm'])
const loading = ref(false)

const handleConfirm = () => {
  loading.value = true
  emit('confirm')
  loading.value = false
}
</script>
