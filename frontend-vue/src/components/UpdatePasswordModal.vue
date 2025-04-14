<script setup>
import { ref } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { XMarkIcon } from '@heroicons/vue/24/outline'

defineProps({
  isOpen: Boolean,
  username: String,
})

const emit = defineEmits(['close', 'submit'])

const password = ref('')
const confirmPassword = ref('')
const error = ref('')

const handleSubmit = () => {
  if (!password.value || !confirmPassword.value) {
    error.value = 'Please fill in all fields'
    return
  }

  if (password.value !== confirmPassword.value) {
    error.value = 'Passwords do not match'
    return
  }

  emit('submit', {
    password: password.value,
  })

  // Reset form
  password.value = ''
  confirmPassword.value = ''
  error.value = ''
}
</script>

<template>
  <Dialog as="div" class="relative z-10" @close="emit('close')" :open="isOpen">
    <div class="fixed inset-0 bg-gray-500/50 backdrop-blur-[2px] transition-opacity" />

    <div class="fixed inset-0 z-10 overflow-y-auto">
      <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6"
        >
          <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
            <button
              type="button"
              class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none"
              @click="emit('close')"
            >
              <span class="sr-only">Close</span>
              <XMarkIcon class="h-6 w-6" aria-hidden="true" />
            </button>
          </div>

          <div class="sm:flex sm:items-start">
            <div class="mt-3 text-center sm:mt-0 sm:text-left w-full">
              <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                Update Password for {{ username }}
              </DialogTitle>

              <div class="mt-4">
                <form @submit.prevent="handleSubmit" class="space-y-4">
                  <div>
                    <label for="password" class="block text-sm font-medium text-gray-700">
                      New Password
                    </label>
                    <input
                      type="password"
                      id="password"
                      v-model="password"
                      class="mt-1 block w-full rounded-md border-gray-300 py-3 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    />
                  </div>

                  <div>
                    <label for="confirmPassword" class="block text-sm font-medium text-gray-700">
                      Confirm Password
                    </label>
                    <input
                      type="password"
                      id="confirmPassword"
                      v-model="confirmPassword"
                      class="mt-1 block w-full rounded-md border-gray-300 py-3 shadow-sm focus:border-primary focus:ring-primary sm:text-sm"
                    />
                  </div>

                  <div v-if="error" class="text-red-600 text-sm text-center">
                    {{ error }}
                  </div>

                  <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                    <button
                      type="submit"
                      class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 sm:ml-3 sm:w-auto"
                    >
                      Update Password
                    </button>
                    <button
                      type="button"
                      class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
                      @click="emit('close')"
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        </DialogPanel>
      </div>
    </div>
  </Dialog>
</template>
