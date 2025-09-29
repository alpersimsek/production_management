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
import { ref, computed, watch, onMounted } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import AppButton from './AppButton.vue'
import CustomSelect from './CustomSelect.vue'
import InputField from './InputField.vue'
import { XMarkIcon, PencilIcon, TrashIcon, ExclamationCircleIcon, PlusIcon, ChevronUpIcon, ChevronDownIcon, ChevronUpDownIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'
import ConfirmDeleteDialog from './ConfirmDeleteDialog.vue'

const props = defineProps({ open: { type: Boolean, required: true } })
const emit = defineEmits(['close', 'saved', 'open-rule-form', 'delete'])

const rules = ref([])
const error = ref('')
const loading = ref(false)
const showDeleteConfirm = ref(false)
const ruleToDelete = ref(null)
const currentPage = ref(1)
const itemsPerPage = ref(3)
const sortColumn = ref('name')
const sortDirection = ref('asc')
const categories = ref(['All Categories', 'IPV4_ADDR', 'MAC_ADDR', 'USERNAME', 'DOMAIN', 'PHONE_NUM'])
const filterCategory = ref('All Categories')
const searchQuery = ref('')
const totalItems = ref(0)


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
      // Convert uppercase category to lowercase enum value
      params.category = filterCategory.value.toLowerCase()
    }
    // Add search query if provided
    if (searchQuery.value && searchQuery.value.trim()) {
      params.search = searchQuery.value.trim()
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

// Watch for modal opening to fetch rules
watch(() => props.open, (isOpen) => {
  if (isOpen) {
    fetchRules()
  }
})

// Watch category filter changes
watch(filterCategory, () => {
  currentPage.value = 1
  fetchRules()
})

// Watch search query changes with debounce
let searchTimeout = null
watch(searchQuery, () => {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    fetchRules()
  }, 300) // 300ms debounce
})

// Fetch rules on component mount
onMounted(() => {
  if (props.open) {
    fetchRules()
  }
})

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
  <Dialog as="div" class="relative z-[60]" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/60 transition-opacity duration-300" aria-hidden="true" />
    <div class="fixed inset-0 overflow-y-auto">
      <div class="flex min-h-full items-center justify-center p-2 sm:p-4 pt-20 sm:pt-4">
        <DialogPanel
          class="relative transform overflow-hidden rounded-2xl bg-white/90 backdrop-blur-sm border border-slate-200/60 px-4 py-6 sm:px-6 sm:py-8 shadow-2xl transition-all duration-300 sm:my-8 w-full max-w-5xl max-h-[95vh] sm:max-h-[90vh] flex flex-col">
          <button type="button"
            class="absolute right-4 top-4 text-slate-400 hover:text-slate-600 focus:outline-none focus:ring-2 focus:ring-gray-400 rounded-lg p-1 transition-all duration-200"
            @click="$emit('close')" aria-label="Close modal">
            <XMarkIcon class="h-6 w-6" />
          </button>
          <DialogTitle as="h3" class="text-xl sm:text-2xl font-bold text-slate-900">Manage Rules</DialogTitle>
          <p class="mt-2 text-sm text-slate-600">View, create, edit, and delete masking rules used in presets for GDPR compliance</p>
          <div v-if="error" class="mt-4 rounded-2xl bg-red-50/80 backdrop-blur-sm border border-red-200/60 p-3 sm:p-4 flex items-center">
            <ExclamationCircleIcon class="h-5 w-5 text-red-400 flex-shrink-0" />
            <p class="ml-2 text-sm text-red-800 flex-1">{{ error }}</p>
            <button type="button" @click="error = ''" class="ml-auto text-red-500 hover:text-red-700 rounded-lg p-1 transition-all duration-200 flex-shrink-0"
              aria-label="Dismiss error">
              <XMarkIcon class="h-6 w-6" />
            </button>
          </div>
          <div class="mt-4 sm:mt-6 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 sm:gap-0">
            <div class="flex items-center">
              <p class="text-sm text-slate-600">Rules define patterns for detecting and masking sensitive data in files</p>
            </div>
            <div class="flex justify-end sm:justify-start">
              <AppButton @click="$emit('open-rule-form')" variant="primary"
                class="inline-flex items-center rounded-2xl bg-gradient-to-r from-gray-500 to-slate-600 px-3 py-2 sm:px-4 text-sm font-semibold text-white shadow-sm hover:from-gray-600 hover:to-slate-700 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200">
                <PlusIcon class="h-4 w-4 sm:h-5 sm:w-5 mr-1 sm:mr-2" />
                <span class="hidden sm:inline">Add Rule</span>
                <span class="sm:hidden">Add</span>
              </AppButton>
            </div>
          </div>
          <div class="mt-4 flex flex-col sm:flex-row sm:items-end gap-3 sm:gap-4">
            <div class="flex-1 sm:flex-none sm:w-48">
              <CustomSelect
                v-model="filterCategory"
                :options="categories.map(cat => ({ value: cat, label: cat }))"
                label="Filter by Category"
                placeholder="Select category"
              />
            </div>
            <div class="flex-1">
              <InputField
                v-model="searchQuery"
                placeholder="Search rules by name or pattern..."
                class="w-full"
              >
                <template #prefix>
                  <MagnifyingGlassIcon class="h-5 w-5 text-gray-400" />
                </template>
              </InputField>
            </div>
          </div>
          <div v-if="loading" class="flex justify-center py-6">
            <div class="animate-spin rounded-full h-8 w-8 border-2 border-gray-400/60 border-t-transparent"></div>
            <p class="ml-4 text-sm font-medium text-slate-600">Loading rules...</p>
          </div>
          <div v-else class="mt-4 sm:mt-6 flex-1 overflow-hidden rounded-2xl border border-slate-200/60 flex flex-col">
            <div class="overflow-x-auto flex-1">
              <table class="min-w-full divide-y divide-slate-200/60" role="grid" aria-label="Rules table">
                <thead class="bg-slate-50/60 backdrop-blur-sm sticky top-0">
                  <tr>
                    <th scope="col" class="py-3 pl-3 sm:pl-6 pr-3 text-left text-xs sm:text-sm font-semibold text-slate-900 min-w-[120px]">
                      <button @click="toggleSort('name')" class="flex items-center space-x-1 hover:bg-slate-100/60 rounded-lg p-1 -m-1 transition-colors duration-200"
                        :aria-sort="sortColumn === 'name' ? sortDirection : 'none'">
                        <span>Name</span>
                        <component :is="getSortIcon('name')" class="h-3 w-3 sm:h-4 sm:w-4" />
                      </button>
                    </th>
                    <th scope="col" class="px-3 py-3 text-left text-xs sm:text-sm font-semibold text-slate-900 min-w-[100px]">
                      <button @click="toggleSort('category')" class="flex items-center space-x-1 hover:bg-slate-100/60 rounded-lg p-1 -m-1 transition-colors duration-200"
                        :aria-sort="sortColumn === 'category' ? sortDirection : 'none'">
                        <span>Category</span>
                        <component :is="getSortIcon('category')" class="h-3 w-3 sm:h-4 sm:w-4" />
                      </button>
                    </th>
                    <th scope="col" class="px-3 py-3 text-left text-xs sm:text-sm font-semibold text-slate-900 min-w-[150px]">Type/Pattern</th>
                    <th scope="col" class="px-3 py-3 text-left text-xs sm:text-sm font-semibold text-slate-900 min-w-[80px]">Patcher</th>
                    <th scope="col" class="relative py-3 pl-3 pr-3 sm:pr-6 min-w-[80px]"><span class="sr-only">Actions</span></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-slate-200/60 bg-white/80 backdrop-blur-sm">
                  <tr v-for="rule in sortedRules" :key="rule.id" class="hover:bg-slate-50/60 transition-all duration-200"
                    role="row">
                    <td class="whitespace-nowrap py-3 sm:py-4 pl-3 sm:pl-6 pr-3 text-xs sm:text-sm font-medium text-slate-900" role="cell">
                      {{ rule.name }}
                    </td>
                    <td class="whitespace-nowrap px-3 py-3 sm:py-4 text-xs sm:text-sm text-slate-600" role="cell">{{ rule.category }}</td>
                    <td class="px-3 py-3 sm:py-4 text-xs sm:text-sm text-slate-600 max-w-xs sm:max-w-md" role="cell">
                      <div class="break-all whitespace-normal">
                        {{ getPatternFromConfig(rule.config) }}
                      </div>
                    </td>
                    <td class="px-3 py-3 sm:py-4 text-xs sm:text-sm text-slate-600" role="cell">{{ getPatcherFromConfig(rule.config) }}</td>
                    <td class="whitespace-nowrap py-3 sm:py-4 pl-3 pr-3 sm:pr-6 text-right text-xs sm:text-sm font-medium" role="cell">
                      <div class="flex space-x-1 sm:space-x-2 justify-end">
                        <AppButton @click="$emit('open-rule-form', rule)" variant="text"
                          class="text-gray-600 hover:text-gray-800 hover:scale-105 transition-all duration-200" title="Edit rule" aria-label="Edit rule">
                          <PencilIcon class="h-4 w-4 sm:h-5 sm:w-5" />
                        </AppButton>
                        <AppButton @click="confirmDelete(rule)" variant="text" class="text-red-600 hover:text-red-800 hover:scale-105 transition-all duration-200"
                          title="Delete rule" aria-label="Delete rule">
                          <TrashIcon class="h-4 w-4 sm:h-5 sm:w-5" />
                        </AppButton>
                      </div>
                    </td>
                  </tr>
                  <tr v-if="sortedRules.length === 0">
                    <td colspan="5" class="py-6 sm:py-8 text-center text-xs sm:text-sm text-slate-600" role="cell">
                      <div class="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-3 sm:mb-4 bg-slate-100/60 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                        <MagnifyingGlassIcon class="h-6 w-6 sm:h-8 sm:w-8 text-slate-400" />
                      </div>
                      <span class="hidden sm:inline">No rules available. Add your first rule to get started.</span>
                      <span class="sm:hidden">No rules available.</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <!-- Pagination -->
            <div class="mt-2 sm:mt-4 flex flex-col sm:flex-row sm:justify-between sm:items-center gap-3 sm:gap-0 px-3 sm:px-6 py-3 sm:py-4 bg-slate-50/60 backdrop-blur-sm">
              <div class="text-xs sm:text-sm text-slate-600 text-center sm:text-left">
                Showing {{ (currentPage - 1) * itemsPerPage + 1 }} to
                {{ Math.min(currentPage * itemsPerPage, totalItems) }} of {{ totalItems }} rules
              </div>
              <div class="flex justify-center sm:justify-end space-x-2">
                <AppButton @click="changePage(currentPage - 1)" :disabled="currentPage === 1" variant="secondary"
                  class="rounded-2xl border border-gray-200/60 bg-white/80 backdrop-blur-sm px-3 py-2 sm:px-4 text-xs sm:text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-100/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
                  aria-label="Previous page">
                  <span class="hidden sm:inline">Previous</span>
                  <span class="sm:hidden">Prev</span>
                </AppButton>
                <AppButton @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" variant="secondary"
                  class="rounded-2xl border border-gray-200/60 bg-white/80 backdrop-blur-sm px-3 py-2 sm:px-4 text-xs sm:text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-100/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
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