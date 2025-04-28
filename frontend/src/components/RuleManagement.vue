<template>
  <Dialog as="div" class="relative z-20" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/60 transition-opacity duration-300" aria-hidden="true" />
    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-xl bg-white px-6 py-8 shadow-2xl transition-all duration-300 sm:my-8 sm:w-full sm:max-w-5xl">
          <button type="button"
            class="absolute right-4 top-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            @click="$emit('close')" aria-label="Close">
            <XMarkIcon class="h-6 w-6" />
          </button>
          <DialogTitle as="h3" class="text-lg font-semibold text-gray-900">Manage Rules</DialogTitle>
          <div v-if="error" class="mt-4 rounded-md bg-red-50 p-3 flex items-center">
            <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
            <p class="ml-2 text-sm text-red-800">{{ error }}</p>
            <button type="button" @click="error = ''" class="ml-auto text-red-500 hover:text-red-700"
              aria-label="Dismiss error">
              <XMarkIcon class="h-5 w-5" />
            </button>
          </div>
          <div class="mt-6 flex justify-between items-center">
            <p class="text-sm text-gray-500">Create and manage custom rules for your presets.</p>
            <button type="button" @click="$emit('open-rule-form')"
              class="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <PlusIcon class="h-5 w-5 mr-2" />
              Add Rule
            </button>
          </div>
          <div v-if="loading" class="flex justify-center py-6">
            <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-600"></div>
          </div>
          <div v-else class="mt-6 overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-300">
              <thead class="bg-gray-50 sticky top-0">
                <tr>
                  <th scope="col" class="py-3.5 pl-6 pr-3 text-left text-sm font-semibold text-gray-900">Name</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Category</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Type/Pattern</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-6"><span class="sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="rule in rules" :key="rule.id" class="hover:bg-gray-50 transition-all duration-200">
                  <td class="whitespace-nowrap py-4 pl-6 pr-3 text-sm font-medium text-gray-900">{{ rule.name }}</td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ rule.category }}</td>
                  <td class="px-3 py-4 text-sm text-gray-500 max-w-xs truncate">{{ rule.type === 'regex' ?
                    getPatternFromConfig(rule.config) : rule.type }}</td>
                  <td class="whitespace-nowrap py-4 pl-3 pr-6 text-right text-sm font-medium">
                    <div class="flex space-x-3 justify-end">
                      <button @click="$emit('open-rule-form', rule)" class="text-indigo-600 hover:text-indigo-900"
                        title="Edit rule" aria-label="Edit rule">
                        <PencilIcon class="h-5 w-5" />
                      </button>
                      <button @click="confirmDelete(rule)" class="text-red-600 hover:text-red-900" title="Delete rule"
                        aria-label="Delete rule">
                        <TrashIcon class="h-5 w-5" />
                      </button>
                    </div>
                  </td>
                </tr>
                <tr v-if="rules.length === 0">
                  <td colspan="4" class="py-6 text-center text-sm text-gray-500">No rules available. Add your first rule
                    to get started.</td>
                </tr>
              </tbody>
            </table>
          </div>
          <ConfirmDeleteDialog :open="showDeleteConfirm" item-type="rule" @close="showDeleteConfirm = false"
            @confirm="handleDeleteConfirm" />
        </DialogPanel>
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { ref } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { XMarkIcon, PlusIcon, PencilIcon, TrashIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'
import ConfirmDeleteDialog from './ConfirmDeleteDialog.vue'

defineProps({ open: { type: Boolean, required: true }, rules: { type: Array, required: true } })
const emit = defineEmits(['close', 'saved', 'open-rule-form'])

const error = ref('')
const loading = ref(false)
const showDeleteConfirm = ref(false)
const ruleToDelete = ref(null)

const getPatternFromConfig = (config) => config?.pattern || ''
const confirmDelete = (rule) => {
  ruleToDelete.value = rule
  showDeleteConfirm.value = true
}
const handleDeleteConfirm = async () => {
  try {
    if (!ruleToDelete.value) return
    loading.value = true
    await ApiService.deleteRule(ruleToDelete.value.id)
    emit('saved')
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
.transition-all {
  transition: all 0.3s ease-in-out;
}
</style>