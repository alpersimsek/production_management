<template>
  <div>
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-gray-900">{{ $t('shipments.shipment_management') }}</h1>
          <div class="flex gap-2">
            <button
              @click="showAddModal = true"
              class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              {{ $t('shipments.new_shipment') }}
            </button>
            <button
              @click="showTrackingModal = true"
              class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              {{ $t('shipments.track_shipment') }}
            </button>
          </div>
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
                  :placeholder="$t('shipments.search_shipments_placeholder')"
                  class="input-field"
                />
              </div>
              <div class="flex gap-2">
                <select v-model="statusFilter" class="input-field">
                  <option value="">{{ $t('shipments.all_status') }}</option>
                  <option value="pending">{{ $t('shipments.shipment_statuses.pending') }}</option>
                  <option value="preparing">{{ $t('shipments.shipment_statuses.preparing') }}</option>
                  <option value="ready_for_pickup">{{ $t('shipments.shipment_statuses.ready_for_pickup') }}</option>
                  <option value="in_transit">{{ $t('shipments.shipment_statuses.in_transit') }}</option>
                  <option value="out_for_delivery">{{ $t('shipments.shipment_statuses.out_for_delivery') }}</option>
                  <option value="delivered">{{ $t('shipments.shipment_statuses.delivered') }}</option>
                  <option value="failed">{{ $t('shipments.shipment_statuses.failed') }}</option>
                  <option value="returned">{{ $t('shipments.shipment_statuses.returned') }}</option>
                </select>
                <select v-model="customerFilter" class="input-field">
                  <option value="">{{ $t('shipments.all_customers') }}</option>
                  <option v-for="customer in customers" :key="customer.id" :value="customer.id">
                    {{ customer.name }}
                  </option>
                </select>
                <select v-model="priorityFilter" class="input-field">
                  <option value="">{{ $t('shipments.all_priorities') }}</option>
                  <option value="low">{{ $t('shipments.shipment_priorities.low') }}</option>
                  <option value="medium">{{ $t('shipments.shipment_priorities.medium') }}</option>
                  <option value="high">{{ $t('shipments.shipment_priorities.high') }}</option>
                  <option value="urgent">{{ $t('shipments.shipment_priorities.urgent') }}</option>
                </select>
                <button
                  @click="loadShipments"
                  class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  {{ $t('shipments.refresh') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Shipments List -->
          <div class="bg-white shadow overflow-hidden sm:rounded-md">
            <div v-if="loading" class="p-6 text-center">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p class="mt-2 text-gray-600">{{ $t('shipments.loading_shipments') }}</p>
            </div>

            <div v-else-if="shipments.length === 0" class="p-6 text-center text-gray-500">
              {{ $t('shipments.no_shipments_found') }}
            </div>

            <!-- Desktop table -->
            <div v-else class="hidden lg:block overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('shipments.shipment_number') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('shipments.order_number') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('shipments.customer') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('shipments.destination') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('shipments.items') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('shipments.status') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('shipments.priority') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('shipments.ship_date') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('shipments.expected_delivery') }}
                    </th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('shipments.actions') }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="shipment in filteredShipments" :key="shipment.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {{ shipment.shipment_number }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ shipment.order_number }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ shipment.customer_name }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ shipment.destination_city }}, {{ shipment.destination_country }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ shipment.item_count }} items
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="getStatusColor(shipment.status)"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      >
                        {{ formatStatus(shipment.status) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="getPriorityColor(shipment.priority)"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      >
                        {{ formatPriority(shipment.priority) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ shipment.ship_date ? formatDate(shipment.ship_date) : '-' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ shipment.expected_delivery_date ? formatDate(shipment.expected_delivery_date) : '-' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        @click="viewShipment(shipment)"
                        class="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        {{ $t('shipments.view') }}
                      </button>
                      <button
                        @click="editShipment(shipment)"
                        class="text-primary-600 hover:text-primary-900 mr-3"
                      >
                        {{ $t('shipments.edit') }}
                      </button>
                      <button
                        v-if="shipment.status === 'pending' || shipment.status === 'preparing'"
                        @click="prepareShipment(shipment)"
                        class="text-green-600 hover:text-green-900 mr-3"
                      >
                        {{ $t('shipments.prepare') }}
                      </button>
                      <button
                        v-if="shipment.status === 'ready_for_pickup'"
                        @click="shipShipment(shipment)"
                        class="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        {{ $t('shipments.ship') }}
                      </button>
                      <button
                        v-if="shipment.status === 'in_transit'"
                        @click="deliverShipment(shipment)"
                        class="text-green-600 hover:text-green-900 mr-3"
                      >
                        {{ $t('shipments.deliver') }}
                      </button>
                      <button
                        @click="trackShipment(shipment)"
                        class="text-purple-600 hover:text-purple-900 mr-3"
                      >
                        {{ $t('shipments.track') }}
                      </button>
                      <button
                        @click="deleteShipment(shipment)"
                        class="text-red-600 hover:text-red-900"
                      >
                        {{ $t('shipments.delete') }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Mobile carousel -->
            <div v-if="shipments.length > 0" class="block lg:hidden p-4">
              <div class="text-sm text-gray-500 mb-2 text-center">
                {{ $t('shipments.showing_shipment') }} {{ currentShipmentIndex + 1 }} {{ $t('common.of') }} {{ filteredShipments.length }} — {{ $t('orders.swipe_hint') }}
              </div>
              <div
                class="bg-white rounded-lg shadow-md overflow-hidden select-none"
                @touchstart.passive="handleShipTouchStart"
                @touchmove.prevent="handleShipTouchMove"
                @touchend="handleShipTouchEnd"
                @mousedown.prevent="handleShipMouseDown"
                @mousemove.prevent="handleShipMouseMove"
                @mouseup.prevent="handleShipMouseUp"
                @mouseleave.prevent="handleShipMouseUp"
              >
                <div class="p-4" v-if="currentShipment">
                  <div class="flex items-center justify-between mb-2">
                    <div class="text-base font-semibold text-gray-900">{{ currentShipment.shipment_number }}</div>
                    <span :class="getStatusColor(currentShipment.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">{{ formatStatus(currentShipment.status) }}</span>
                  </div>
                  <div class="space-y-1 text-sm">
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('shipments.order_number') }}:</span><span class="text-gray-900">{{ currentShipment.order_number }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('shipments.customer') }}:</span><span class="text-gray-900">{{ currentShipment.customer_name }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('shipments.destination') }}:</span><span class="text-gray-900">{{ currentShipment.destination_city }}, {{ currentShipment.destination_country }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('shipments.items') }}:</span><span class="text-gray-900">{{ currentShipment.item_count }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('shipments.priority') }}:</span><span class="text-gray-900"><span :class="getPriorityColor(currentShipment.priority)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">{{ formatPriority(currentShipment.priority) }}</span></span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('shipments.ship_date') }}:</span><span class="text-gray-900">{{ currentShipment.ship_date ? formatDate(currentShipment.ship_date) : '-' }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('shipments.expected_delivery') }}:</span><span class="text-gray-900">{{ currentShipment.expected_delivery_date ? formatDate(currentShipment.expected_delivery_date) : '-' }}</span></div>
                  </div>
                  <div class="flex gap-3 mt-3">
                    <button @click="viewShipment(currentShipment)" class="text-blue-600 hover:text-blue-900 text-sm">{{ $t('shipments.view') }}</button>
                    <button @click="editShipment(currentShipment)" class="text-primary-600 hover:text-primary-900 text-sm">{{ $t('shipments.edit') }}</button>
                    <button v-if="currentShipment.status === 'pending' || currentShipment.status === 'preparing'" @click="prepareShipment(currentShipment)" class="text-green-600 hover:text-green-900 text-sm">{{ $t('shipments.prepare') }}</button>
                    <button v-if="currentShipment.status === 'ready_for_pickup'" @click="shipShipment(currentShipment)" class="text-blue-600 hover:text-blue-900 text-sm">{{ $t('shipments.ship') }}</button>
                    <button v-if="currentShipment.status === 'in_transit'" @click="deliverShipment(currentShipment)" class="text-green-600 hover:text-green-900 text-sm">{{ $t('shipments.deliver') }}</button>
                    <button @click="trackShipment(currentShipment)" class="text-purple-600 hover:text-purple-900 text-sm">{{ $t('shipments.track') }}</button>
                  </div>
                </div>
              </div>
              <div class="flex justify-between mt-3">
                <button @click="previousShipment" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.previous') }}</button>
                <button @click="nextShipment" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.next') }}</button>
              </div>
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
                {{ $t('shipments.previous') }}
              </button>
              <button
                @click="nextPage"
                :disabled="currentPage === totalPages"
                class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                {{ $t('shipments.next') }}
              </button>
            </div>
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p class="text-sm text-gray-700">
                  {{ $t('shipments.showing') }}
                  <span class="font-medium">{{ (currentPage - 1) * itemsPerPage + 1 }}</span>
                  {{ $t('shipments.to') }}
                  <span class="font-medium">{{ Math.min(currentPage * itemsPerPage, totalShipments) }}</span>
                  {{ $t('shipments.of') }}
                  <span class="font-medium">{{ totalShipments }}</span>
                  {{ $t('shipments.results') }}
                </p>
              </div>
              <div>
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    @click="previousPage"
                    :disabled="currentPage === 1"
                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    {{ $t('shipments.previous') }}
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
                    {{ $t('shipments.next') }}
                  </button>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add/Edit Shipment Modal -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ showAddModal ? $t('shipments.new_shipment') : $t('shipments.edit_shipment') }}
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

          <form @submit.prevent="saveShipment" class="space-y-6">
            <!-- Shipment Basic Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.order') }} *</label>
                <select v-model="shipmentForm.order_id" required class="input-field mt-1">
                  <option value="">{{ $t('shipments.select_order') }}</option>
                  <option v-for="order in orders" :key="order.id" :value="order.id">
                    {{ order.order_number }} - {{ order.customer_name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.customer_name') }} *</label>
                <input
                  v-model="shipmentForm.customer_name"
                  type="text"
                  readonly
                  class="input-field mt-1 bg-gray-50"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.priority') }} *</label>
                <select v-model="shipmentForm.priority" required class="input-field mt-1">
                  <option value="">{{ $t('shipments.select_priority') }}</option>
                  <option value="low">{{ $t('shipments.shipment_priorities.low') }}</option>
                  <option value="medium">{{ $t('shipments.shipment_priorities.medium') }}</option>
                  <option value="high">{{ $t('shipments.shipment_priorities.high') }}</option>
                  <option value="urgent">{{ $t('shipments.shipment_priorities.urgent') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.status') }} *</label>
                <select v-model="shipmentForm.status" required class="input-field mt-1">
                  <option value="">{{ $t('shipments.select_status') }}</option>
                  <option value="pending">{{ $t('shipments.shipment_statuses.pending') }}</option>
                  <option value="preparing">{{ $t('shipments.shipment_statuses.preparing') }}</option>
                  <option value="ready_for_pickup">{{ $t('shipments.shipment_statuses.ready_for_pickup') }}</option>
                  <option value="in_transit">{{ $t('shipments.shipment_statuses.in_transit') }}</option>
                  <option value="out_for_delivery">{{ $t('shipments.shipment_statuses.out_for_delivery') }}</option>
                  <option value="delivered">{{ $t('shipments.shipment_statuses.delivered') }}</option>
                  <option value="failed">{{ $t('shipments.shipment_statuses.failed') }}</option>
                  <option value="returned">{{ $t('shipments.shipment_statuses.returned') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.ship_date') }}</label>
                <input
                  v-model="shipmentForm.ship_date"
                  type="date"
                  class="input-field mt-1"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.expected_delivery_date') }}</label>
                <input
                  v-model="shipmentForm.expected_delivery_date"
                  type="date"
                  class="input-field mt-1"
                />
              </div>
            </div>

            <!-- Delivery Address -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('shipments.delivery_address') }}</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.street_address') }} *</label>
                  <input
                    v-model="shipmentForm.delivery_address"
                    type="text"
                    required
                    class="input-field mt-1"
                    placeholder="123 Main Street"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.city') }} *</label>
                  <input
                    v-model="shipmentForm.destination_city"
                    type="text"
                    required
                    class="input-field mt-1"
                    placeholder="Istanbul"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.state_province') }}</label>
                  <input
                    v-model="shipmentForm.destination_state"
                    type="text"
                    class="input-field mt-1"
                    placeholder="Istanbul"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.postal_code') }}</label>
                  <input
                    v-model="shipmentForm.destination_postal_code"
                    type="text"
                    class="input-field mt-1"
                    placeholder="34000"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.country') }} *</label>
                  <input
                    v-model="shipmentForm.destination_country"
                    type="text"
                    required
                    class="input-field mt-1"
                    placeholder="Türkiye"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.contact_phone') }}</label>
                  <input
                    v-model="shipmentForm.contact_phone"
                    type="tel"
                    class="input-field mt-1"
                    placeholder="+90 212 123 4567"
                  />
                </div>
              </div>
            </div>

            <!-- Shipping Details -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('shipments.shipping_details') }}</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.shipping_method') }}</label>
                  <select v-model="shipmentForm.shipping_method" class="input-field mt-1">
                    <option value="">{{ $t('shipments.select_method') }}</option>
                    <option value="standard">{{ $t('shipments.shipping_methods.standard') }}</option>
                    <option value="express">{{ $t('shipments.shipping_methods.express') }}</option>
                    <option value="overnight">{{ $t('shipments.shipping_methods.overnight') }}</option>
                    <option value="freight">{{ $t('shipments.shipping_methods.freight') }}</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.carrier') }}</label>
                  <select v-model="shipmentForm.carrier" class="input-field mt-1">
                    <option value="">{{ $t('shipments.select_carrier') }}</option>
                    <option value="ups">{{ $t('shipments.carriers.ups') }}</option>
                    <option value="fedex">{{ $t('shipments.carriers.fedex') }}</option>
                    <option value="dhl">{{ $t('shipments.carriers.dhl') }}</option>
                    <option value="aramex">{{ $t('shipments.carriers.aramex') }}</option>
                    <option value="yurtici">{{ $t('shipments.carriers.yurtici') }}</option>
                    <option value="mng">{{ $t('shipments.carriers.mng') }}</option>
                    <option value="ptt">{{ $t('shipments.carriers.ptt') }}</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.tracking_number') }}</label>
                  <input
                    v-model="shipmentForm.tracking_number"
                    type="text"
                    class="input-field mt-1"
                    placeholder="1Z999AA1234567890"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.weight') }}</label>
                  <input
                    v-model.number="shipmentForm.weight"
                    type="number"
                    step="0.01"
                    min="0"
                    class="input-field mt-1"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.dimensions') }}</label>
                  <input
                    v-model="shipmentForm.dimensions"
                    type="text"
                    class="input-field mt-1"
                    placeholder="30 x 20 x 10"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.shipping_cost') }}</label>
                  <input
                    v-model.number="shipmentForm.shipping_cost"
                    type="number"
                    step="0.01"
                    min="0"
                    class="input-field mt-1"
                    placeholder="0.00"
                  />
                </div>
              </div>
            </div>

            <!-- Special Instructions -->
            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.special_instructions') }}</label>
              <textarea
                v-model="shipmentForm.special_instructions"
                class="input-field mt-1"
                rows="3"
                placeholder="Delivery instructions, handling requirements, etc."
              ></textarea>
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="closeModal"
                class="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md text-sm font-medium"
              >
                {{ $t('shipments.cancel') }}
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
              >
                {{ saving ? $t('shipments.saving') : $t('shipments.save_shipment') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Shipment Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ $t('shipments.shipment_details') }} - {{ selectedShipment?.shipment_number }}
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

          <div v-if="selectedShipment" class="space-y-6">
            <!-- Shipment Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('shipments.basic_information') }}</h4>
                <dl class="space-y-2">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('shipments.shipment_number') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedShipment.shipment_number }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('shipments.order_number') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedShipment.order_number }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('shipments.customer') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedShipment.customer_name }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('shipments.status') }}:</dt>
                    <dd class="text-sm">
                      <span :class="getStatusColor(selectedShipment.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                        {{ formatStatus(selectedShipment.status) }}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('shipments.priority') }}:</dt>
                    <dd class="text-sm">
                      <span :class="getPriorityColor(selectedShipment.priority)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                        {{ formatPriority(selectedShipment.priority) }}
                      </span>
                    </dd>
                  </div>
                </dl>
              </div>

              <div>
                <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('shipments.delivery_information') }}</h4>
                <dl class="space-y-2">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('shipments.destination') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedShipment.destination_city }}, {{ selectedShipment.destination_country }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('shipments.address') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedShipment.delivery_address }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('shipments.contact') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedShipment.contact_phone || '-' }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('shipments.ship_date') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedShipment.ship_date ? formatDate(selectedShipment.ship_date) : '-' }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('shipments.expected_delivery') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedShipment.expected_delivery_date ? formatDate(selectedShipment.expected_delivery_date) : '-' }}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <!-- Shipping Details -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('shipments.shipping_details') }}</h4>
              <div class="bg-gray-50 p-4 rounded-lg">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('shipments.shipping_method') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedShipment.shipping_method || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('shipments.carrier') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedShipment.carrier || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('shipments.tracking_number') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedShipment.tracking_number || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('shipments.weight') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedShipment.weight ? selectedShipment.weight + ' kg' : '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('shipments.dimensions') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedShipment.dimensions || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('shipments.shipping_cost') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedShipment.shipping_cost ? '₺' + selectedShipment.shipping_cost : '-' }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Shipment Timeline -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('shipments.shipment_timeline') }}</h4>
              <div class="space-y-4">
                <div class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-green-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('shipments.shipment_created') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedShipment.created_at) }}</p>
                  </div>
                </div>
                <div v-if="selectedShipment.ship_date" class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-blue-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('shipments.shipped') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedShipment.ship_date) }}</p>
                  </div>
                </div>
                <div v-if="selectedShipment.expected_delivery_date" class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-gray-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('shipments.expected_delivery_timeline') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedShipment.expected_delivery_date) }}</p>
                  </div>
                </div>
                <div v-if="selectedShipment.delivered_at" class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-green-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('shipments.delivered_timeline') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedShipment.delivered_at) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Special Instructions -->
            <div v-if="selectedShipment.special_instructions">
              <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('shipments.special_instructions') }}</h4>
              <p class="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">{{ selectedShipment.special_instructions }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Tracking Modal -->
    <div v-if="showTrackingModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-2xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">{{ $t('shipments.track_shipment') }}</h3>
            <button
              @click="showTrackingModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('shipments.enter_tracking_number') }}</label>
              <div class="mt-1 flex">
                <input
                  v-model="trackingNumber"
                  type="text"
                  class="input-field rounded-r-none"
                  placeholder="1Z999AA1234567890"
                />
                <button
                  @click="trackShipmentByNumber"
                  class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-r-md text-sm font-medium"
                >
                  {{ $t('shipments.track') }}
                </button>
              </div>
            </div>

            <div v-if="trackingResult" class="bg-gray-50 p-4 rounded-lg">
              <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('shipments.tracking_information') }}</h4>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">{{ $t('shipments.status') }}:</span>
                  <span :class="getStatusColor(trackingResult.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ formatStatus(trackingResult.status) }}
                  </span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">{{ $t('shipments.last_update') }}:</span>
                  <span class="text-sm text-gray-900">{{ formatDateTime(trackingResult.last_update) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-500">{{ $t('shipments.location') }}:</span>
                  <span class="text-sm text-gray-900">{{ trackingResult.location }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// Data
const shipments = ref([])
const orders = ref([])
const customers = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const customerFilter = ref('')
const priorityFilter = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showDetailsModal = ref(false)
const showTrackingModal = ref(false)
const editingShipment = ref(null)
const selectedShipment = ref(null)
const trackingNumber = ref('')
const trackingResult = ref(null)

// Mobile carousel state
const currentShipmentIndex = ref(0)
const shipTouchStartX = ref(0)
const shipTouchStartY = ref(0)
const shipIsDragging = ref(false)

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(10)
const totalShipments = ref(0)

const shipmentForm = ref({
  order_id: '',
  customer_name: '',
  priority: '',
  status: '',
  ship_date: '',
  expected_delivery_date: '',
  delivery_address: '',
  destination_city: '',
  destination_state: '',
  destination_postal_code: '',
  destination_country: '',
  contact_phone: '',
  shipping_method: '',
  carrier: '',
  tracking_number: '',
  weight: 0,
  dimensions: '',
  shipping_cost: 0,
  special_instructions: ''
})

// Computed
const filteredShipments = computed(() => {
  let filtered = shipments.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(shipment =>
      shipment.shipment_number.toLowerCase().includes(query) ||
      shipment.order_number.toLowerCase().includes(query) ||
      shipment.customer_name.toLowerCase().includes(query) ||
      shipment.destination_city.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(shipment => shipment.status === statusFilter.value)
  }

  if (customerFilter.value) {
    filtered = filtered.filter(shipment => shipment.customer_id === parseInt(customerFilter.value))
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(shipment => shipment.priority === priorityFilter.value)
  }

  return filtered
})

const currentShipment = computed(() => filteredShipments.value[currentShipmentIndex.value] || null)

const totalPages = computed(() => Math.ceil(totalShipments.value / itemsPerPage.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Methods
function getStatusColor (status) {
  const colors = {
    pending: 'bg-gray-100 text-gray-800',
    preparing: 'bg-yellow-100 text-yellow-800',
    ready_for_pickup: 'bg-blue-100 text-blue-800',
    in_transit: 'bg-indigo-100 text-indigo-800',
    out_for_delivery: 'bg-purple-100 text-purple-800',
    delivered: 'bg-green-100 text-green-800',
    failed: 'bg-red-100 text-red-800',
    returned: 'bg-orange-100 text-orange-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

function getPriorityColor (priority) {
  const colors = {
    low: 'bg-gray-100 text-gray-800',
    medium: 'bg-blue-100 text-blue-800',
    high: 'bg-orange-100 text-orange-800',
    urgent: 'bg-red-100 text-red-800'
  }
  return colors[priority] || 'bg-gray-100 text-gray-800'
}

function formatStatus (status) {
  return t(`shipments.shipment_statuses.${status}`) || status
}

function formatPriority (priority) {
  return t(`shipments.shipment_priorities.${priority}`) || priority
}

function formatDate (dateString) {
  return new Date(dateString).toLocaleDateString('tr-TR')
}

function formatDateTime (dateString) {
  return new Date(dateString).toLocaleString('tr-TR')
}

async function loadShipments () {
  loading.value = true
  try {
    // Load data from API
    // Mock data removed
    totalShipments.value = shipments.value.length
  } catch (error) {
    console.error('Error loading shipments:', error)
  } finally {
    loading.value = false
  }
}

async function loadOrders () {
  try {
    // Load data from API
    // Mock data removed
  } catch (error) {
    console.error('Error loading orders:', error)
  }
}

async function loadCustomers () {
  try {
    // Load data from API
    // Mock data removed
  } catch (error) {
    console.error('Error loading customers:', error)
  }
}

function viewShipment (shipment) {
  selectedShipment.value = shipment
  showDetailsModal.value = true
}

function editShipment (shipment) {
  editingShipment.value = shipment
  shipmentForm.value = {
    order_id: shipment.order_id,
    customer_name: shipment.customer_name,
    priority: shipment.priority,
    status: shipment.status,
    ship_date: shipment.ship_date,
    expected_delivery_date: shipment.expected_delivery_date,
    delivery_address: shipment.delivery_address,
    destination_city: shipment.destination_city,
    destination_state: shipment.destination_state,
    destination_postal_code: shipment.destination_postal_code,
    destination_country: shipment.destination_country,
    contact_phone: shipment.contact_phone,
    shipping_method: shipment.shipping_method,
    carrier: shipment.carrier,
    tracking_number: shipment.tracking_number,
    weight: shipment.weight,
    dimensions: shipment.dimensions,
    shipping_cost: shipment.shipping_cost,
    special_instructions: shipment.special_instructions
  }
  showEditModal.value = true
}

async function prepareShipment (shipment) {
  if (confirm(`Prepare shipment ${shipment.shipment_number} for shipping?`)) {
    try {
      // TODO: Implement prepare API call
      shipment.status = 'ready_for_pickup'
    } catch (error) {
      console.error('Error preparing shipment:', error)
    }
  }
}

async function shipShipment (shipment) {
  if (confirm(`Ship ${shipment.shipment_number}?`)) {
    try {
      // TODO: Implement ship API call
      shipment.status = 'in_transit'
      shipment.ship_date = new Date().toISOString().split('T')[0]
    } catch (error) {
      console.error('Error shipping:', error)
    }
  }
}

async function deliverShipment (shipment) {
  if (confirm(`Mark ${shipment.shipment_number} as delivered?`)) {
    try {
      // TODO: Implement deliver API call
      shipment.status = 'delivered'
      shipment.delivered_at = new Date().toISOString()
    } catch (error) {
      console.error('Error delivering shipment:', error)
    }
  }
}

function trackShipment (shipment) {
  trackingNumber.value = shipment.tracking_number
  showTrackingModal.value = true
  trackShipmentByNumber()
}

function trackShipmentByNumber () {
  if (!trackingNumber.value) return

  // Mock tracking result
  trackingResult.value = {
    status: 'in_transit',
    last_update: '2024-01-20T15:30:00Z',
    location: 'Istanbul Distribution Center'
  }
}

async function deleteShipment (shipment) {
  if (confirm(`Are you sure you want to delete shipment ${shipment.shipment_number}?`)) {
    try {
      // TODO: Implement delete API call
      shipments.value = shipments.value.filter(s => s.id !== shipment.id)
      totalShipments.value = shipments.value.length
    } catch (error) {
      console.error('Error deleting shipment:', error)
    }
  }
}

async function saveShipment () {
  saving.value = true
  try {
    if (showAddModal.value) {
      // TODO: Implement create API call
      const newShipment = {
        id: Date.now(),
        shipment_number: `SHIP-2024-${String(shipments.value.length + 1).padStart(3, '0')}`,
        order_id: shipmentForm.value.order_id,
        order_number: orders.value.find(o => o.id === shipmentForm.value.order_id)?.order_number || '',
        customer_id: orders.value.find(o => o.id === shipmentForm.value.order_id)?.customer_id || 1,
        customer_name: shipmentForm.value.customer_name,
        priority: shipmentForm.value.priority,
        status: shipmentForm.value.status,
        ship_date: shipmentForm.value.ship_date,
        expected_delivery_date: shipmentForm.value.expected_delivery_date,
        delivered_at: null,
        delivery_address: shipmentForm.value.delivery_address,
        destination_city: shipmentForm.value.destination_city,
        destination_state: shipmentForm.value.destination_state,
        destination_postal_code: shipmentForm.value.destination_postal_code,
        destination_country: shipmentForm.value.destination_country,
        contact_phone: shipmentForm.value.contact_phone,
        shipping_method: shipmentForm.value.shipping_method,
        carrier: shipmentForm.value.carrier,
        tracking_number: shipmentForm.value.tracking_number,
        weight: shipmentForm.value.weight,
        dimensions: shipmentForm.value.dimensions,
        shipping_cost: shipmentForm.value.shipping_cost,
        item_count: 1,
        special_instructions: shipmentForm.value.special_instructions,
        created_at: new Date().toISOString()
      }
      shipments.value.unshift(newShipment)
      totalShipments.value = shipments.value.length
    } else {
      // TODO: Implement update API call
      const index = shipments.value.findIndex(s => s.id === editingShipment.value.id)
      if (index !== -1) {
        shipments.value[index] = {
          ...shipments.value[index],
          order_id: shipmentForm.value.order_id,
          order_number: orders.value.find(o => o.id === shipmentForm.value.order_id)?.order_number || '',
          customer_name: shipmentForm.value.customer_name,
          priority: shipmentForm.value.priority,
          status: shipmentForm.value.status,
          ship_date: shipmentForm.value.ship_date,
          expected_delivery_date: shipmentForm.value.expected_delivery_date,
          delivery_address: shipmentForm.value.delivery_address,
          destination_city: shipmentForm.value.destination_city,
          destination_state: shipmentForm.value.destination_state,
          destination_postal_code: shipmentForm.value.destination_postal_code,
          destination_country: shipmentForm.value.destination_country,
          contact_phone: shipmentForm.value.contact_phone,
          shipping_method: shipmentForm.value.shipping_method,
          carrier: shipmentForm.value.carrier,
          tracking_number: shipmentForm.value.tracking_number,
          weight: shipmentForm.value.weight,
          dimensions: shipmentForm.value.dimensions,
          shipping_cost: shipmentForm.value.shipping_cost,
          special_instructions: shipmentForm.value.special_instructions
        }
      }
    }
    closeModal()
  } catch (error) {
    console.error('Error saving shipment:', error)
  } finally {
    saving.value = false
  }
}

function closeModal () {
  showAddModal.value = false
  showEditModal.value = false
  showDetailsModal.value = false
  showTrackingModal.value = false
  editingShipment.value = null
  selectedShipment.value = null
  trackingNumber.value = ''
  trackingResult.value = null
  shipmentForm.value = {
    order_id: '',
    customer_name: '',
    priority: '',
    status: '',
    ship_date: '',
    expected_delivery_date: '',
    delivery_address: '',
    destination_city: '',
    destination_state: '',
    destination_postal_code: '',
    destination_country: '',
    contact_phone: '',
    shipping_method: '',
    carrier: '',
    tracking_number: '',
    weight: 0,
    dimensions: '',
    shipping_cost: 0,
    special_instructions: ''
  }
}

// Carousel navigation
function nextShipment () {
  if (filteredShipments.value.length === 0) return
  currentShipmentIndex.value = (currentShipmentIndex.value + 1) % filteredShipments.value.length
}

function previousShipment () {
  if (filteredShipments.value.length === 0) return
  currentShipmentIndex.value = (currentShipmentIndex.value - 1 + filteredShipments.value.length) % filteredShipments.value.length
}

function handleShipTouchStart (e) {
  const touch = e.touches[0]
  shipTouchStartX.value = touch.clientX
  shipTouchStartY.value = touch.clientY
  shipIsDragging.value = true
}

function handleShipTouchMove (e) {
  // intentionally left blank (no-op)
}

function handleShipTouchEnd (e) {
  if (!shipIsDragging.value) return
  const touch = e.changedTouches[0]
  const dx = touch.clientX - shipTouchStartX.value
  shipIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextShipment()
  else if (dx > threshold) previousShipment()
}

function handleShipMouseDown (e) {
  shipTouchStartX.value = e.clientX
  shipTouchStartY.value = e.clientY
  shipIsDragging.value = true
}

function handleShipMouseMove (e) {
  // intentionally left blank (no-op)
}

function handleShipMouseUp (e) {
  if (!shipIsDragging.value) return
  const dx = e.clientX - shipTouchStartX.value
  shipIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextShipment()
  else if (dx > threshold) previousShipment()
}

// ESC to close modals
function handleKeydown (event) {
  if (event.key === 'Escape') {
    closeModal()
  }
}

// Pagination methods
function goToPage (page) {
  currentPage.value = page
}

function previousPage () {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

function nextPage () {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

// Watch for order changes to update customer info
watch(() => shipmentForm.value.order_id, (newOrderId) => {
  const order = orders.value.find(o => o.id === newOrderId)
  if (order) {
    shipmentForm.value.customer_name = order.customer_name
  }
})

// Lifecycle
onMounted(() => {
  loadShipments()
  loadOrders()
  loadCustomers()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>
