<template>
  <Dialog as="div" class="relative" style="z-index: 20;" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/50 transition-opacity" @mousedown.stop style="z-index: 20;" />
    <div class="fixed inset-0 overflow-y-auto" style="z-index: 20;">
      <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-4xl sm:p-6"
        >
          <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
            <button
              type="button"
              class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              @click="$emit('close')"
            >
              <span class="sr-only">Close</span>
              <XMarkIcon class="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div>
            <div class="mt-3 text-center sm:mt-0 sm:text-left">
              <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                Manage Rules
              </DialogTitle>
              <div class="mt-4">
                <div class="flex justify-between items-center mb-4">
                  <p class="text-sm text-gray-500">Create and manage custom rules for your presets.</p>
                  <button
                    type="button"
                    @click="openCustomRuleForm()"
                    class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  >
                    <PlusIcon class="h-5 w-5 mr-2" />
                    Add Rule
                  </button>
                </div>

                <!-- Rules table -->
                <div class="mt-2 flow-root">
                  <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                    <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                      <table class="min-w-full divide-y divide-gray-300">
                        <thead>
                          <tr>
                            <th scope="col" class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-0">Name</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Category</th>
                            <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Type/Pattern</th>
                            <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-0">
                              <span class="sr-only">Actions</span>
                            </th>
                          </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-200">
                          <tr v-for="rule in rules" :key="rule.id">
                            <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-0">{{ rule.name }}</td>
                            <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ rule.category }}</td>
                            <td class="px-3 py-4 text-sm text-gray-500 max-w-xs truncate">
                              {{ rule.type === 'regex' ? getPatternFromConfig(rule.config) : rule.type }}
                            </td>
                            <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
                              <div class="flex space-x-2 justify-end">
                                <button
                                  @click="openCustomRuleForm(rule)"
                                  class="text-indigo-600 hover:text-indigo-900"
                                  title="Edit rule"
                                >
                                  <PencilIcon class="h-5 w-5" />
                                </button>
                                <button
                                  @click="confirmDelete(rule)"
                                  class="text-red-600 hover:text-red-900"
                                  title="Delete rule"
                                >
                                  <TrashIcon class="h-5 w-5" />
                                </button>
                              </div>
                            </td>
                          </tr>
                          <tr v-if="rules.length === 0">
                            <td colspan="4" class="py-4 text-center text-sm text-gray-500">
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
          </div>
        </DialogPanel>
      </div>
    </div>
  </Dialog>

  <!-- Custom Rule Form Modal -->
  <CustomRuleForm
    :open="showCustomRuleForm"
    :rule="selectedRule"
    @close="showCustomRuleForm = false"
    @saved="handleRuleSaved"
    @error="$emit('error', $event)"
  />

  <!-- Confirm Delete Dialog -->
  <ConfirmDeleteDialog
    :open="showDeleteConfirm"
    item-type="rule"
    @close="showDeleteConfirm = false"
    @confirm="handleDeleteConfirm"
  />
</template>

<script setup>
import { ref } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { XMarkIcon, PlusIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'
import CustomRuleForm from './CustomRuleForm.vue'
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

const emit = defineEmits(['close', 'rulesChanged', 'error'])

// Local state
const showCustomRuleForm = ref(false)
const showDeleteConfirm = ref(false)
const selectedRule = ref(null)
const ruleToDelete = ref(null)

// Helper function to get pattern from config
const getPatternFromConfig = (config) => {
  return config && config.pattern ? config.pattern : ''
}

// Open custom rule form
const openCustomRuleForm = (rule = null) => {
  selectedRule.value = rule
  showCustomRuleForm.value = true
}

// Confirm delete
const confirmDelete = (rule) => {
  ruleToDelete.value = rule
  showDeleteConfirm.value = true
}

// Handle rule saved
const handleRuleSaved = () => {
  emit('rulesChanged')
}

// Handle delete confirmation
const handleDeleteConfirm = async () => {
  try {
    if (ruleToDelete.value) {
      await ApiService.deleteRule(ruleToDelete.value.id)
      emit('rulesChanged')
    }
    showDeleteConfirm.value = false
    ruleToDelete.value = null
  } catch (err) {
    emit('error', `Failed to delete rule: ${err.message || 'Unknown error'}`)
  }
}
</script>
