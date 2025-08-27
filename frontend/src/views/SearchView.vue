<script setup>
import { ref, watch, onMounted } from 'vue'
import MainLayout from '../components/MainLayout.vue'
import ExpandableCard from '../components/ExpandableCard.vue'
import AppButton from '../components/AppButton.vue'
import InputField from '../components/InputField.vue'
import SelectField from '../components/SelectField.vue'
import ApiService from '../services/api'
import {
  CheckCircleIcon,
  DocumentDuplicateIcon,
  ArrowDownTrayIcon,
  ChevronUpDownIcon,
  ChevronUpIcon,
  ChevronDownIcon
} from '@heroicons/vue/24/outline'

// State
const searchResults = ref([])
const searchLoading = ref(false)
const searchError = ref(null)
const searchQuery = ref('')
const searchInputRef = ref(null)
const categories = ref([])
const selectedCategory = ref('')
const categoriesLoading = ref(false)
const hasMoreResults = ref(false)
const currentPage = ref(1)
const resultsPerPage = ref(20)
const sortOptions = ref([
  { value: 'created_at:desc', label: 'Newest first' },
  { value: 'created_at:asc', label: 'Oldest first' },
  { value: 'relevance:desc', label: 'Most relevant' }
])
const currentSort = ref('created_at:desc')

// Table sorting state
const tableSortColumn = ref('created_at')
const tableSortDirection = ref('desc')

// Debounce function
const debounce = (fn, delay) => {
  let timeout
  return (...args) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => fn(...args), delay)
  }
}

// Load masking data with optional search
const loadData = async (resetPagination = true) => {
  if (resetPagination) {
    currentPage.value = 1
  }

  searchLoading.value = true
  searchError.value = null

  // Store the current focus state
  const wasFocused = document.activeElement === searchInputRef.value?.$el?.querySelector('input')

  try {
    // Calculate offset based on pagination
    const offset = (currentPage.value - 1) * resultsPerPage.value

    // Prepare search params
    const params = {
      limit: resultsPerPage.value,
      offset: offset,
      sort: currentSort.value
    }

    // Add search query if present
    if (searchQuery.value.trim()) {
      params.query = searchQuery.value
    }

    // Add category filter if selected
    if (selectedCategory.value) {
      params.categories = [selectedCategory.value]
    }

    // Call the API
    const results = await ApiService.searchMaskingMaps(params)
    
    console.log('API results:', results.length, 'items')
    if (selectedCategory.value) {
      console.log('Filtered by category:', selectedCategory.value)
    }

    if (resetPagination) {
      searchResults.value = results
      console.log('Updated searchResults to:', searchResults.value.length, 'items')
    } else {
      // Append results for pagination
      searchResults.value = [...searchResults.value, ...results]
      console.log('Appended to searchResults, total:', searchResults.value.length, 'items')
    }

    // Check if there might be more results
    hasMoreResults.value = results.length === resultsPerPage.value

  } catch (err) {
    console.error('Failed to load data:', err)
    searchError.value = err.message || 'Failed to load data. Please try again.'
    searchResults.value = []
    hasMoreResults.value = false
  } finally {
    searchLoading.value = false

    // Restore focus to the input if it was focused before
    if (wasFocused) {
      // Use nextTick to ensure the DOM has updated
      setTimeout(() => {
        searchInputRef.value?.$el?.querySelector('input')?.focus()
      }, 0)
    }
  }
}

// Load more results (pagination)
const loadMore = async () => {
  if (searchLoading.value || !hasMoreResults.value) return

  currentPage.value++
  await loadData(false) // Don't reset existing results
}

// Table sorting functionality
const sortTable = (column) => {
  if (tableSortColumn.value === column) {
    // Toggle direction if same column clicked
    tableSortDirection.value = tableSortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    // Default to descending for new column
    tableSortColumn.value = column
    tableSortDirection.value = 'desc'
  }

  // Update current sort parameter for API
  currentSort.value = `${column}:${tableSortDirection.value}`
  loadData(true)
}

// Get sort icon for a column
const getSortIcon = (column) => {
  if (tableSortColumn.value !== column) {
    return ChevronUpDownIcon
  }
  return tableSortDirection.value === 'asc' ? ChevronUpIcon : ChevronDownIcon
}

// Perform search
const performSearch = () => {
  loadData(true)
}

// Debounced search function that will be called as user types
const debouncedSearch = debounce(() => loadData(true), 500)

// Watch for search query changes to trigger search
watch(searchQuery, () => {
  debouncedSearch()
})

// Watch for filter or sort changes
watch([selectedCategory], (newValues) => {
  console.log('Category changed to:', newValues[0])
  loadData(true)
}, { deep: true })

// Load categories on component mount
const loadCategories = async () => {
  categoriesLoading.value = true
  try {
    const result = await ApiService.getMaskingCategories()

    // Add an "All Categories" option at the beginning
    categories.value = [
      { value: '', label: 'All Categories' },
      ...result.map(category => ({
        value: category,
        label: category.charAt(0).toUpperCase() + category.slice(1)
      }))
    ]
  } catch (err) {
    console.error('Failed to load categories:', err)
  } finally {
    categoriesLoading.value = false
  }
}

// Format date for display
const formatDate = (dateString) => {
  if (!dateString) return 'Unknown'
  return new Date(dateString).toLocaleString()
}

// Export data
const exportData = async (item) => {
  try {
    // Call the API with responseType: 'blob' to handle binary data
    const response = await ApiService.downloadFile(item.id)

    // Get filename from item or use a default
    const filename = item.filename || `masking-data-${item.id}.csv`

    // Create a download link
    const url = window.URL.createObjectURL(new Blob([response]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();

    // Clean up
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert(`Export failed: ${err.message}`)
  }
}

// Export search results
const exportSearchResults = async () => {
  if (searchResults.value.length === 0) {
    alert('No results to export')
    return
  }

  try {
    // Prepare export params
    const params = {
      sort: currentSort.value
    }

    // Add search query if present
    if (searchQuery.value.trim()) {
      params.query = searchQuery.value
    }

    // Add category filter if selected
    if (selectedCategory.value) {
      params.categories = [selectedCategory.value]
    }

    // Call the export API with responseType: 'blob' to handle binary data
    const response = await ApiService.exportMaskingMaps(params)

    // Create a download link
    const url = window.URL.createObjectURL(new Blob([response]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'masking-data.csv');
    document.body.appendChild(link);
    link.click();

    // Clean up
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert(`Export failed: ${err.message}`)
  }
}

// Initialize component - load all data by default
onMounted(() => {
  loadCategories()
  loadData() // Load all masking data by default
})
</script>

<template>
  <MainLayout>
    <div class="min-h-screen bg-gray-50 px-4 sm:px-6 lg:px-8 py-1 sm:py-1">
      <!-- Header (Matching PresetManagement.vue and UserManagement.vue) -->
      <div class="sm:flex sm:items-center mb-8">
        <div class="sm:flex-auto">
          <div class="flex items-center gap-3">
            <svg xmlns="http://www.w3.org/2000/svg"
              class="h-7 w-7 text-indigo-500 transition-transform duration-300 hover:scale-110" fill="none"
              viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <h1 class="text-2xl font-bold text-gray-900 tracking-tight">GDPR Data Search</h1>
          </div>
          <p class="mt-2 text-sm text-gray-600 font-medium">
            Search and manage GDPR-compliant data masking records
          </p>
        </div>
        <div class="mt-6 sm:mt-0 sm:ml-16 sm:flex-none flex space-x-4">
          <AppButton v-if="searchResults.length > 0" type="button" variant="secondary" @click="exportSearchResults"
            class="inline-flex items-center justify-center rounded-lg border border-gray-200 bg-white px-5 py-2.5 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
            :preserveOriginalStyle="false" title="Export search results to CSV"
            aria-label="Export search results to CSV">
            <ArrowDownTrayIcon class="h-5 w-5 mr-2 text-gray-500" aria-hidden="true" />
            Export
          </AppButton>
          <AppButton type="button" variant="primary" @click="performSearch" :loading="searchLoading"
            class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200 disabled:bg-indigo-400"
            :preserveOriginalStyle="false" title="Perform search" aria-label="Perform search">
            <CheckCircleIcon v-if="!searchLoading" class="h-5 w-5 mr-2" aria-hidden="true" />
            {{ searchLoading ? 'Updating...' : 'Update' }}
          </AppButton>
        </div>
      </div>

      <!-- Search Form -->
      <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-8 animate-fade-in">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <InputField id="search-query" v-model="searchQuery" label="Search Query" type="text"
            placeholder="Enter search terms or patterns" :disabled="searchLoading" ref="searchInputRef"
            custom-class="border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-lg" />
          <SelectField id="categories" v-model="selectedCategory" label="Data Category"
            :disabled="searchLoading || categoriesLoading"
            custom-class="border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-lg">
            <option v-for="category in categories" :key="category.value" :value="category.value">
              {{ category.label }}
            </option>
          </SelectField>
          <SelectField id="sort" v-model="currentSort" label="Sort By" :disabled="searchLoading"
            custom-class="border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-lg">
            <option v-for="option in sortOptions" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </SelectField>
        </div>
      </div>

      <!-- Error State -->
      <div v-if="searchError"
        class="mt-6 rounded-xl bg-red-50 p-4 shadow-sm animate-fade-in flex items-center justify-between">
        <div class="flex items-center">
          <svg class="h-5 w-5 text-red-400 mr-2" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clip-rule="evenodd" />
          </svg>
          <span class="text-sm font-medium text-red-800">{{ searchError }}</span>
        </div>
        <AppButton variant="text"
          class="text-red-700 hover:text-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          @click="loadData" :preserveOriginalStyle="false" aria-label="Retry loading data">
          Retry
        </AppButton>
      </div>

      <!-- Search Results -->
      <div class="mt-8">
        <!-- Loading State -->
        <div v-if="searchLoading && !searchResults.length" class="py-8 flex justify-center items-center"
          aria-live="polite">
          <div class="animate-spin rounded-full h-12 W-12 border-t-4 border-indigo-600"></div>
          <p class="ml-4 text-sm font-medium text-gray-600">Loading data...</p>
        </div>

        <!-- Empty State -->
        <div v-if="!searchResults.length && !searchLoading" class="py-8 text-center text-gray-600 font-medium"
          aria-live="polite">
          No masking data found. Try adjusting your search or filters.
        </div>

        <!-- Results Table -->
        <div v-if="searchResults.length > 0"
          class="bg-white rounded-xl shadow-sm border border-gray-100 p-6 animate-fade-in">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col"
                    class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6 cursor-pointer"
                    @click="sortTable('category')">
                    <div class="flex items-center gap-1">
                      Category
                      <component :is="getSortIcon('category')" class="h-4 w-4 text-gray-500"></component>
                    </div>
                  </th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 cursor-pointer"
                    @click="sortTable('original_value')">
                    <div class="flex items-center gap-1">
                      Original Value
                      <component :is="getSortIcon('original_value')" class="h-4 w-4 text-gray-500"></component>
                    </div>
                  </th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 cursor-pointer"
                    @click="sortTable('masked_value')">
                    <div class="flex items-center gap-1">
                      Masked Value
                      <component :is="getSortIcon('masked_value')" class="h-4 w-4 text-gray-500"></component>
                    </div>
                  </th>
                  <th scope="col" class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 cursor-pointer"
                    @click="sortTable('created_at')">
                    <div class="flex items-center gap-1">
                      Created Date
                      <component :is="getSortIcon('created_at')" class="h-4 w-4 text-gray-500"></component>
                    </div>
                  </th>
                  <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6"
                    v-if="searchResults.some(item => item.processed)">
                    <span class="sr-only">Actions</span>
                  </th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-200">
                <tr v-for="item in searchResults" :key="item.id"
                  class="hover:bg-gray-50 transition-colors duration-200">
                  <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                    {{ item.category ? item.category.charAt(0).toUpperCase() + item.category.slice(1) : 'Unknown' }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-600">
                    {{ item.original_value || 'N/A' }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-600">
                    {{ item.masked_value || 'Not masked' }}
                  </td>
                  <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-600">
                    {{ formatDate(item.created_at) }}
                  </td>
                  <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6"
                    v-if="searchResults.some(item => item.processed)">
                    <div class="flex justify-end gap-2">
                      <AppButton v-if="item.processed" @click="exportData(item)" variant="text"
                        class="text-indigo-600 hover:text-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                        :preserveOriginalStyle="false" title="Export processed file" aria-label="Export processed file">
                        <DocumentDuplicateIcon class="h-5 w-5" aria-hidden="true" />
                      </AppButton>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Load More Button -->
        <div v-if="hasMoreResults && searchResults.length > 0" class="mt-6 text-center">
          <AppButton variant="secondary" @click="loadMore" :loading="searchLoading" :disabled="searchLoading"
            class="inline-flex items-center justify-center rounded-lg border border-gray-200 bg-white px-5 py-2.5 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
            :preserveOriginalStyle="false" aria-label="Load more results">
            Load More Results
          </AppButton>
        </div>
      </div>

      <!-- Footer Branding -->
      <footer class="mt-12 text-center text-sm text-gray-500 px-4 sm:px-16">
        © {{ new Date().getFullYear() }} GDPR Processor. All rights reserved.
        <a href="/privacy" class="text-indigo-600 hover:text-indigo-700 ml-2 transition-colors duration-200">Privacy
          Policy</a>
      </footer>
    </div>
  </MainLayout>
</template>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
</style>