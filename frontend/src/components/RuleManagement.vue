<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-20" :open="open" @close="handleClose">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
        leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 bg-gray-500/50 backdrop-blur-sm transition-opacity" @click="handleClose" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel
              class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 shadow-xl sm:my-8 sm:w-full sm:max-w-4xl sm:p-6"
              @click.stop @mousedown.stop>
              <!-- Close Button -->
              <div class="absolute right-0 top-0 pr-4 pt-4">
                <button type="button"
                  class="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  @click="handleClose">
                  <span class="sr-only">Close</span>
                  <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                </button>
              </div>

              <!-- Content -->
              <DialogTitle as="h3" class="text-lg font-semibold text-gray-900">
                Manage Rules
              </DialogTitle>
              <p class="mt-1 text-sm text-gray-500">Create and manage custom rules for your presets.</p>

              <!-- Error Message -->
              <div v-if="error" class="mt-4 rounded-md bg-red-50 p-4 animate-fade-in">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <XMarkIcon class="h-5 w-5 text-red-400" />
                  </div>
                  <div class="ml-3">
                    <p class="text-sm font-medium text-red-800">{{ error }}</p>
                  </div>
                  <button @click="error = ''" class="ml-auto">
                    <XMarkIcon class="h-5 w-5 text-red-400" />
                  </button>
                </div>
              </div>

              <!-- Add Rule Button -->
              <div class="mt-4 flex justify-end">
                <button type="button" @click="openCustomRuleForm(null)"
                  class="inline-flex items-center rounded-lg border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2">
                  <PlusIcon class="h-5 w-5 mr-2" />
                  Add Rule
                </button>
              </div>

              <!-- Rules Table -->
              <div class="mt-6 flow-root">
                <div class="-my-2 -mx-4 overflow-x-auto sm:-mx-6 lg:-mx-8">
                  <div class="inline-block min-w-full py-2 align-middle sm:px-6 lg:px-8">
                    <table class="min-w-full divide-y divide-gray-300">
                      <thead>
                        <tr>
                          <th scope="col"
                            class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-0">Name</th>
                          <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Category
                          </th>
                          <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Type/Pattern
                          </th>
                          <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-0">
                            <span class="sr-only">Actions</span>
                          </th>
                        </tr>
                      </thead>
                      <tbody class="divide-y divide-gray-200 bg-white">
                        <tr v-for="rule in rules" :key="rule.id">
                          <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-0">{{
                            rule.name }}</td>
                          <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">{{ rule.category }}</td>
                          <td class="px-3 py-4 text-sm text-gray-500 max-w-xs truncate">
                            {{ rule.config?.type === 'regex' ? rule.config.pattern : rule.config?.type || 'N/A' }}
                          </td>
                          <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-0">
                            <div class="flex space-x-2 justify-end">
                              <button @click="openCustomRuleForm(rule)" class="text-indigo-600 hover:text-indigo-900"
                                title="Edit rule">
                                <PencilIcon class="h-5 w-5" />
                              </button>
                              <button @click="confirmDelete(rule)" class="text-red-600 hover:text-red-900"
                                title="Delete rule">
                                <TrashIcon class="h-5 w-5" />
                              </button>
                            </div>
                          </td>
                        </tr>
                        <tr v-if="rules.length === 0">
                          <td colspan="4" class="py-4 text-center text-sm text-gray-500">
                            No rules available. Add a rule to get started.
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>

  <!-- Confirm Delete Dialog -->
  <ConfirmDeleteDialog :open="showDeleteConfirm" item-type="rule" @close="showDeleteConfirm = false"
    @confirm="handleDeleteConfirm" />
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { XMarkIcon, PlusIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'
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

const emit = defineEmits(['close', 'saved', 'delete', 'open-rule-form'])

// Local state
const showDeleteConfirm = ref(false)
const ruleToDelete = ref(null)
const error = ref('')
const isClosing = ref(false)

// Open custom rule form
const openCustomRuleForm = (rule = null) => {
  console.log('RuleManagement: Emitting open-rule-form, rule:', rule)
  emit('open-rule-form', rule)
}

// Handle modal close
const handleClose = async () => {
  if (isClosing.value) return
  isClosing.value = true
  console.log('RuleManagement: Closing modal')

  // Close nested modals
  showDeleteConfirm.value = false
  ruleToDelete.value = null
  error.value = ''

  // Wait for DOM updates
  await nextTick()

  // Delay emission to ensure Vue's update cycle finishes
  setTimeout(() => {
    emit('close')
    isClosing.value = false
  }, 100)
}

// Handle rule saved
const handleRuleSaved = () => {
  console.log('RuleManagement: Rule saved, refreshing rules')
  error.value = ''
  emit('saved')
}

// Confirm delete
const confirmDelete = (rule) => {
  console.log('RuleManagement: Confirming delete for rule:', rule)
  ruleToDelete.value = rule
  showDeleteConfirm.value = true
}

// Handle delete confirmation
const handleDeleteConfirm = async () => {
  try {
    if (ruleToDelete.value) {
      console.log('RuleManagement: Deleting rule:', ruleToDelete.value.id)
      await ApiService.deleteRule(ruleToDelete.value.id)
      emit('saved') // Refresh rules after deletion
      emit('delete', ruleToDelete.value) // Trigger confirmDelete in PresetsView
    }
  } catch (err) {
    error.value = `Failed to delete rule: ${err.message || 'Unknown error'}`
  } finally {
    showDeleteConfirm.value = false
    ruleToDelete.value = null
  }
}
</script>