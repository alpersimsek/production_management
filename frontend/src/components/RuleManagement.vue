<template>
  <Dialog as="div" class="relative z-20" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/50 transition-opacity duration-300" aria-hidden="true" />
    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 shadow-xl transition-all duration-300 sm:my-8 sm:w-full sm:max-w-4xl sm:p-6">
          <!-- Close Button -->
          <div class="absolute right-0 top-0 pr-4 pt-4">
            <button type="button"
              class="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              @click="$emit('close')" aria-label="Close">
              <XMarkIcon class="h-6 w-6" aria-hidden="true" />
            </button>
          </div>

          <!-- Content -->
          <div>
            <DialogTitle as="h3" class="text-lg font-semibold text-gray-900">Manage Rules</DialogTitle>
            <div class="mt-4">
              <!-- Error Message -->
              <div v-if="error" class="mb-4 rounded-md bg-red-50 p-3">
                <div class="flex items-center">
                  <ExclamationCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
                  <p class="ml-2 text-sm text-red-800">{{ error }}</p>
                  <button type="button" @click="error = ''" class="ml-auto text-red-500 hover:text-red-700"
                    aria-label="Dismiss error">
                    <XMarkIcon class="h-5 w-5" />
                  </button>
                </div>
              </div>

              <!-- Header -->
              <div class="flex justify-between items-center mb-6">
                <p class="text-sm text-gray-500">Create and manage custom rules for your presets.</p>
                <button type="button" @click="$emit('open-rule-form')"
                  class="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                  <PlusIcon class="h-5 w-5 mr-2" aria-hidden="true" />
                  Add Rule
                </button>
              </div>

              <!-- Rules Table -->
              <div v-if="loading" class="flex justify-center py-4">
                <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-600"></div>
              </div>
              <div v-else class="flow-root">
                <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                  <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                    <table class="min-w-full divide-y divide-gray-300">
                      <thead>
                        <tr>
                          <th scope="col"
                            class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6">Name</th>
                          <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Category
                          </th>
                          <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Type/Pattern
                          </th>
                          <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6">
                            <span class="sr-only">Actions</span>
                          </th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-gray-200 bg-white">
                        <tr v-for="rule in rules" :key="rule.id" class="hover:bg-gray-50 transition-colors">
                          <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">{{
                            rule.name }}</td>
                          <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ rule.category }}</td>
                          <td class="px-3 py-4 text-sm text-gray-500 max-w-xs truncate">
                            {{ rule.type === 'regex' ? getPatternFromConfig(rule.config) : rule.type }}
                          </td>
                          <td class="whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6">
                            <div class="flex space-x-3 justify-end">
                              <button @click="$emit('open-rule-form', rule)"
                                class="text-indigo-600 hover:text-indigo-900" title="Edit rule" aria-label="Edit rule">
                                <PencilIcon class="h-5 w-5" />
                              </button>
                              <button @click="confirmDelete(rule)" class="text-red-600 hover:text-red-900"
                                title="Delete rule" aria-label="Delete rule">
                                <TrashIcon class="h-5 w-5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                        <tr v-if="rules.length === 0">
                          <td colspan="4" class="py-6 text-center text-sm text-gray-500">
                            No rules available. Add your first rule to get started.
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </DialogPanel>
      </div>
    </div>

    <!-- Confirm Delete Dialog -->
    <ConfirmDeleteDialog :open="showDeleteConfirm" item-type="rule" @close="showDeleteConfirm = false"
      @confirm="handleDeleteConfirm" />
  </Dialog>
</template>

<script setup>
import { ref } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { XMarkIcon, PlusIcon, PencilIcon, TrashIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'
import ConfirmDeleteDialog from './ConfirmDeleteDialog.vue'

defineProps({
  open: {
    type: Boolean,
    required: true
  },
  rules: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['close', 'saved', 'open-rule-form'])

const error = ref('') // Track errors for display
const loading = ref(false) // Track loading state for delete operations
const showDeleteConfirm = ref(false)
const ruleToDelete = ref(null)

// Helper function to extract pattern from config
const getPatternFromConfig = (config) => {
  return config?.pattern || ''
}

// Open custom rule form by emitting to parent
const confirmDelete = (rule) => {
  ruleToDelete.value = rule
  showDeleteConfirm.value = true
}

// Handle delete confirmation
const handleDeleteConfirm = async () => {
  try {
    if (!ruleToDelete.value) return
    loading.value = true
    await ApiService.deleteRule(ruleToDelete.value.id)
    emit('saved') // Notify parent to refresh rules
    showDeleteConfirm.value = false
    ruleToDelete.value = null
  } catch (err) {
    error.value = `Failed to delete rule: ${err.message || 'Unknown error'}`
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* Smooth transitions for modal */
.transition-all {
  transition: all 0.3s ease-in-out;
}

/* Hover effects for table rows */
tbody tr:hover {
  background-color: #f9fafb;
}
</style>