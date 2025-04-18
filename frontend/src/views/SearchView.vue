<script setup>
import { ref, watch, onMounted } from 'vue'
import MainLayout from '../components/MainLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import ExpandableCard from '../components/ExpandableCard.vue'
import AppButton from '../components/AppButton.vue'
import InputField from '../components/InputField.vue'
import SelectField from '../components/SelectField.vue'
import ApiService from '../services/api'
import {
  MagnifyingGlassIcon,
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

    if (resetPagination) {
      searchResults.value = results
    } else {
      // Append results for pagination
      searchResults.value = [...searchResults.value, ...results]
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
watch([selectedCategory], () => {
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
    <div class="px-4 sm:px-6 lg:px-8">
      <PageHeader title="GDPR Data Search" description="Search GDPR masking data">
        <template #actions>
          <div class="flex space-x-3">
            <AppButton
              v-if="searchResults.length > 0"
              type="button"
              variant="secondary"
              @click="exportSearchResults"
              class="flex flex-row items-center justify-center rounded-md border border-gray-300 px-4 py-2 text-sm font-medium"
              :preserveOriginalStyle="true"
              title="Export search results to CSV"
            >
              <template #icon-left>
                <ArrowDownTrayIcon class="h-5 w-5 mr-2 flex-shrink-0" aria-hidden="true" />
              </template>
              Export
            </AppButton>

            <AppButton
              type="button"
              variant="primary"
              @click="performSearch"
              :loading="searchLoading"
              class="flex flex-row items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto disabled:bg-indigo-300"
              :preserveOriginalStyle="true"
            >
              <template #icon-left>
                <MagnifyingGlassIcon v-if="!searchLoading" class="h-5 w-5 mr-2 flex-shrink-0" aria-hidden="true" />
              </template>
              {{ searchLoading ? 'Searching...' : 'Search' }}
            </AppButton>
          </div>
        </template>
      </PageHeader>

      <!-- Search form -->
      <ExpandableCard
        title="Search Parameters"
        :expandable="false"
      >
        <template #content>
          <div class="space-y-4">
            <div>
              <InputField
                id="search-query"
                v-model="searchQuery"
                label="Search Query"
                type="text"
                placeholder="Enter search terms or patterns"
                :disabled="searchLoading"
                ref="searchInputRef"
              />
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <SelectField
                  id="categories"
                  v-model="selectedCategory"
                  label="Data Category"
                  :disabled="searchLoading || categoriesLoading"
                >
                  <option v-for="category in categories" :key="category.value" :value="category.value">
                    {{ category.label }}
                  </option>
                </SelectField>
              </div>

              <div>
                <SelectField
                  id="sort"
                  v-model="currentSort"
                  label="Sort By"
                  :disabled="searchLoading"
                >
                  <option v-for="option in sortOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </option>
                </SelectField>
              </div>
            </div>
          </div>
        </template>
      </ExpandableCard>

      <!-- Error state -->
      <div v-if="searchError" class="mt-4 p-4 bg-red-50 text-red-700 rounded-md">
        {{ searchError }}
        <AppButton
          variant="text"
          class="ml-2 text-red-700 underline"
          @click="loadData"
        >
          Retry
        </AppButton>
      </div>

      <!-- Search results table -->
      <div class="mt-8">
        <div v-if="searchLoading && !searchResults.length" class="py-6 text-center text-gray-500">
          Loading data...
        </div>

        <div v-if="!searchResults.length && !searchLoading" class="py-6 text-center text-gray-500">
          No masking data found. Try adjusting your search or filters.
        </div>

        <div v-if="searchResults.length > 0" class="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
          <table class="min-w-full divide-y divide-gray-300">
            <thead class="bg-gray-50">
              <tr>
                <th
                  scope="col"
                  class="py-3.5 pl-4 pr-3 text-left text-sm font-semibold text-gray-900 sm:pl-6 cursor-pointer"
                  @click="sortTable('category')"
                >
                  <div class="flex items-center gap-1">
                    Category
                    <component :is="getSortIcon('category')" class="h-4 w-4" />
                  </div>
                </th>
                <th
                  scope="col"
                  class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 cursor-pointer"
                  @click="sortTable('original_value')"
                >
                  <div class="flex items-center gap-1">
                    Original Value
                    <component :is="getSortIcon('original_value')" class="h-4 w-4" />
                  </div>
                </th>
                <th
                  scope="col"
                  class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 cursor-pointer"
                  @click="sortTable('masked_value')"
                >
                  <div class="flex items-center gap-1">
                    Masked Value
                    <component :is="getSortIcon('masked_value')" class="h-4 w-4" />
                  </div>
                </th>
                <th
                  scope="col"
                  class="px-3 py-3.5 text-left text-sm font-semibold text-gray-900 cursor-pointer"
                  @click="sortTable('created_at')"
                >
                  <div class="flex items-center gap-1">
                    Created Date
                    <component :is="getSortIcon('created_at')" class="h-4 w-4" />
                  </div>
                </th>
                <th scope="col" class="relative py-3.5 pl-3 pr-4 sm:pr-6" v-if="searchResults.some(item => item.processed)">
                  <span class="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 bg-white">
              <tr v-for="item in searchResults" :key="item.id" class="hover:bg-gray-50">
                <td class="whitespace-nowrap py-4 pl-4 pr-3 text-sm font-medium text-gray-900 sm:pl-6">
                  {{ item.category ? item.category.charAt(0).toUpperCase() + item.category.slice(1) : 'Unknown' }}
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                  {{ item.original_value || 'N/A' }}
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                  {{ item.masked_value || 'Not masked' }}
                </td>
                <td class="whitespace-nowrap px-3 py-4 text-sm text-gray-500">
                  {{ formatDate(item.created_at) }}
                </td>
                <td class="relative whitespace-nowrap py-4 pl-3 pr-4 text-right text-sm font-medium sm:pr-6" v-if="searchResults.some(item => item.processed)">
                  <div class="flex justify-end gap-2">
                    <!-- Export/Copy (for processed files) -->
                    <AppButton
                      v-if="item.processed"
                      @click="exportData(item)"
                      variant="text"
                      class="text-gray-400 hover:text-indigo-600 transition-colors"
                      :preserveOriginalStyle="true"
                      title="Export processed file"
                    >
                      <template #icon-left>
                        <DocumentDuplicateIcon class="h-5 w-5 mr-2 flex-shrink-0" aria-hidden="true" />
                      </template>
                      Export
                    </AppButton>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Load more button -->
        <div v-if="hasMoreResults && searchResults.length > 0" class="mt-4 text-center">
          <AppButton
            variant="secondary"
            @click="loadMore"
            :loading="searchLoading"
            :disabled="searchLoading"
            class="px-4 py-2 text-sm"
            :preserveOriginalStyle="true"
          >
            Load More Results
          </AppButton>
        </div>
      </div>
    </div>
  </MainLayout>
</template>
