<!--
GDPR Tool Rule Management - Rules Management Modal Component

This component provides a comprehensive interface for managing rules in the GDPR compliance tool.
It displays rules in a table format with sorting, filtering, pagination, and CRUD operations.

Key Features:
- Rules Display: Shows all rules in a sortable table format
- Rule Management: Add, edit, and delete rules
- Category Filtering: Filter rules by category
- Sorting: Sort rules by name or category
- Pagination: Navigate through large rule sets
- Search and Filter: Advanced filtering capabilities
- Confirmation Dialogs: Safe deletion with confirmation

Props:
- open: Whether the modal is open (boolean, required)

Events:
- close: Emitted when modal is closed
- saved: Emitted when rules are saved
- open-rule-form: Emitted when opening rule form (rule: object, optional)
- delete: Emitted when rule is deleted

Features:
- Rule Table: Displays rules with name, category, pattern, and patcher
- Category Filter: Filter rules by predefined categories
- Sorting: Click column headers to sort rules
- Pagination: Navigate through rule pages
- Add Rule: Button to create new rules
- Edit Rule: Edit existing rules
- Delete Rule: Delete rules with confirmation
- Loading States: Visual feedback during operations
- Error Handling: Clear error messages and retry functionality

The component provides a comprehensive interface for rule management in the
GDPR compliance tool with proper data handling and user feedback.
-->

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import AppButton from './AppButton.vue'
import SelectField from './SelectField.vue'
import { XMarkIcon, PencilIcon, TrashIcon, ExclamationCircleIcon, PlusIcon, ChevronUpIcon, ChevronDownIcon, ChevronUpDownIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'
import ConfirmDeleteDialog from './ConfirmDeleteDialog.vue'

defineProps({ open: { type: Boolean, required: true } })
const emit = defineEmits(['close', 'saved', 'open-rule-form', 'delete'])

const rules = ref([])
const error = ref('')
const loading = ref(false)
const showDeleteConfirm = ref(false)
const ruleToDelete = ref(null)
const currentPage = ref(1)
const itemsPerPage = ref(10)
const sortColumn = ref('name')
const sortDirection = ref('asc')
const filterCategory = ref('All Categories')
const totalItems = ref(0)

// Rule categories from RuleCategory enum (lowercase to match backend)
const categories = [
  'All Categories',
  'ipv4_addr',
  'mac_addr',
  'username',
  'domain',
  'phone_num'
]

// Fetch rules with pagination, sorting, and filtering
const fetchRules = async () => {
  try {
    loading.value = true
    const params = {
      limit: itemsPerPage.value,
      offset: (currentPage.value - 1) * itemsPerPage.value,
      sort: `${sortColumn.value}:${sortDirection.value}`,
    }
    // Only include category if valid (not 'All Categories' or empty)
    if (filterCategory.value && filterCategory.value !== 'All Categories') {
      params.category = filterCategory.value.toLowerCase()
    }
    const response = await ApiService.getRules(params)
    rules.value = response.data || []
    totalItems.value = response.total || 0
  } catch (err) {
    error.value = `Failed to load rules: ${err.message || err.data?.detail || 'An error occurred. Please try again.'}`
  } finally {
    loading.value = false
  }
}

// Computed properties
const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage.value))
const sortedRules = computed(() => rules.value)

// Sorting
const getSortIcon = (column) => {
  if (sortColumn.value !== column) return ChevronUpDownIcon
  return sortDirection.value === 'asc' ? ChevronUpIcon : ChevronDownIcon
}

const toggleSort = (column) => {
  if (sortColumn.value === column) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = column
    sortDirection.value = 'asc'
  }
  fetchRules()
}

// Pagination
const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    fetchRules()
  }
}

// Watch filter changes
watch(filterCategory, () => {
  currentPage.value = 1
  fetchRules()
})

// Initial fetch
fetchRules()

const getPatternFromConfig = (config) => config?.pattern || config?.type || 'N/A'
const getPatcherFromConfig = (config) => config?.patcher_cfg?.type || 'replace'

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
    await fetchRules()
  } catch (err) {
    error.value = `Failed to delete rule: ${err.message || err.data?.detail || 'Unknown error'}`
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <Dialog as="div" class="relative z-20" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/60 transition-opacity duration-300" aria-hidden="true" />
    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-xl bg-white px-6 py-8 shadow-2xl transition-all duration-300 sm:my-8 sm:w-full sm:max-w-5xl">
          <button type="button"
            class="absolute right-4 top-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            @click="$emit('close')" aria-label="Close modal">
            <XMarkIcon class="h-6 w-6" />
          </button>
          <DialogTitle as="h3" class="text-lg font-semibold text-gray-900">Manage Rules</DialogTitle>
          <div v-if="error" class="mt-4 rounded-md bg-red-50 p-3 flex items-center">
            <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
            <p class="ml-2 text-sm text-red-800">{{ error }}</p>
            <button type="button" @click="error = ''" class="ml-auto text-red-500 hover:text-red-700"
              aria-label="Dismiss error">
              <XMarkIcon class="h-6 w-6" />
            </button>
          </div>
          <div class="mt-6 flex justify-between items-center">
            <div class="flex items-center space-x-4">
              <p class="text-sm text-gray-500">Create and manage custom rules for your presets.</p>
              <SelectField id="category-filter" v-model="filterCategory" label="Filter by Category"
                class="w-48" aria-label="Filter rules by category">
                <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
              </SelectField>
            </div>
            <AppButton @click="$emit('open-rule-form')" variant="primary"
              class="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500">
              <PlusIcon class="h-5 w-5 mr-2" />
              Add Rule
            </AppButton>
          </div>
          <div v-if="loading" class="flex justify-center py-6">
            <div class="animate-spin rounded-full h-8 w-8 border-t-2 border-indigo-600"></div>
          </div>
          <div v-else class="mt-6 overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-300" role="grid" aria-label="Rules table">
              <thead class="bg-gray-50 sticky top-0">
                <tr>
                  <th scope="col" class="py-3.5 pl-6 pr-3 text-left text-sm font-semibold text-gray-900">
                    <button @click="toggleSort('name')" class="flex items-center space-x-1"
                      :aria-sort="sortColumn === 'name' ? sortDirection : 'none'">
                      <span>Name</span>
                      <component :is="getSortIcon('name')" class="h-4 w-4" />
                    </button>
                  </th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">
                    <button @click="toggleSort('category')" class="flex items-center space-x-1"
                      :aria-sort="sortColumn === 'category' ? sortDirection : 'none'">
                      <span>Category</span>
                      <component :is="getSortIcon('category')" class="h-4 w-4" />
                    </button>
                  </th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Type/Pattern</th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900">Patcher</th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-6"><span class="sr-only">Actions</span></th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200 bg-white">
                <tr v-for="rule in sortedRules" :key="rule.id" class="hover:bg-gray-50 transition-all duration-200"
                  role="row">
                  <td class="whitespace-nowrap py-4 pl-6 pr-3 text-sm font-medium text-gray-900" role="cell">
                    {{ rule.name }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500" role="cell">{{ rule.category }}</td>
                  <td class="px-3 py-4 text-sm text-gray-500 max-w-xs truncate" role="cell">
                    {{ getPatternFromConfig(rule.config) }}
                  </td>
                  <td class="px-3 py-4 text-sm text-gray-500" role="cell">{{ getPatcherFromConfig(rule.config) }}</td>
                  <td class="whitespace-nowrap py-4 pl-3 pr-6 text-right text-sm font-medium" role="cell">
                    <div class="flex space-x-3 justify-end">
                      <AppButton @click="$emit('open-rule-form', rule)" variant="text"
                        class="text-indigo-600 hover:text-indigo-900" title="Edit rule" aria-label="Edit rule">
                        <PencilIcon class="h-5 w-5" />
                      </AppButton>
                      <AppButton @click="confirmDelete(rule)" variant="text" class="text-red-600 hover:text-red-900"
                        title="Delete rule" aria-label="Delete rule">
                        <TrashIcon class="h-5 w-5" />
                      </AppButton>
                    </div>
                  </td>
                </tr>
                <tr v-if="sortedRules.length === 0">
                  <td colspan="5" class="py-6 text-center text-sm text-gray-500" role="cell">
                    No rules available. Add your first rule to get started.
                  </td>
                </tr>
              </tbody>
            </table>
            <!-- Pagination -->
            <div class="mt-4 flex justify-between items-center">
              <div class="text-sm text-gray-500">
                Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to
                {{ Math.min(currentPage * itemsPerPage, totalItems) }} of {{ totalItems }} rules
              </div>
              <div class="flex space-x-2">
                <AppButton @click="changePage(currentPage - 1)" :disabled="currentPage === 1" variant="secondary"
                  aria-label="Previous page">
                  Previous
                </AppButton>
                <AppButton @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" variant="secondary"
                  aria-label="Next page">
                  Next
                </AppButton>
              </div>
            </div>
          </div>
          <ConfirmDeleteDialog :open="showDeleteConfirm" item-type="rule" :item-name="ruleToDelete?.name"
            @close="showDeleteConfirm = false" @confirm="handleDeleteConfirm" />
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