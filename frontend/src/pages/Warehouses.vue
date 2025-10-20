<template>
  <div>
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-gray-900">{{ $t('warehouse.warehouse_management') }}</h1>
          <div class="flex gap-2">
            <button
              @click="showAddModal = true"
              class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              {{ $t('warehouse.new_warehouse') }}
            </button>
            <button
              @click="showInventoryModal = true"
              class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              {{ $t('warehouse.inventory_overview') }}
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
                  :placeholder="$t('warehouse.search_warehouses_placeholder')"
                  class="input-field"
                />
              </div>
              <div class="flex gap-2">
                <select v-model="statusFilter" class="input-field">
                  <option value="">{{ $t('warehouse.all_status') }}</option>
                  <option value="active">{{ $t('warehouse.status_types.active') }}</option>
                  <option value="inactive">{{ $t('warehouse.status_types.inactive') }}</option>
                  <option value="maintenance">{{ $t('warehouse.status_types.maintenance') }}</option>
                </select>
                <select v-model="typeFilter" class="input-field">
                  <option value="">{{ $t('warehouse.all_types') }}</option>
                  <option value="raw_materials">{{ $t('warehouse.warehouse_types.raw_materials') }}</option>
                  <option value="finished_goods">{{ $t('warehouse.warehouse_types.finished_goods') }}</option>
                  <option value="packaging">{{ $t('warehouse.warehouse_types.packaging') }}</option>
                  <option value="general">{{ $t('warehouse.warehouse_types.general') }}</option>
                </select>
                <button
                  @click="loadWarehouses"
                  class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  {{ $t('warehouse.refresh') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Warehouse Cards: Desktop grid -->
          <div class="hidden lg:grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <div v-for="warehouse in filteredWarehouses" :key="warehouse.id" class="bg-white rounded-lg shadow-md overflow-hidden">
              <div class="p-6">
                <div class="flex items-center justify-between mb-4">
                  <h3 class="text-lg font-semibold text-gray-900">{{ formatWarehouseName(warehouse.type) }}</h3>
                  <span :class="getStatusColor(warehouse.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                    {{ t(`warehouse.status_types.${warehouse.status}`) }}
                  </span>
                </div>

                <div class="space-y-2 mb-4">
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-500">{{ $t('warehouse.type') }}:</span>
                    <span class="text-gray-900">{{ formatWarehouseType(warehouse.type) }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-500">{{ $t('warehouse.location') }}:</span>
                    <span class="text-gray-900">{{ warehouse.location }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-500">{{ $t('warehouse.capacity') }}:</span>
                    <span class="text-gray-900">{{ warehouse.capacity }} {{ warehouse.capacity_unit }}</span>
                  </div>
                  <div class="flex justify-between text-sm">
                    <span class="text-gray-500">{{ $t('warehouse.used') }}:</span>
                    <span class="text-gray-900">{{ warehouse.used_capacity }} {{ warehouse.capacity_unit }}</span>
                  </div>
                </div>

                <div class="mb-4">
                  <div class="flex justify-between text-xs text-gray-500 mb-1">
                    <span>{{ $t('warehouse.capacity_usage') }}</span>
                    <span>{{ Math.round((warehouse.used_capacity / warehouse.capacity) * 100) }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-2">
                    <div :class="getCapacityColor(warehouse.used_capacity / warehouse.capacity)" class="h-2 rounded-full transition-all duration-300" :style="{ width: `${(warehouse.used_capacity / warehouse.capacity) * 100}%` }"></div>
                  </div>
                </div>

                <div class="flex justify-between items-center">
                  <div class="text-sm text-gray-500">
                    {{ warehouse.item_count }} {{ $t('warehouse.items') }}
                  </div>
                  <div class="flex gap-2">
                    <button @click="viewWarehouse(warehouse)" class="text-blue-600 hover:text-blue-900 text-sm">{{ $t('warehouse.view') }}</button>
                    <button @click="editWarehouse(warehouse)" class="text-primary-600 hover:text-primary-900 text-sm">{{ $t('warehouse.edit') }}</button>
                    <button @click="manageInventory(warehouse)" class="text-green-600 hover:text-green-900 text-sm">{{ $t('warehouse.inventory') }}</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Warehouse Cards: Mobile carousel -->
          <div class="block lg:hidden mb-8">
            <div v-if="filteredWarehouses.length === 0" class="text-center text-gray-500 py-8">
              {{ $t('messages.no_data') }}
            </div>
            <div v-else class="relative">
              <div class="text-sm text-gray-500 mb-2 text-center">
                {{ $t('warehouse.showing_warehouse') }} {{ currentWarehouseIndex + 1 }} {{ $t('common.of') }} {{ filteredWarehouses.length }} — {{ $t('orders.swipe_hint') }}
              </div>
              <div
                class="bg-white rounded-lg shadow-md overflow-hidden select-none"
                @touchstart.passive="handleWhTouchStart"
                @touchmove.prevent="handleWhTouchMove"
                @touchend="handleWhTouchEnd"
                @mousedown.prevent="handleWhMouseDown"
                @mousemove.prevent="handleWhMouseMove"
                @mouseup.prevent="handleWhMouseUp"
                @mouseleave.prevent="handleWhMouseUp"
              >
                <div class="p-6" v-if="currentWarehouse">
                  <div class="flex items-center justify-between mb-4">
                    <h3 class="text-lg font-semibold text-gray-900">{{ formatWarehouseName(currentWarehouse.type) }}</h3>
                    <span :class="getStatusColor(currentWarehouse.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                      {{ t(`warehouse.status_types.${currentWarehouse.status}`) }}
                    </span>
                  </div>

                  <div class="space-y-2 mb-4">
                    <div class="flex justify-between text-sm">
                      <span class="text-gray-500">{{ $t('warehouse.type') }}:</span>
                      <span class="text-gray-900">{{ formatWarehouseType(currentWarehouse.type) }}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                      <span class="text-gray-500">{{ $t('warehouse.location') }}:</span>
                      <span class="text-gray-900">{{ currentWarehouse.location }}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                      <span class="text-gray-500">{{ $t('warehouse.capacity') }}:</span>
                      <span class="text-gray-900">{{ currentWarehouse.capacity }} {{ currentWarehouse.capacity_unit }}</span>
                    </div>
                    <div class="flex justify-between text-sm">
                      <span class="text-gray-500">{{ $t('warehouse.used') }}:</span>
                      <span class="text-gray-900">{{ currentWarehouse.used_capacity }} {{ currentWarehouse.capacity_unit }}</span>
                    </div>
                  </div>

                  <div class="mb-4">
                    <div class="flex justify-between text-xs text-gray-500 mb-1">
                      <span>{{ $t('warehouse.capacity_usage') }}</span>
                      <span>{{ Math.round((currentWarehouse.used_capacity / currentWarehouse.capacity) * 100) }}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                      <div :class="getCapacityColor(currentWarehouse.used_capacity / currentWarehouse.capacity)" class="h-2 rounded-full transition-all duration-300" :style="{ width: `${(currentWarehouse.used_capacity / currentWarehouse.capacity) * 100}%` }"></div>
                    </div>
                  </div>

                  <div class="flex justify-between items-center">
                    <div class="text-sm text-gray-500">
                      {{ currentWarehouse.item_count }} {{ $t('warehouse.items') }}
                    </div>
                    <div class="flex gap-2">
                      <button @click="viewWarehouse(currentWarehouse)" class="text-blue-600 hover:text-blue-900 text-sm">{{ $t('warehouse.view') }}</button>
                      <button @click="editWarehouse(currentWarehouse)" class="text-primary-600 hover:text-primary-900 text-sm">{{ $t('warehouse.edit') }}</button>
                      <button @click="manageInventory(currentWarehouse)" class="text-green-600 hover:text-green-900 text-sm">{{ $t('warehouse.inventory') }}</button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="flex justify-between mt-3">
                <button @click="previousWarehouse" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.previous') }}</button>
                <button @click="nextWarehouse" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.next') }}</button>
              </div>
            </div>
          </div>

          <!-- Warehouse Operations -->
          <div class="bg-white shadow overflow-hidden sm:rounded-md mb-6">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-lg font-medium text-gray-900">{{ $t('warehouse.recent_operations') }}</h3>
            </div>
            <!-- Desktop table -->
            <div class="hidden lg:block overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.date') }}</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.operation') }}</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.warehouse') }}</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.product') }}</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.quantity') }}</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.status') }}</th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.operator') }}</th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="operation in recentOperations" :key="operation.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(operation.date) }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ formatOperationType(operation.type) }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ operation.warehouse_name }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ operation.product_name }}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ operation.quantity }} {{ operation.unit }}</td>
                    <td class="px-6 py-4 whitespace-nowrap"><span :class="getOperationStatusColor(operation.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">{{ formatOperationStatus(operation.status) }}</span></td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ operation.operator_name }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Mobile carousel -->
            <div class="block lg:hidden p-4">
              <div v-if="recentOperations.length === 0" class="text-center text-gray-500 py-4">{{ $t('messages.no_data') }}</div>
              <div v-else>
                <div class="text-sm text-gray-500 mb-2 text-center">
                  {{ $t('warehouse.showing_operation') }} {{ currentOperationIndex + 1 }} {{ $t('common.of') }} {{ recentOperations.length }} — {{ $t('orders.swipe_hint') }}
                </div>
                <div
                  class="bg-white rounded-lg shadow-md overflow-hidden select-none"
                  @touchstart.passive="handleOpTouchStart"
                  @touchmove.prevent="handleOpTouchMove"
                  @touchend="handleOpTouchEnd"
                  @mousedown.prevent="handleOpMouseDown"
                  @mousemove.prevent="handleOpMouseMove"
                  @mouseup.prevent="handleOpMouseUp"
                  @mouseleave.prevent="handleOpMouseUp"
                >
                  <div class="p-4" v-if="currentOperation">
                    <div class="flex items-center justify-between mb-2">
                      <div class="text-base font-semibold text-gray-900">{{ formatOperationType(currentOperation.type) }}</div>
                      <span :class="getOperationStatusColor(currentOperation.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">{{ formatOperationStatus(currentOperation.status) }}</span>
                    </div>
                    <div class="space-y-1 text-sm">
                      <div class="flex justify-between"><span class="text-gray-500">{{ $t('warehouse.date') }}:</span><span class="text-gray-900">{{ formatDate(currentOperation.date) }}</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">{{ $t('warehouse.warehouse') }}:</span><span class="text-gray-900">{{ currentOperation.warehouse_name }}</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">{{ $t('warehouse.product') }}:</span><span class="text-gray-900">{{ currentOperation.product_name }}</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">{{ $t('warehouse.quantity') }}:</span><span class="text-gray-900">{{ currentOperation.quantity }} {{ currentOperation.unit }}</span></div>
                      <div class="flex justify-between"><span class="text-gray-500">{{ $t('warehouse.operator') }}:</span><span class="text-gray-900">{{ currentOperation.operator_name }}</span></div>
                    </div>
                  </div>
                </div>
                <div class="flex justify-between mt-3">
                  <button @click="previousOperation" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.previous') }}</button>
                  <button @click="nextOperation" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.next') }}</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add/Edit Warehouse Modal -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-2xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ showAddModal ? $t('warehouse.new_warehouse') : $t('warehouse.edit_warehouse') }}
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

          <form @submit.prevent="saveWarehouse" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('warehouse.name') }} *</label>
                <input
                  v-model="warehouseForm.name"
                  type="text"
                  required
                  class="input-field mt-1"
                  :placeholder="$t('warehouse.warehouse_name_placeholder')"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('warehouse.code') }} *</label>
                <input
                  v-model="warehouseForm.code"
                  type="text"
                  required
                  class="input-field mt-1"
                  :placeholder="$t('warehouse.warehouse_code_placeholder')"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('warehouse.type') }} *</label>
                <select v-model="warehouseForm.type" required class="input-field mt-1">
                  <option value="">{{ $t('warehouse.select_type') }}</option>
                  <option value="raw_materials">{{ $t('warehouse.warehouse_types.raw_materials') }}</option>
                  <option value="finished_goods">{{ $t('warehouse.warehouse_types.finished_goods') }}</option>
                  <option value="packaging">{{ $t('warehouse.warehouse_types.packaging') }}</option>
                  <option value="general">{{ $t('warehouse.warehouse_types.general') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('warehouse.status') }} *</label>
                <select v-model="warehouseForm.status" required class="input-field mt-1">
                  <option value="">{{ $t('warehouse.select_status') }}</option>
                  <option value="active">{{ $t('warehouse.status_types.active') }}</option>
                  <option value="inactive">{{ $t('warehouse.status_types.inactive') }}</option>
                  <option value="maintenance">{{ $t('warehouse.status_types.maintenance') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('warehouse.location') }} *</label>
                <input
                  v-model="warehouseForm.location"
                  type="text"
                  required
                  class="input-field mt-1"
                  :placeholder="$t('warehouse.location_placeholder')"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('warehouse.manager') }}</label>
                <input
                  v-model="warehouseForm.manager"
                  type="text"
                  class="input-field mt-1"
                  :placeholder="$t('warehouse.manager_placeholder')"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('warehouse.capacity') }} *</label>
                <input
                  v-model.number="warehouseForm.capacity"
                  type="number"
                  min="1"
                  required
                  class="input-field mt-1"
                  :placeholder="$t('warehouse.capacity_placeholder')"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('warehouse.capacity_unit') }} *</label>
                <select v-model="warehouseForm.capacity_unit" required class="input-field mt-1">
                  <option value="">{{ $t('warehouse.select_unit') }}</option>
                  <option value="kg">{{ $t('warehouse.kilogram') }}</option>
                  <option value="m3">{{ $t('warehouse.cubic_meter') }}</option>
                  <option value="pallet">{{ $t('warehouse.pallet') }}</option>
                  <option value="unit">{{ $t('warehouse.unit') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('warehouse.temperature_range') }}</label>
                <input
                  v-model="warehouseForm.temperature_range"
                  type="text"
                  class="input-field mt-1"
                  :placeholder="$t('warehouse.temperature_placeholder')"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('warehouse.humidity_range') }}</label>
                <input
                  v-model="warehouseForm.humidity_range"
                  type="text"
                  class="input-field mt-1"
                  :placeholder="$t('warehouse.humidity_placeholder')"
                />
              </div>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('common.description') }}</label>
              <textarea
                v-model="warehouseForm.description"
                class="input-field mt-1"
                rows="3"
                :placeholder="$t('warehouse.description_placeholder')"
              ></textarea>
            </div>

            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="closeModal"
                class="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md text-sm font-medium"
              >
                {{ $t('warehouse.cancel') }}
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
              >
                {{ saving ? $t('warehouse.saving') : $t('warehouse.save_warehouse') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Warehouse Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ $t('warehouse.warehouse_details') }} - {{ selectedWarehouse?.name }}
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

          <div v-if="selectedWarehouse" class="space-y-6">
            <!-- Warehouse Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('warehouse.basic_information') }}</h4>
                <dl class="space-y-2">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('warehouse.name') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedWarehouse.name }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('warehouse.code') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedWarehouse.code }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('warehouse.type') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ formatWarehouseType(selectedWarehouse.type) }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('warehouse.status') }}:</dt>
                    <dd class="text-sm">
                      <span :class="getStatusColor(selectedWarehouse.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                        {{ selectedWarehouse.status }}
                      </span>
                    </dd>
                  </div>
                </dl>
              </div>

              <div>
                <h4 class="text-md font-medium text-gray-900 mb-2">Location & Capacity</h4>
                <dl class="space-y-2">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('warehouse.location') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedWarehouse.location }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('warehouse.manager') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedWarehouse.manager || '-' }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('warehouse.capacity') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedWarehouse.capacity }} {{ selectedWarehouse.capacity_unit }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('warehouse.used') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedWarehouse.used_capacity }} {{ selectedWarehouse.capacity_unit }}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <!-- Capacity Usage -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-2">Capacity Usage</h4>
              <div class="w-full bg-gray-200 rounded-full h-4">
                <div
                  :class="getCapacityColor(selectedWarehouse.used_capacity / selectedWarehouse.capacity)"
                  class="h-4 rounded-full transition-all duration-300"
                  :style="{ width: `${(selectedWarehouse.used_capacity / selectedWarehouse.capacity) * 100}%` }"
                ></div>
              </div>
              <p class="text-sm text-gray-600 mt-2">
                {{ Math.round((selectedWarehouse.used_capacity / selectedWarehouse.capacity) * 100) }}% used
                ({{ selectedWarehouse.used_capacity }} / {{ selectedWarehouse.capacity }} {{ selectedWarehouse.capacity_unit }})
              </p>
            </div>

            <!-- Environmental Conditions -->
            <div v-if="selectedWarehouse.temperature_range || selectedWarehouse.humidity_range">
              <h4 class="text-md font-medium text-gray-900 mb-4">Environmental Conditions</h4>
              <div class="bg-gray-50 p-4 rounded-lg">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div v-if="selectedWarehouse.temperature_range">
                    <p class="text-sm font-medium text-gray-500">{{ $t('warehouse.temperature_range') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedWarehouse.temperature_range }}</p>
                  </div>
                  <div v-if="selectedWarehouse.humidity_range">
                    <p class="text-sm font-medium text-gray-500">{{ $t('warehouse.humidity_range') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedWarehouse.humidity_range }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Description -->
            <div v-if="selectedWarehouse.description">
              <h4 class="text-md font-medium text-gray-900 mb-2">Description</h4>
              <p class="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">{{ selectedWarehouse.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Inventory Overview Modal -->
    <div v-if="showInventoryModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-6xl shadow-lg rounded-md bg-white" @click.stop>
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">{{ $t('warehouse.inventory_overview') }}</h3>
            <button
              @click="showInventoryModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div class="space-y-6">
            <!-- Inventory Summary -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div class="bg-blue-50 p-4 rounded-lg">
                <div class="text-2xl font-bold text-blue-600">{{ totalItems }}</div>
                <div class="text-sm text-blue-800">{{ $t('warehouse.total_items') }}</div>
              </div>
              <div class="bg-green-50 p-4 rounded-lg">
                <div class="text-2xl font-bold text-green-600">{{ totalValue.toLocaleString() }}</div>
                <div class="text-sm text-green-800">{{ $t('warehouse.total_value') }} (₺)</div>
              </div>
              <div class="bg-yellow-50 p-4 rounded-lg">
                <div class="text-2xl font-bold text-yellow-600">{{ lowStockItems }}</div>
                <div class="text-sm text-yellow-800">{{ $t('warehouse.low_stock_items') }}</div>
              </div>
              <div class="bg-red-50 p-4 rounded-lg">
                <div class="text-2xl font-bold text-red-600">{{ outOfStockItems }}</div>
                <div class="text-sm text-red-800">{{ $t('warehouse.out_of_stock') }}</div>
              </div>
            </div>

          <!-- Inventory Table (Desktop) -->
          <div class="hidden lg:block overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.product') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.warehouse') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.quantity') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.unit_price') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.total_value') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.status') }}</th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('warehouse.last_updated') }}</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="item in inventoryItems" :key="item.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ item.product_name }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.warehouse_name }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ item.quantity }} {{ item.unit }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₺{{ item.unit_price }}</td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">₺{{ (item.quantity * item.unit_price).toLocaleString() }}</td>
                  <td class="px-6 py-4 whitespace-nowrap"><span :class="getStockStatusColor(item.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">{{ formatStockStatus(item.status) }}</span></td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ formatDate(item.last_updated) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Inventory Cards (Mobile Carousel) -->
          <div class="block lg:hidden">
            <div v-if="inventoryItems.length === 0" class="text-center text-gray-500 py-4">{{ $t('messages.no_data') }}</div>
            <div v-else class="relative">
              <div class="text-sm text-gray-500 mb-2 text-center">
                {{ $t('warehouse.showing_item') }} {{ currentInventoryIndex + 1 }} {{ $t('common.of') }} {{ inventoryItems.length }} — {{ $t('orders.swipe_hint') }}
              </div>
              <div
                class="bg-white rounded-lg shadow-md overflow-hidden select-none"
                @touchstart.passive="handleInvTouchStart"
                @touchmove.prevent="handleInvTouchMove"
                @touchend="handleInvTouchEnd"
                @mousedown.prevent="handleInvMouseDown"
                @mousemove.prevent="handleInvMouseMove"
                @mouseup.prevent="handleInvMouseUp"
                @mouseleave.prevent="handleInvMouseUp"
              >
                <div class="p-4" v-if="currentInventoryItem">
                  <div class="flex items-center justify-between mb-2">
                    <div class="text-base font-semibold text-gray-900">{{ currentInventoryItem.product_name }}</div>
                    <span :class="getStockStatusColor(currentInventoryItem.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">{{ formatStockStatus(currentInventoryItem.status) }}</span>
                  </div>
                  <div class="space-y-1 text-sm">
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('warehouse.warehouse') }}:</span><span class="text-gray-900">{{ currentInventoryItem.warehouse_name }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('warehouse.quantity') }}:</span><span class="text-gray-900">{{ currentInventoryItem.quantity }} {{ currentInventoryItem.unit }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('warehouse.unit_price') }}:</span><span class="text-gray-900">₺{{ currentInventoryItem.unit_price }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('warehouse.total_value') }}:</span><span class="text-gray-900">₺{{ (currentInventoryItem.quantity * currentInventoryItem.unit_price).toLocaleString() }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('warehouse.last_updated') }}:</span><span class="text-gray-900">{{ formatDate(currentInventoryItem.last_updated) }}</span></div>
                  </div>
                </div>
              </div>
              <div class="flex justify-between mt-3">
                <button @click="previousInventoryItem" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.previous') }}</button>
                <button @click="nextInventoryItem" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.next') }}</button>
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
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'

// Initialize i18n
const { t } = useI18n()

// Data
const warehouses = ref([])
const recentOperations = ref([])
const inventoryItems = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showDetailsModal = ref(false)
const showInventoryModal = ref(false)
const editingWarehouse = ref(null)
const selectedWarehouse = ref(null)

// Carousel state - Warehouses (mobile)
const currentWarehouseIndex = ref(0)
const whTouchStartX = ref(0)
const whTouchStartY = ref(0)
const whIsDragging = ref(false)

// Carousel state - Inventory (mobile)
const currentInventoryIndex = ref(0)
const invTouchStartX = ref(0)
const invTouchStartY = ref(0)
const invIsDragging = ref(false)

// Carousel state - Recent operations (mobile)
const currentOperationIndex = ref(0)
const opTouchStartX = ref(0)
const opTouchStartY = ref(0)
const opIsDragging = ref(false)

const warehouseForm = ref({
  name: '',
  code: '',
  type: '',
  status: '',
  location: '',
  manager: '',
  capacity: 0,
  capacity_unit: '',
  temperature_range: '',
  humidity_range: '',
  description: ''
})

// Computed
const filteredWarehouses = computed(() => {
  let filtered = warehouses.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(warehouse =>
      warehouse.name.toLowerCase().includes(query) ||
      warehouse.code.toLowerCase().includes(query) ||
      warehouse.location.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(warehouse => warehouse.status === statusFilter.value)
  }

  if (typeFilter.value) {
    filtered = filtered.filter(warehouse => warehouse.type === typeFilter.value)
  }

  return filtered
})

const currentWarehouse = computed(() => filteredWarehouses.value[currentWarehouseIndex.value] || null)
const currentInventoryItem = computed(() => inventoryItems.value[currentInventoryIndex.value] || null)
const currentOperation = computed(() => recentOperations.value[currentOperationIndex.value] || null)

const totalItems = computed(() => inventoryItems.value.length)
const totalValue = computed(() => inventoryItems.value.reduce((sum, item) => sum + (item.quantity * item.unit_price), 0))
const lowStockItems = computed(() => inventoryItems.value.filter(item => item.status === 'low_stock').length)
const outOfStockItems = computed(() => inventoryItems.value.filter(item => item.status === 'out_of_stock').length)

// Methods
function getStatusColor (status) {
  const colors = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-gray-100 text-gray-800',
    maintenance: 'bg-yellow-100 text-yellow-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

function getCapacityColor (usage) {
  if (usage >= 0.9) return 'bg-red-500'
  if (usage >= 0.7) return 'bg-yellow-500'
  return 'bg-green-500'
}

function getOperationStatusColor (status) {
  const colors = {
    completed: 'bg-green-100 text-green-800',
    pending: 'bg-yellow-100 text-yellow-800',
    failed: 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

function getStockStatusColor (status) {
  const colors = {
    in_stock: 'bg-green-100 text-green-800',
    low_stock: 'bg-yellow-100 text-yellow-800',
    out_of_stock: 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

function formatWarehouseType (type) {
  const types = {
    raw_materials: t('warehouse.warehouse_types.raw_materials'),
    finished_goods: t('warehouse.warehouse_types.finished_goods'),
    packaging: t('warehouse.warehouse_types.packaging'),
    general: t('warehouse.warehouse_types.general')
  }
  return types[type] || type
}

function formatWarehouseName (type) {
  const names = {
    raw_materials: t('warehouse.warehouse_names.raw_materials'),
    finished_goods: t('warehouse.warehouse_names.finished_goods'),
    packaging: t('warehouse.warehouse_names.packaging'),
    general: t('warehouse.warehouse_names.general')
  }
  return names[type] || type
}

function formatOperationType (type) {
  const types = {
    receipt: t('warehouse.operation_types.receipt'),
    issue: t('warehouse.operation_types.issue'),
    transfer: t('warehouse.operation_types.transfer'),
    adjustment: t('warehouse.operation_types.adjustment')
  }
  return types[type] || type
}

function formatOperationStatus (status) {
  const statuses = {
    completed: t('warehouse.operation_statuses.completed'),
    pending: t('warehouse.operation_statuses.pending'),
    failed: t('warehouse.operation_statuses.failed')
  }
  return statuses[status] || status
}

function formatStockStatus (status) {
  const statuses = {
    in_stock: t('warehouse.stock_statuses.in_stock'),
    low_stock: t('warehouse.stock_statuses.low_stock'),
    out_of_stock: t('warehouse.stock_statuses.out_of_stock')
  }
  return statuses[status] || status
}

function formatDate (dateString) {
  return new Date(dateString).toLocaleDateString('tr-TR')
}

async function loadWarehouses () {
  loading.value = true
  try {
    // Load data from API
    // Mock data removed
  } catch (error) {
    console.error('Error loading warehouses:', error)
  } finally {
    loading.value = false
  }
}

async function loadRecentOperations () {
  try {
    // Load data from API
    // Mock data removed
  } catch (error) {
    console.error('Error loading recent operations:', error)
  }
}

async function loadInventoryItems () {
  try {
    // Load data from API
    // Mock data removed
  } catch (error) {
    console.error('Error loading inventory items:', error)
  }
}

function viewWarehouse (warehouse) {
  selectedWarehouse.value = warehouse
  showDetailsModal.value = true
}

function editWarehouse (warehouse) {
  editingWarehouse.value = warehouse
  warehouseForm.value = {
    name: warehouse.name,
    code: warehouse.code,
    type: warehouse.type,
    status: warehouse.status,
    location: warehouse.location,
    manager: warehouse.manager,
    capacity: warehouse.capacity,
    capacity_unit: warehouse.capacity_unit,
    temperature_range: warehouse.temperature_range,
    humidity_range: warehouse.humidity_range,
    description: warehouse.description
  }
  showEditModal.value = true
}

function manageInventory (warehouse) {
  // TODO: Implement inventory management
  alert(`Inventory management for ${warehouse.name} - Coming Soon`)
}

async function saveWarehouse () {
  saving.value = true
  try {
    if (showAddModal.value) {
      // TODO: Implement create API call
      const newWarehouse = {
        id: Date.now(),
        ...warehouseForm.value,
        used_capacity: 0,
        item_count: 0,
        created_at: new Date().toISOString()
      }
      warehouses.value.unshift(newWarehouse)
    } else {
      // TODO: Implement update API call
      const index = warehouses.value.findIndex(w => w.id === editingWarehouse.value.id)
      if (index !== -1) {
        warehouses.value[index] = {
          ...warehouses.value[index],
          ...warehouseForm.value
        }
      }
    }
    closeModal()
  } catch (error) {
    console.error('Error saving warehouse:', error)
  } finally {
    saving.value = false
  }
}

function closeModal () {
  showAddModal.value = false
  showEditModal.value = false
  showDetailsModal.value = false
  showInventoryModal.value = false
  editingWarehouse.value = null
  selectedWarehouse.value = null
  warehouseForm.value = {
    name: '',
    code: '',
    type: '',
    status: '',
    location: '',
    manager: '',
    capacity: 0,
    capacity_unit: '',
    temperature_range: '',
    humidity_range: '',
    description: ''
  }
}

// Carousel navigation - Warehouses
function nextWarehouse () {
  if (filteredWarehouses.value.length === 0) return
  currentWarehouseIndex.value = (currentWarehouseIndex.value + 1) % filteredWarehouses.value.length
}

function previousWarehouse () {
  if (filteredWarehouses.value.length === 0) return
  currentWarehouseIndex.value = (currentWarehouseIndex.value - 1 + filteredWarehouses.value.length) % filteredWarehouses.value.length
}

function handleWhTouchStart (e) {
  const touch = e.touches[0]
  whTouchStartX.value = touch.clientX
  whTouchStartY.value = touch.clientY
  whIsDragging.value = true
}

function handleWhTouchMove (e) {
  // intentionally left blank (no-op)
}

function handleWhTouchEnd (e) {
  if (!whIsDragging.value) return
  const touch = e.changedTouches[0]
  const dx = touch.clientX - whTouchStartX.value
  whIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextWarehouse()
  else if (dx > threshold) previousWarehouse()
}

function handleWhMouseDown (e) {
  whTouchStartX.value = e.clientX
  whTouchStartY.value = e.clientY
  whIsDragging.value = true
}

function handleWhMouseMove (e) {
  // intentionally left blank (no-op)
}

function handleWhMouseUp (e) {
  if (!whIsDragging.value) return
  const dx = e.clientX - whTouchStartX.value
  whIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextWarehouse()
  else if (dx > threshold) previousWarehouse()
}

// Carousel navigation - Inventory
function nextInventoryItem () {
  if (inventoryItems.value.length === 0) return
  currentInventoryIndex.value = (currentInventoryIndex.value + 1) % inventoryItems.value.length
}

function previousInventoryItem () {
  if (inventoryItems.value.length === 0) return
  currentInventoryIndex.value = (currentInventoryIndex.value - 1 + inventoryItems.value.length) % inventoryItems.value.length
}

function handleInvTouchStart (e) {
  const touch = e.touches[0]
  invTouchStartX.value = touch.clientX
  invTouchStartY.value = touch.clientY
  invIsDragging.value = true
}

function handleInvTouchMove (e) {
  // intentionally left blank (no-op)
}

function handleInvTouchEnd (e) {
  if (!invIsDragging.value) return
  const touch = e.changedTouches[0]
  const dx = touch.clientX - invTouchStartX.value
  invIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextInventoryItem()
  else if (dx > threshold) previousInventoryItem()
}

function handleInvMouseDown (e) {
  invTouchStartX.value = e.clientX
  invTouchStartY.value = e.clientY
  invIsDragging.value = true
}

function handleInvMouseMove (e) {
  // intentionally left blank (no-op)
}

function handleInvMouseUp (e) {
  if (!invIsDragging.value) return
  const dx = e.clientX - invTouchStartX.value
  invIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextInventoryItem()
  else if (dx > threshold) previousInventoryItem()
}

// Carousel navigation - Operations
function nextOperation () {
  if (recentOperations.value.length === 0) return
  currentOperationIndex.value = (currentOperationIndex.value + 1) % recentOperations.value.length
}

function previousOperation () {
  if (recentOperations.value.length === 0) return
  currentOperationIndex.value = (currentOperationIndex.value - 1 + recentOperations.value.length) % recentOperations.value.length
}

function handleOpTouchStart (e) {
  const touch = e.touches[0]
  opTouchStartX.value = touch.clientX
  opTouchStartY.value = touch.clientY
  opIsDragging.value = true
}

function handleOpTouchMove (e) {
  // intentionally left blank (no-op)
}

function handleOpTouchEnd (e) {
  if (!opIsDragging.value) return
  const touch = e.changedTouches[0]
  const dx = touch.clientX - opTouchStartX.value
  opIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextOperation()
  else if (dx > threshold) previousOperation()
}

function handleOpMouseDown (e) {
  opTouchStartX.value = e.clientX
  opTouchStartY.value = e.clientY
  opIsDragging.value = true
}

function handleOpMouseMove (e) {
  // intentionally left blank (no-op)
}

function handleOpMouseUp (e) {
  if (!opIsDragging.value) return
  const dx = e.clientX - opTouchStartX.value
  opIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextOperation()
  else if (dx > threshold) previousOperation()
}

// ESC to close modals
function handleKeydown (event) {
  if (event.key === 'Escape') {
    closeModal()
  }
}

// Lifecycle
onMounted(() => {
  loadWarehouses()
  loadRecentOperations()
  loadInventoryItems()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>
