<template>
  <div>
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-gray-900">{{ $t('customers.title') }}</h1>
          <button
            @click="showAddModal = true"
            class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            {{ $t('customers.add_customer') }}
          </button>
        </div>
      </div>
    </header>

    <main>
      <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="px-4 py-6 sm:px-0">
          <!-- Search and Filters -->
          <div class="mb-6">
            <div class="flex flex-col sm:flex-row gap-4">
              <div class="flex-1">
                <input
                  v-model="searchQuery"
                  type="text"
                  :placeholder="$t('customers.search_placeholder')"
                  class="input-field"
                />
              </div>
              <div class="flex gap-2">
                <select v-model="statusFilter" class="input-field">
                  <option value="">{{ $t('customers.all_status') }}</option>
                  <option value="active">{{ $t('customers.status.active') }}</option>
                  <option value="inactive">{{ $t('customers.status.inactive') }}</option>
                </select>
                <button
                  @click="loadCustomers"
                  class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  {{ $t('common.refresh') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {{ error }}
          </div>

          <!-- Customers Table -->
          <div class="bg-white shadow overflow-hidden sm:rounded-md">
            <div v-if="loading" class="p-6 text-center">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p class="mt-2 text-gray-600">{{ $t('customers.loading') }}</p>
            </div>

            <div v-else-if="customers.length === 0" class="p-6 text-center text-gray-500">
              {{ $t('customers.no_customers_found') }}
            </div>

            <div v-else class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.name') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.email') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.phone') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('customers.tax_number') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.status') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('customers.created') }}
                    </th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.actions') }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="customer in filteredCustomers" :key="customer.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {{ customer.name }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ customer.email || '-' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ customer.phone || '-' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ customer.tax_number || '-' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="customer.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      >
                        {{ customer.is_active ? $t('customers.status.active') : $t('customers.status.inactive') }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(customer.created_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        @click="editCustomer(customer)"
                        class="text-primary-600 hover:text-primary-900 mr-3"
                      >
                        {{ $t('common.edit') }}
                      </button>
                      <button
                        @click="deleteCustomer(customer)"
                        class="text-red-600 hover:text-red-900"
                      >
                        {{ $t('common.delete') }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add/Edit Customer Modal -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ showAddModal ? $t('customers.add_customer') : $t('customers.edit_customer') }}
          </h3>

          <form @submit.prevent="saveCustomer" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('common.name') }} *</label>
              <input
                v-model="customerForm.name"
                type="text"
                required
                class="input-field mt-1"
                :placeholder="$t('customers.customer_name_placeholder')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('common.email') }}</label>
              <input
                v-model="customerForm.email"
                type="email"
                class="input-field mt-1"
                :placeholder="$t('customers.email_placeholder')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('common.phone') }}</label>
              <input
                v-model="customerForm.phone"
                type="tel"
                class="input-field mt-1"
                :placeholder="$t('customers.phone_placeholder')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('common.address') }}</label>
              <textarea
                v-model="customerForm.address"
                class="input-field mt-1"
                rows="3"
                :placeholder="$t('customers.address_placeholder')"
              ></textarea>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('customers.tax_number') }}</label>
              <input
                v-model="customerForm.tax_number"
                type="text"
                class="input-field mt-1"
                :placeholder="$t('customers.tax_number_placeholder')"
              />
            </div>

            <div>
              <label class="flex items-center">
                <input
                  v-model="customerForm.is_active"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                />
                <span class="ml-2 text-sm text-gray-700">{{ $t('customers.status.active') }}</span>
              </label>
            </div>

            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="closeModal"
                class="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md text-sm font-medium"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
              >
                {{ saving ? $t('customers.saving') : $t('common.save') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { customersAPI } from '@/services/api'

// Data
const customers = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const editingCustomer = ref(null)
const error = ref('')

const customerForm = ref({
  name: '',
  email: '',
  phone: '',
  address: '',
  tax_number: '',
  is_active: true
})

// Computed
const filteredCustomers = computed(() => {
  let filtered = customers.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(customer =>
      customer.name.toLowerCase().includes(query) ||
      (customer.email && customer.email.toLowerCase().includes(query)) ||
      (customer.phone && customer.phone.includes(query)) ||
      (customer.tax_number && customer.tax_number.includes(query))
    )
  }

  if (statusFilter.value) {
    const isActive = statusFilter.value === 'active'
    filtered = filtered.filter(customer => customer.is_active === isActive)
  }

  return filtered
})

// Methods
async function loadCustomers () {
  loading.value = true
  error.value = ''
  try {
    const response = await customersAPI.getCustomers()
    customers.value = response
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to load customers'
    console.error('Error loading customers:', err)
  } finally {
    loading.value = false
  }
}

function editCustomer (customer) {
  editingCustomer.value = customer
  customerForm.value = { ...customer }
  showEditModal.value = true
}

async function deleteCustomer (customer) {
  if (confirm(`Are you sure you want to delete ${customer.name}?`)) {
    try {
      await customersAPI.deleteCustomer(customer.id)
      customers.value = customers.value.filter(c => c.id !== customer.id)
    } catch (err) {
      error.value = err.response?.data?.detail || 'Failed to delete customer'
      console.error('Error deleting customer:', err)
    }
  }
}

async function saveCustomer () {
  saving.value = true
  error.value = ''
  try {
    if (showAddModal.value) {
      const newCustomer = await customersAPI.createCustomer(customerForm.value)
      customers.value.push(newCustomer)
    } else {
      const updatedCustomer = await customersAPI.updateCustomer(editingCustomer.value.id, customerForm.value)
      const index = customers.value.findIndex(c => c.id === editingCustomer.value.id)
      if (index !== -1) {
        customers.value[index] = updatedCustomer
      }
    }
    closeModal()
  } catch (err) {
    error.value = err.response?.data?.detail || 'Failed to save customer'
    console.error('Error saving customer:', err)
  } finally {
    saving.value = false
  }
}

function closeModal () {
  showAddModal.value = false
  showEditModal.value = false
  editingCustomer.value = null
  error.value = ''
  customerForm.value = {
    name: '',
    email: '',
    phone: '',
    address: '',
    tax_number: '',
    is_active: true
  }
}

function formatDate (dateString) {
  return new Date(dateString).toLocaleDateString('tr-TR')
}

// Lifecycle
onMounted(() => {
  loadCustomers()
})
</script>
