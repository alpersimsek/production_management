<template>
  <div>
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-gray-900">{{ $t('orders.title') }}</h1>
          <button
            @click="showAddModal = true"
            class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            {{ $t('orders.new_order') }}
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
                  :placeholder="$t('orders.search_placeholder')"
                  class="input-field"
                />
              </div>
              <div class="flex gap-2">
                <select v-model="statusFilter" class="input-field">
                  <option value="">{{ $t('orders.all_status') }}</option>
                  <option value="pending">{{ $t('orders.status.pending') }}</option>
                  <option value="confirmed">{{ $t('orders.status.confirmed') }}</option>
                  <option value="in_production">{{ $t('orders.status.in_production') }}</option>
                  <option value="completed">{{ $t('orders.status.completed') }}</option>
                  <option value="shipped">{{ $t('orders.status.shipped') }}</option>
                  <option value="delivered">{{ $t('orders.status.delivered') }}</option>
                  <option value="cancelled">{{ $t('orders.status.cancelled') }}</option>
                </select>
                <select v-model="customerFilter" class="input-field">
                  <option value="">{{ $t('orders.all_customers') }}</option>
                  <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                    {{ customer.name }}
                  </option>
                </select>
                <button
                  @click="loadOrders"
                  class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  {{ $t('common.refresh') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Orders Table -->
          <div class="bg-white shadow overflow-hidden sm:rounded-md">
            <div v-if="loading" class="p-6 text-center">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p class="mt-2 text-gray-600">{{ $t('orders.loading') }}</p>
            </div>

            <div v-else-if="orders.length === 0" class="p-6 text-center text-gray-500">
              {{ $t('orders.no_orders_found') }}
            </div>

            <div v-else class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('orders.order_number') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('orders.customer') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('orders.due_date') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.status') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('orders.total_amount') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('orders.items') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('orders.created') }}
                    </th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.actions') }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="order in filteredOrders" :key="order.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {{ order.order_number }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ order.customer_name || $t('orders.unknown_customer') }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm">
                      <span :class="getDueDateColor(order.due_date, order.status)">
                        {{ formatDate(order.due_date) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="getStatusColor(order.status)"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      >
                        {{ $t(`orders.status.${order.status}`) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ formatCurrency(order.total_amount || 0) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ order.items_count || 0 }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(order.created_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        @click="viewOrder(order)"
                        class="text-blue-600 hover:text-blue-900 mr-3"
                      >
                      {{ $t('common.view') }}
                      </button>
                      <button
                        @click="editOrder(order)"
                        class="text-primary-600 hover:text-primary-900 mr-3"
                      >
                        {{ $t('common.edit') }}
                      </button>
                      <button
                        v-if="order.status === 'pending'"
                        @click="confirmOrder(order)"
                        class="text-green-600 hover:text-green-900 mr-3"
                      >
                        {{ $t('orders.confirm') }}
                      </button>
                      <button
                        v-if="order.status !== 'cancelled' && order.status !== 'delivered'"
                        @click="cancelOrder(order)"
                        class="text-red-600 hover:text-red-900 mr-3"
                      >
                        {{ $t('orders.cancel') }}
                      </button>
                      <button
                        @click="deleteOrder(order)"
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

          <!-- Pagination -->
          <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4">
            <div class="flex-1 flex justify-between sm:hidden">
              <button
                @click="previousPage"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                {{ $t('common.previous') }}
              </button>
              <button
                @click="nextPage"
                :disabled="currentPage === totalPages"
                class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                {{ $t('common.next') }}
              </button>
            </div>
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p class="text-sm text-gray-700">
                  {{ $t('common.showing') }}
                  <span class="font-medium">{{ (currentPage - 1) * itemsPerPage + 1 }}</span>
                  {{ $t('common.to') }}
                  <span class="font-medium">{{ Math.min(currentPage * itemsPerPage, totalOrders) }}</span>
                  {{ $t('common.of') }}
                  <span class="font-medium">{{ totalOrders }}</span>
                  {{ $t('common.results') }}
                </p>
              </div>
              <div>
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    @click="previousPage"
                    :disabled="currentPage === 1"
                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
                  </button>
                  <button
                    v-for="page in visiblePages"
                    :key="page"
                    @click="goToPage(page)"
                    :class="[
                      'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                      page === currentPage
                        ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                    ]"
                  >
                    {{ page }}
                  </button>
                  <button
                    @click="nextPage"
                    :disabled="currentPage === totalPages"
                    class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add/Edit Order Modal -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ showAddModal ? $t('orders.new_order') : $t('orders.edit_order') }}
            </h3>
            <button
              @click="closeModal"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <form @submit.prevent="saveOrder" class="space-y-6">
            <!-- Order Basic Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('orders.customer') }} *</label>
                <select v-model="orderForm.customer_id" required class="input-field mt-1">
                  <option value="">{{ $t('orders.select_customer') }}</option>
                  <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                    {{ customer.name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('orders.due_date') }} *</label>
                <input
                  v-model="orderForm.due_date"
                  type="date"
                  required
                  class="input-field mt-1"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('common.status') }}</label>
                <select v-model="orderForm.status" class="input-field mt-1">
                  <option value="pending">{{ $t('orders.status.pending') }}</option>
                  <option value="confirmed">{{ $t('orders.status.confirmed') }}</option>
                  <option value="in_production">{{ $t('orders.status.in_production') }}</option>
                  <option value="completed">{{ $t('orders.status.completed') }}</option>
                  <option value="shipped">{{ $t('orders.status.shipped') }}</option>
                  <option value="delivered">{{ $t('orders.status.delivered') }}</option>
                  <option value="cancelled">{{ $t('orders.status.cancelled') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('orders.total_amount') }}</label>
                <input
                  v-model.number="orderForm.total_amount"
                  type="number"
                  step="0.01"
                  class="input-field mt-1"
                  placeholder="0.00"
                />
              </div>
            </div>

            <!-- Order Items -->
            <div>
              <div class="flex justify-between items-center mb-4">
                <h4 class="text-md font-medium text-gray-900">{{ $t('orders.order_items') }}</h4>
                <button
                  type="button"
                  @click="addOrderItem"
                  class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded-md text-sm"
                >
                  {{ $t('orders.add_item') }}
                </button>
              </div>

              <div class="space-y-4">
                <div
                  v-for="(item, index) in orderForm.items"
                  :key="index"
                  class="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 border rounded-lg"
                >
                  <div>
                    <label class="block text-sm font-medium text-gray-700">{{ $t('orders.product') }}</label>
                    <select v-model="item.product_id" class="input-field mt-1">
                      <option value="">{{ $t('orders.select_product') }}</option>
                      <option v-for="product in products" :key="product.id" :value="product.id">
                        {{ product.name }} ({{ product.code }})
                      </option>
                    </select>
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700">{{ $t('common.quantity') }}</label>
                    <input
                      v-model.number="item.quantity"
                      type="number"
                      min="0"
                      step="0.01"
                      class="input-field mt-1"
                      placeholder="0"
                    />
                  </div>

                  <div>
                    <label class="block text-sm font-medium text-gray-700">{{ $t('orders.unit_price') }}</label>
                    <input
                      v-model.number="item.unit_price"
                      type="number"
                      min="0"
                      step="0.01"
                      class="input-field mt-1"
                      placeholder="0.00"
                    />
                  </div>

                  <div class="flex items-end">
                    <button
                      type="button"
                      @click="removeOrderItem(index)"
                      class="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-md text-sm"
                    >
                      {{ $t('orders.remove') }}
                    </button>
                  </div>
                </div>
              </div>

              <div class="mt-4 p-4 bg-gray-50 rounded-lg">
                <div class="flex justify-between items-center">
                  <span class="text-lg font-medium text-gray-900">{{ $t('common.total') }}:</span>
                  <span class="text-lg font-bold text-gray-900">{{ formatCurrency(orderTotal) }}</span>
                </div>
              </div>
            </div>

            <!-- Notes -->
            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('common.notes') }}</label>
              <textarea
                v-model="orderForm.notes"
                class="input-field mt-1"
                rows="3"
                :placeholder="$t('orders.order_notes_placeholder')"
              ></textarea>
            </div>

            <!-- Actions -->
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
                {{ saving ? $t('orders.saving') : $t('orders.save_order') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Order Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ $t('orders.order_details') }} - {{ selectedOrder?.order_number }}
            </h3>
            <button
              @click="showDetailsModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div v-if="selectedOrder" class="space-y-6">
            <!-- Order Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('orders.order_information') }}</h4>
                <dl class="space-y-2">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('orders.order_number') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedOrder.order_number }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('orders.customer') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedOrder.customer_name || $t('orders.unknown_customer') }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('orders.due_date') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ formatDate(selectedOrder.due_date) }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('orders.total_amount') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ formatCurrency(selectedOrder.total_amount || 0) }}</dd>
                  </div>
                </dl>
              </div>

              <div>
                <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('orders.status_progress') }}</h4>
                <dl class="space-y-2">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('common.status') }}:</dt>
                    <dd class="text-sm">
                      <span :class="getStatusColor(selectedOrder.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                        {{ $t(`orders.status.${selectedOrder.status}`) }}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('orders.items_count') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedOrder.items_count || 0 }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('orders.created') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ formatDate(selectedOrder.created_at) }}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <!-- Order Items -->
            <div v-if="selectedOrder.items && selectedOrder.items.length > 0">
              <h4 class="text-md font-medium text-gray-900 mb-4">Order Items</h4>
              <div class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unit Price</th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Total</th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="item in selectedOrder.items" :key="item.id">
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ item.product_name }}</td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ item.quantity }}</td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatCurrency(item.unit_price) }}</td>
                      <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatCurrency(item.quantity * item.unit_price) }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Notes -->
            <div v-if="selectedOrder.notes">
              <h4 class="text-md font-medium text-gray-900 mb-2">Notes</h4>
              <p class="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">{{ selectedOrder.notes }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { ordersAPI, customersAPI, productsAPI } from '@/services/api'

// Data
const orders = ref([])
const customers = ref([])
const products = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const customerFilter = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showDetailsModal = ref(false)
const editingOrder = ref(null)
const selectedOrder = ref(null)

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(10)
const totalOrders = ref(0)

const orderForm = ref({
  customer_id: '',
  due_date: '',
  status: 'pending',
  total_amount: 0,
  notes: '',
  items: [{ product_id: '', quantity: 0, unit_price: 0 }]
})

// Computed
const filteredOrders = computed(() => {
  let filtered = orders.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(order =>
      order.order_number.toLowerCase().includes(query) ||
      (order.customer_name && order.customer_name.toLowerCase().includes(query))
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(order => order.status === statusFilter.value)
  }

  if (customerFilter.value) {
    filtered = filtered.filter(order => order.customer_id === parseInt(customerFilter.value))
  }

  return filtered
})

const totalPages = computed(() => Math.ceil(totalOrders.value / itemsPerPage.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

const orderTotal = computed(() => {
  return orderForm.value.items.reduce((total, item) => {
    return total + (item.quantity * item.unit_price)
  }, 0)
})

// Methods
function getStatusColor (status) {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    confirmed: 'bg-blue-100 text-blue-800',
    in_production: 'bg-purple-100 text-purple-800',
    completed: 'bg-green-100 text-green-800',
    shipped: 'bg-indigo-100 text-indigo-800',
    delivered: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

function getDueDateColor (dueDate, status) {
  const today = new Date()
  const due = new Date(dueDate)
  const diffTime = due - today
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))

  // Durum bazlı renk kodlaması
  if (status === 'delivered') {
    return 'text-green-600 font-semibold' // 🟢 Teslim edildi
  }

  if (status === 'shipped' || status === 'completed') {
    return 'text-blue-600 font-semibold' // 🔵 Teslim edilmek üzere hazır
  }

  // Gün bazlı renk kodlaması
  if (diffDays < 0) {
    return 'text-red-600 font-semibold' // 🔴 Gecikmiş
  }

  if (diffDays <= 7) {
    return 'text-red-600 font-semibold' // 🔴 < 7 gün kala
  }

  if (diffDays >= 8 && diffDays <= 15) {
    return 'text-orange-600 font-semibold' // 🟠 8-15 gün kala
  }

  if (diffDays >= 16 && diffDays <= 30) {
    return 'text-yellow-600 font-semibold' // 🟡 16-30 gün kala
  }

  return 'text-gray-600' // Normal (30+ gün)
}

function formatDate (dateString) {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('tr-TR')
}

function formatCurrency (amount) {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY'
  }).format(amount || 0)
}

async function loadOrders () {
  loading.value = true
  try {
    const params = {
      skip: (currentPage.value - 1) * itemsPerPage.value,
      limit: itemsPerPage.value
    }

    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    if (customerFilter.value) {
      params.customer_id = customerFilter.value
    }

    const response = await ordersAPI.getOrders(params)
    orders.value = response
    totalOrders.value = response.length
  } catch (error) {
    console.error('Error loading orders:', error)
    // Fallback to empty array on error
    orders.value = []
    totalOrders.value = 0
  } finally {
    loading.value = false
  }
}

async function loadCustomers () {
  try {
    const response = await customersAPI.getCustomers()
    customers.value = response
  } catch (error) {
    console.error('Error loading customers:', error)
    // Fallback to empty array on error
    customers.value = []
  }
}

async function loadProducts () {
  try {
    const response = await productsAPI.getProducts()
    products.value = response
  } catch (error) {
    console.error('Error loading products:', error)
    // Fallback to empty array on error
    products.value = []
  }
}

function viewOrder (order) {
  selectedOrder.value = order
  showDetailsModal.value = true
}

function editOrder (order) {
  editingOrder.value = order
  orderForm.value = {
    customer_id: order.customer_id,
    due_date: order.due_date,
    status: order.status,
    total_amount: order.total_amount || 0,
    notes: order.notes || '',
    items: order.items
      ? order.items.map(item => ({
        product_id: item.product_id || '',
        quantity: item.quantity || 0,
        unit_price: item.unit_price || 0
      }))
      : [{ product_id: '', quantity: 0, unit_price: 0 }]
  }
  showEditModal.value = true
}

async function confirmOrder (order) {
  if (confirm(`Confirm order ${order.order_number}?`)) {
    try {
      await ordersAPI.updateOrder(order.id, { status: 'confirmed' })
      order.status = 'confirmed'
    } catch (error) {
      console.error('Error confirming order:', error)
    }
  }
}

async function cancelOrder (order) {
  if (confirm(`Cancel order ${order.order_number}?`)) {
    try {
      await ordersAPI.updateOrder(order.id, { status: 'cancelled' })
      order.status = 'cancelled'
    } catch (error) {
      console.error('Error cancelling order:', error)
    }
  }
}

async function deleteOrder (order) {
  if (confirm(`Are you sure you want to delete order ${order.order_number}?`)) {
    try {
      await ordersAPI.deleteOrder(order.id)
      orders.value = orders.value.filter(o => o.id !== order.id)
      totalOrders.value = orders.value.length
    } catch (error) {
      console.error('Error deleting order:', error)
    }
  }
}

async function saveOrder () {
  saving.value = true
  try {
    const orderData = {
      customer_id: orderForm.value.customer_id,
      due_date: orderForm.value.due_date,
      total_amount: orderTotal.value,
      notes: orderForm.value.notes
    }

    if (showAddModal.value) {
      const newOrder = await ordersAPI.createOrder(orderData)

      // Add order items
      for (const item of orderForm.value.items) {
        if (item.product_id && item.quantity > 0) {
          await ordersAPI.createOrderItem(newOrder.id, {
            product_id: item.product_id,
            quantity: item.quantity,
            unit_price: item.unit_price
          })
        }
      }

      orders.value.unshift(newOrder)
      totalOrders.value = orders.value.length
    } else {
      const updatedOrder = await ordersAPI.updateOrder(editingOrder.value.id, orderData)

      // Update order items
      const existingItems = await ordersAPI.getOrderItems(editingOrder.value.id)
      for (const existingItem of existingItems) {
        await ordersAPI.deleteOrderItem(existingItem.id)
      }

      for (const item of orderForm.value.items) {
        if (item.product_id && item.quantity > 0) {
          await ordersAPI.createOrderItem(editingOrder.value.id, {
            product_id: item.product_id,
            quantity: item.quantity,
            unit_price: item.unit_price
          })
        }
      }

      const index = orders.value.findIndex(o => o.id === editingOrder.value.id)
      if (index !== -1) {
        orders.value[index] = updatedOrder
      }
    }

    closeModal()
  } catch (error) {
    console.error('Error saving order:', error)
  } finally {
    saving.value = false
  }
}

function closeModal () {
  showAddModal.value = false
  showEditModal.value = false
  showDetailsModal.value = false
  editingOrder.value = null
  selectedOrder.value = null
  orderForm.value = {
    customer_id: '',
    due_date: '',
    status: 'pending',
    total_amount: 0,
    notes: '',
    items: [{ product_id: '', quantity: 0, unit_price: 0 }]
  }
}

function addOrderItem () {
  orderForm.value.items.push({ product_id: '', quantity: 0, unit_price: 0 })
}

function removeOrderItem (index) {
  if (orderForm.value.items.length > 1) {
    orderForm.value.items.splice(index, 1)
  }
}

// Pagination methods
function goToPage (page) {
  currentPage.value = page
  loadOrders()
}

function previousPage () {
  if (currentPage.value > 1) {
    currentPage.value--
    loadOrders()
  }
}

function nextPage () {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadOrders()
  }
}

// Watch for filter changes
watch([searchQuery, statusFilter, customerFilter], () => {
  currentPage.value = 1
  loadOrders()
})

// Lifecycle
onMounted(() => {
  loadOrders()
  loadCustomers()
  loadProducts()
})
</script>

<style scoped>
.input-field {
  @apply block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm;
}
</style>
