<template>
  <div>
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-gray-900">{{ $t('products.title') }}</h1>
          <button
            @click="showAddModal = true"
            class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            {{ $t('products.add_product') }}
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
                  :placeholder="$t('products.search_placeholder')"
                  class="input-field"
                />
              </div>
              <div class="flex gap-2">
                <select v-model="typeFilter" class="input-field">
                  <option value="">{{ $t('products.all_types') }}</option>
                  <option value="poset">{{ $t('products.types.poset') }}</option>
                  <option value="deterjan">{{ $t('products.types.deterjan') }}</option>
                  <option value="al-sat">{{ $t('products.types.al-sat') }}</option>
                </select>
                <select v-model="statusFilter" class="input-field">
                  <option value="">{{ $t('products.all_status') }}</option>
                  <option value="active">{{ $t('products.status.active') }}</option>
                  <option value="inactive">{{ $t('products.status.inactive') }}</option>
                </select>
                <button
                  @click="loadProducts"
                  class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  {{ $t('common.refresh') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Products Content -->
          <div class="bg-white shadow overflow-hidden sm:rounded-md">
            <div v-if="loading" class="p-6 text-center">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p class="mt-2 text-gray-600">{{ $t('products.loading') }}</p>
            </div>

            <div v-else-if="products.length === 0" class="p-6 text-center text-gray-500">
              {{ $t('products.no_products_found') }}
            </div>

            <div v-else class="space-y-4">
              <!-- Desktop Table View -->
              <div class="hidden lg:block overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('products.code') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.name') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('products.type') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('products.unit') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('products.efficiency') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.status') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('products.created') }}
                    </th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.actions') }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="product in filteredProducts" :key="product.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {{ product.code }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ product.name }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="getTypeColor(product.product_type)"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      >
                        {{ product.product_type }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ product.unit }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ product.efficiency ? `${product.efficiency}%` : '-' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="product.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      >
                        {{ product.is_active ? $t('products.status.active') : $t('products.status.inactive') }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(product.created_at) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        @click="editProduct(product)"
                        class="text-primary-600 hover:text-primary-900 mr-3"
                      >
                        {{ $t('common.edit') }}
                      </button>
                      <button
                        @click="viewFormulas(product)"
                        class="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        {{ $t('products.formulas') }}
                      </button>
                      <button
                        @click="deleteProduct(product)"
                        class="text-red-600 hover:text-red-900"
                      >
                        {{ $t('common.delete') }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              </div>

              <!-- Mobile Card View - Carousel -->
              <div class="block lg:hidden">
                <!-- Carousel Header -->
                <div class="flex items-center justify-between mb-4 px-4">
                  <div class="text-xs text-gray-500">
                    {{ $t('products.showing_product') }} {{ currentProductIndex + 1 }} {{ $t('common.of') }} {{ filteredProducts.length }}
                  </div>
                  <div class="flex items-center space-x-2">
                    <!-- Swipe hint -->
                    <div class="text-xs text-gray-400 hidden sm:block">
                      {{ $t('products.swipe_hint') }}
                    </div>
                    <!-- Previous Button -->
                    <button
                      @click="previousProduct"
                      :disabled="currentProductIndex === 0"
                      class="p-2 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                      </svg>
                    </button>
                    <!-- Next Button -->
                    <button
                      @click="nextProduct"
                      :disabled="currentProductIndex >= filteredProducts.length - 1"
                      class="p-2 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      <svg class="w-4 h-4 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- Carousel Card -->
                <div class="relative">
                  <div
                    v-if="filteredProducts.length > 0"
                    @touchstart="handleTouchStart"
                    @touchmove="handleTouchMove"
                    @touchend="handleTouchEnd"
                    @mousedown="handleMouseDown"
                    @mousemove="handleMouseMove"
                    @mouseup="handleMouseUp"
                    @mouseleave="handleMouseUp"
                    class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm transition-all duration-300 ease-in-out select-none carousel-card cursor-grab active:cursor-grabbing mx-4"
                  >
                    <!-- Product Header -->
                    <div class="flex justify-between items-start mb-3">
                      <div class="flex-1 min-w-0">
                        <h3 class="text-sm font-semibold text-gray-900 truncate">{{ currentProduct.name }}</h3>
                        <p class="text-xs text-gray-500 truncate">{{ currentProduct.code }}</p>
                      </div>
                      <span
                        :class="getStatusColor(currentProduct.is_active ? 'active' : 'inactive')"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ml-2 flex-shrink-0"
                      >
                        {{ currentProduct.is_active ? $t('products.status.active') : $t('products.status.inactive') }}
                      </span>
                    </div>

                    <!-- Product Details - Kompakt Grid -->
                    <div class="grid grid-cols-2 gap-2 text-xs text-gray-600 mb-3">
                      <div class="flex flex-col">
                        <span class="font-medium text-gray-500">{{ $t('products.type') }}</span>
                        <span class="font-semibold">{{ $t(`products.types.${currentProduct.product_type}`) }}</span>
                      </div>
                      <div class="flex flex-col">
                        <span class="font-medium text-gray-500">{{ $t('products.unit') }}</span>
                        <span class="font-semibold text-gray-900">{{ currentProduct.unit || $t('products.no_unit') }}</span>
                      </div>
                      <div class="flex flex-col">
                        <span class="font-medium text-gray-500">{{ $t('products.efficiency') }}</span>
                        <span class="font-semibold">{{ currentProduct.efficiency ? `${currentProduct.efficiency}%` : $t('products.no_efficiency') }}</span>
                      </div>
                      <div class="flex flex-col">
                        <span class="font-medium text-gray-500">{{ $t('products.created') }}</span>
                        <span class="font-semibold">{{ formatDate(currentProduct.created_at) }}</span>
                      </div>
                    </div>

                    <!-- Product Description -->
                    <div v-if="currentProduct.description" class="mb-3 p-2 bg-gray-50 rounded text-xs">
                      <div class="font-medium text-gray-700 mb-1">{{ $t('common.description') }}</div>
                      <div class="text-gray-600">{{ currentProduct.description }}</div>
                    </div>

                    <!-- Actions - Kompakt -->
                    <div class="flex flex-wrap gap-1">
                      <button
                        @click="viewFormulas(currentProduct)"
                        class="text-blue-600 hover:text-blue-900 text-xs font-medium px-2 py-1 rounded hover:bg-blue-50"
                      >
                        {{ $t('products.formulas') }}
                      </button>
                      <button
                        @click="editProduct(currentProduct)"
                        class="text-primary-600 hover:text-primary-900 text-xs font-medium px-2 py-1 rounded hover:bg-primary-50"
                      >
                        {{ $t('common.edit') }}
                      </button>
                      <button
                        @click="deleteProduct(currentProduct)"
                        class="text-red-600 hover:text-red-900 text-xs font-medium px-2 py-1 rounded hover:bg-red-50"
                      >
                        {{ $t('common.delete') }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add/Edit Product Modal -->
    <div
      v-if="showAddModal || showEditModal"
      @click="closeModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div
        @click.stop
        class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white"
      >
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">
            {{ showAddModal ? $t('products.add_product') : $t('products.edit_product') }}
          </h3>

          <form @submit.prevent="saveProduct" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('products.code') }} *</label>
              <input
                v-model="productForm.code"
                type="text"
                required
                class="input-field mt-1"
                :placeholder="$t('products.code_placeholder')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('common.name') }} *</label>
              <input
                v-model="productForm.name"
                type="text"
                required
                class="input-field mt-1"
                :placeholder="$t('products.name_placeholder')"
              />
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('products.type') }} *</label>
              <select v-model="productForm.product_type" required class="input-field mt-1">
                <option value="">{{ $t('products.select_type') }}</option>
                <option value="poset">{{ $t('products.types.poset') }}</option>
                <option value="deterjan">{{ $t('products.types.deterjan') }}</option>
                <option value="al-sat">{{ $t('products.types.al-sat') }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('products.unit') }} *</label>
              <select v-model="productForm.unit" required class="input-field mt-1">
                <option value="">{{ $t('products.select_unit') }}</option>
                <option value="kg">{{ $t('products.units.kg') }}</option>
                <option value="adet">{{ $t('products.units.adet') }}</option>
                <option value="m3">{{ $t('products.units.m3') }}</option>
              </select>
            </div>

            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('products.efficiency') }} (%)</label>
              <input
                v-model="productForm.efficiency"
                type="number"
                step="0.01"
                min="0"
                max="100"
                class="input-field mt-1"
                :placeholder="$t('products.efficiency_placeholder')"
              />
            </div>

            <div>
              <label class="flex items-center">
                <input
                  v-model="productForm.is_active"
                  type="checkbox"
                  class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                />
                <span class="ml-2 text-sm text-gray-700">{{ $t('products.status.active') }}</span>
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
                {{ saving ? $t('products.saving') : $t('common.save') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Formulas Modal -->
    <div
      v-if="showFormulasModal"
      @click="closeFormulasModal"
      class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50"
    >
      <div
        @click.stop
        class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white"
      >
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              Formulas for {{ selectedProduct?.name }}
            </h3>
            <button
              @click="showFormulasModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div class="mb-4">
            <button
              @click="showAddFormulaModal = true"
              class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Add Formula
            </button>
          </div>

          <div v-if="formulas.length === 0" class="text-center text-gray-500 py-8">
            No formulas found for this product.
          </div>
          <div v-if="formulas.length > 0" class="hidden lg:block overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Version
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Valid From
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Valid To
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <tr v-for="formula in formulas" :key="formula.id" class="hover:bg-gray-50">
                  <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {{ formula.version }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(formula.valid_from) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formula.valid_to ? formatDate(formula.valid_to) : 'No end date' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span
                      :class="formula.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                      class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    >
                      {{ formula.is_active ? 'Active' : 'Inactive' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {{ formatDate(formula.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      @click="viewFormulaDetails(formula)"
                      class="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      View
                    </button>
                    <button
                      @click="editFormula(formula)"
                      class="text-primary-600 hover:text-primary-900 mr-3"
                    >
                      Edit
                    </button>
                    <button
                      @click="deleteFormula(formula)"
                      class="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-if="formulas.length > 0" class="block lg:hidden">
            <div v-if="formulas.length > 0" class="space-y-4">
              <!-- Carousel Header -->
              <div class="flex items-center justify-between">
                <div class="text-sm text-gray-500">
                  {{ $t('products.showing_formula') }} {{ currentFormulaIndex + 1 }} {{ $t('common.of') }} {{ formulas.length }}
                </div>
                <div class="flex space-x-2">
                  <button
                    @click="previousFormula"
                    :disabled="currentFormulaIndex === 0"
                    class="p-2 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
                    </svg>
                  </button>
                  <button
                    @click="nextFormula"
                      :disabled="currentFormulaIndex === formulas.length - 1"
                    class="p-2 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                    </svg>
                  </button>
                </div>
              </div>

              <!-- Swipe Hint -->
              <div class="text-center text-xs text-gray-400 mb-2">
                {{ $t('products.swipe_hint') }}
              </div>

              <!-- Formula Card -->
              <div
                v-if="currentFormula"
                @touchstart="handleFormulaTouchStart"
                @touchmove="handleFormulaTouchMove"
                @touchend="handleFormulaTouchEnd"
                @mousedown="handleFormulaMouseDown"
                @mousemove="handleFormulaMouseMove"
                @mouseup="handleFormulaMouseUp"
                @mouseleave="handleFormulaMouseUp"
                class="bg-white rounded-lg shadow-md p-4 border border-gray-200 cursor-grab active:cursor-grabbing select-none"
              >
                <!-- Formula Header -->
                <div class="flex items-center justify-between mb-3">
                  <h4 class="text-lg font-semibold text-gray-900">
                    Version {{ currentFormula.version }}
                  </h4>
                  <span
                    :class="currentFormula.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                    class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                  >
                    {{ currentFormula.is_active ? $t('products.status.active') : $t('products.status.inactive') }}
                  </span>
                </div>

                <!-- Formula Details -->
                <div class="space-y-3">
                  <div class="flex justify-between">
                    <span class="text-sm font-medium text-gray-500">{{ $t('products.valid_from') }}:</span>
                    <span class="text-sm text-gray-900">{{ formatDate(currentFormula.valid_from) }}</span>
                  </div>

                  <div class="flex justify-between">
                    <span class="text-sm font-medium text-gray-500">{{ $t('products.valid_to') }}:</span>
                    <span class="text-sm text-gray-900">
                      {{ currentFormula.valid_to ? formatDate(currentFormula.valid_to) : $t('products.no_end_date') }}
                    </span>
                  </div>

                  <div class="flex justify-between">
                    <span class="text-sm font-medium text-gray-500">{{ $t('products.created') }}:</span>
                    <span class="text-sm text-gray-900">{{ formatDate(currentFormula.created_at) }}</span>
                  </div>
                </div>

                <!-- Formula Actions -->
                <div class="flex justify-end space-x-2 mt-4 pt-3 border-t border-gray-200">
                  <button
                    @click="viewFormulaDetails(currentFormula)"
                    class="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  >
                    {{ $t('common.view') }}
                  </button>
                  <button
                    @click="editFormula(currentFormula)"
                    class="px-3 py-1 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700"
                  >
                    {{ $t('common.edit') }}
                  </button>
                  <button
                    @click="deleteFormula(currentFormula)"
                    class="px-3 py-1 text-sm bg-red-600 text-white rounded-md hover:bg-red-700"
                  >
                    {{ $t('common.delete') }}
                  </button>
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

// Data
const products = ref([])
const formulas = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const typeFilter = ref('')
const statusFilter = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showFormulasModal = ref(false)
const showAddFormulaModal = ref(false)
const editingProduct = ref(null)
const selectedProduct = ref(null)

// Carousel state
const currentProductIndex = ref(0)
const touchStartX = ref(0)
const touchStartY = ref(0)
const touchEndX = ref(0)
const touchEndY = ref(0)
const isDragging = ref(false)

// Formulas carousel state
const currentFormulaIndex = ref(0)
const formulaTouchStartX = ref(0)
const formulaTouchStartY = ref(0)
const formulaTouchEndX = ref(0)
const formulaTouchEndY = ref(0)
const formulaIsDragging = ref(false)

const productForm = ref({
  code: '',
  name: '',
  product_type: '',
  unit: '',
  efficiency: null,
  is_active: true
})

// Computed
const filteredProducts = computed(() => {
  let filtered = products.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(product =>
      product.name.toLowerCase().includes(query) ||
      product.code.toLowerCase().includes(query)
    )
  }

  if (typeFilter.value) {
    filtered = filtered.filter(product => product.product_type === typeFilter.value)
  }

  if (statusFilter.value) {
    const isActive = statusFilter.value === 'active'
    filtered = filtered.filter(product => product.is_active === isActive)
  }

  // Sort by creation date (newest first)
  return filtered.sort((a, b) => {
    return new Date(b.created_at) - new Date(a.created_at)
  })
})

// Current product for carousel
const currentProduct = computed(() => {
  return filteredProducts.value[currentProductIndex.value] || null
})

// Formulas computed properties
const sortedFormulas = computed(() => {
  return [...formulas.value].sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
})

const currentFormula = computed(() => {
  return sortedFormulas.value[currentFormulaIndex.value] || null
})

// Carousel functions
function nextProduct () {
  if (currentProductIndex.value < filteredProducts.value.length - 1) {
    currentProductIndex.value++
  }
}

function previousProduct () {
  if (currentProductIndex.value > 0) {
    currentProductIndex.value--
  }
}

// Formulas carousel functions
function nextFormula () {
  if (currentFormulaIndex.value < formulas.value.length - 1) {
    currentFormulaIndex.value++
  }
}

function previousFormula () {
  if (currentFormulaIndex.value > 0) {
    currentFormulaIndex.value--
  }
}

// Touch/swipe handlers
function handleTouchStart (event) {
  const touch = event.touches[0]
  touchStartX.value = touch.clientX
  touchStartY.value = touch.clientY
  isDragging.value = false
}

function handleTouchMove (event) {
  if (!touchStartX.value || !touchStartY.value) return

  const touch = event.touches[0]
  const deltaX = touch.clientX - touchStartX.value
  const deltaY = touch.clientY - touchStartY.value

  // Check if it's a horizontal swipe (more horizontal than vertical)
  if (Math.abs(deltaX) > Math.abs(deltaY)) {
    isDragging.value = true
    event.preventDefault() // Prevent scrolling
  }
}

function handleTouchEnd (event) {
  if (!isDragging.value) return

  const touch = event.changedTouches[0]
  touchEndX.value = touch.clientX
  touchEndY.value = touch.clientY

  const deltaX = touchEndX.value - touchStartX.value
  const deltaY = touchEndY.value - touchStartY.value

  // Minimum swipe distance (in pixels)
  const minSwipeDistance = 50

  // Check if it's a valid horizontal swipe
  if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
    if (deltaX > 0) {
      // Swipe right - go to previous product
      previousProduct()
    } else {
      // Swipe left - go to next product
      nextProduct()
    }
  }

  // Reset touch state
  touchStartX.value = 0
  touchStartY.value = 0
  touchEndX.value = 0
  touchEndY.value = 0
  isDragging.value = false
}

// Formulas touch/swipe handlers
function handleFormulaTouchStart (event) {
  const touch = event.touches[0]
  formulaTouchStartX.value = touch.clientX
  formulaTouchStartY.value = touch.clientY
  formulaIsDragging.value = false
}

function handleFormulaTouchMove (event) {
  if (!formulaTouchStartX.value || !formulaTouchStartY.value) return

  const touch = event.touches[0]
  const deltaX = touch.clientX - formulaTouchStartX.value
  const deltaY = touch.clientY - formulaTouchStartY.value

  // Check if it's a horizontal swipe (more horizontal than vertical)
  if (Math.abs(deltaX) > Math.abs(deltaY)) {
    formulaIsDragging.value = true
    event.preventDefault() // Prevent scrolling
  }
}

function handleFormulaTouchEnd (event) {
  if (!formulaIsDragging.value) return

  const touch = event.changedTouches[0]
  formulaTouchEndX.value = touch.clientX
  formulaTouchEndY.value = touch.clientY

  const deltaX = formulaTouchEndX.value - formulaTouchStartX.value
  const deltaY = formulaTouchEndY.value - formulaTouchStartY.value

  // Minimum swipe distance (in pixels)
  const minSwipeDistance = 50

  // Check if it's a valid horizontal swipe
  if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
    if (deltaX > 0) {
      // Swipe right - go to previous formula
      previousFormula()
    } else {
      // Swipe left - go to next formula
      nextFormula()
    }
  }

  // Reset touch state
  formulaTouchStartX.value = 0
  formulaTouchStartY.value = 0
  formulaTouchEndX.value = 0
  formulaTouchEndY.value = 0
  formulaIsDragging.value = false
}

// Mouse handlers for desktop testing
function handleMouseDown (event) {
  touchStartX.value = event.clientX
  touchStartY.value = event.clientY
  isDragging.value = false
}

function handleMouseMove (event) {
  if (!touchStartX.value || !touchStartY.value) return

  const deltaX = event.clientX - touchStartX.value
  const deltaY = event.clientY - touchStartY.value

  // Check if it's a horizontal drag (more horizontal than vertical)
  if (Math.abs(deltaX) > Math.abs(deltaY)) {
    isDragging.value = true
  }
}

function handleMouseUp (event) {
  if (!isDragging.value) return

  touchEndX.value = event.clientX
  touchEndY.value = event.clientY

  const deltaX = touchEndX.value - touchStartX.value
  const deltaY = touchEndY.value - touchStartY.value

  // Minimum drag distance (in pixels)
  const minDragDistance = 50

  // Check if it's a valid horizontal drag
  if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minDragDistance) {
    if (deltaX > 0) {
      // Drag right - go to previous product
      previousProduct()
    } else {
      // Drag left - go to next product
      nextProduct()
    }
  }

  // Reset drag state
  touchStartX.value = 0
  touchStartY.value = 0
  touchEndX.value = 0
  touchEndY.value = 0
  isDragging.value = false
}

// Formulas mouse handlers for desktop testing
function handleFormulaMouseDown (event) {
  formulaTouchStartX.value = event.clientX
  formulaTouchStartY.value = event.clientY
  formulaIsDragging.value = false
}

function handleFormulaMouseMove (event) {
  if (!formulaTouchStartX.value || !formulaTouchStartY.value) return

  const deltaX = event.clientX - formulaTouchStartX.value
  const deltaY = event.clientY - formulaTouchStartY.value

  // Check if it's a horizontal drag (more horizontal than vertical)
  if (Math.abs(deltaX) > Math.abs(deltaY)) {
    formulaIsDragging.value = true
  }
}

function handleFormulaMouseUp (event) {
  if (!formulaIsDragging.value) return

  formulaTouchEndX.value = event.clientX
  formulaTouchEndY.value = event.clientY

  const deltaX = formulaTouchEndX.value - formulaTouchStartX.value
  const deltaY = formulaTouchEndY.value - formulaTouchStartY.value

  // Minimum drag distance (in pixels)
  const minDragDistance = 50

  // Check if it's a valid horizontal drag
  if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minDragDistance) {
    if (deltaX > 0) {
      // Drag right - go to previous formula
      previousFormula()
    } else {
      // Drag left - go to next formula
      nextFormula()
    }
  }

  // Reset drag state
  formulaTouchStartX.value = 0
  formulaTouchStartY.value = 0
  formulaTouchEndX.value = 0
  formulaTouchEndY.value = 0
  formulaIsDragging.value = false
}

// Methods
function getTypeColor (type) {
  const colors = {
    poset: 'bg-blue-100 text-blue-800',
    deterjan: 'bg-green-100 text-green-800',
    'al-sat': 'bg-purple-100 text-purple-800'
  }
  return colors[type] || 'bg-gray-100 text-gray-800'
}

function getStatusColor (status) {
  const colors = {
    active: 'bg-green-100 text-green-800',
    inactive: 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

async function loadProducts () {
  loading.value = true
  try {
    // Mock data for now
    products.value = [
      {
        id: 1,
        code: 'POS001',
        name: 'Market Poşeti 30x40',
        product_type: 'poset',
        unit: 'kg',
        efficiency: 95.5,
        is_active: true,
        created_at: '2024-01-15T10:30:00Z'
      },
      {
        id: 2,
        code: 'DET001',
        name: 'Bulaşık Deterjanı',
        product_type: 'deterjan',
        unit: 'kg',
        efficiency: 92.0,
        is_active: true,
        created_at: '2024-01-20T14:15:00Z'
      },
      {
        id: 3,
        code: 'ALS001',
        name: 'Temizlik Malzemesi',
        product_type: 'al-sat',
        unit: 'adet',
        efficiency: 88.5,
        is_active: false,
        created_at: '2024-01-25T09:45:00Z'
      }
    ]

    // Mock formulas data
    formulas.value = [
      {
        id: 1,
        product_id: 1,
        version: '1.0',
        valid_from: '2024-01-01',
        valid_to: null,
        is_active: true,
        created_at: '2024-01-15T10:30:00Z'
      },
      {
        id: 2,
        product_id: 1,
        version: '1.1',
        valid_from: '2024-02-01',
        valid_to: null,
        is_active: true,
        created_at: '2024-02-01T14:15:00Z'
      },
      {
        id: 3,
        product_id: 2,
        version: '2.0',
        valid_from: '2024-01-20',
        valid_to: '2024-12-31',
        is_active: true,
        created_at: '2024-01-20T09:45:00Z'
      }
    ]

    console.log('Formulas loaded:', formulas.value.length)
  } catch (error) {
    console.error('Error loading products:', error)
  } finally {
    loading.value = false
  }
}

function editProduct (product) {
  editingProduct.value = product
  productForm.value = { ...product }
  showEditModal.value = true
}

function viewFormulas (product) {
  selectedProduct.value = product
  loadFormulas(product.id)
  showFormulasModal.value = true
}

async function loadFormulas (productId) {
  try {
    // Mock data for now
    formulas.value = [
      {
        id: 1,
        product_id: productId,
        version: '1.0',
        valid_from: '2024-01-01',
        valid_to: null,
        is_active: true,
        created_at: '2024-01-15T10:30:00Z'
      },
      {
        id: 2,
        product_id: productId,
        version: '1.1',
        valid_from: '2024-02-01',
        valid_to: null,
        is_active: false,
        created_at: '2024-02-01T14:15:00Z'
      }
    ]
  } catch (error) {
    console.error('Error loading formulas:', error)
  }
}

function viewFormulaDetails (formula) {
  // TODO: Implement formula details view
  alert(`Formula ${formula.version} details`)
}

function editFormula (formula) {
  // TODO: Implement formula edit
  alert(`Edit formula ${formula.version}`)
}

function deleteFormula (formula) {
  if (confirm(`Are you sure you want to delete formula ${formula.version}?`)) {
    formulas.value = formulas.value.filter(f => f.id !== formula.id)
  }
}

async function deleteProduct (product) {
  if (confirm(`Are you sure you want to delete ${product.name}?`)) {
    try {
      // TODO: Implement delete API call
      products.value = products.value.filter(p => p.id !== product.id)
    } catch (error) {
      console.error('Error deleting product:', error)
    }
  }
}

async function saveProduct () {
  saving.value = true
  try {
    if (showAddModal.value) {
      // TODO: Implement create API call
      const newProduct = {
        id: Date.now(),
        ...productForm.value,
        created_at: new Date().toISOString()
      }
      products.value.push(newProduct)
    } else {
      // TODO: Implement update API call
      const index = products.value.findIndex(p => p.id === editingProduct.value.id)
      if (index !== -1) {
        products.value[index] = { ...products.value[index], ...productForm.value }
      }
    }
    closeModal()
  } catch (error) {
    console.error('Error saving product:', error)
  } finally {
    saving.value = false
  }
}

function closeModal () {
  showAddModal.value = false
  showEditModal.value = false
  showFormulasModal.value = false
  showAddFormulaModal.value = false
  editingProduct.value = null
  selectedProduct.value = null
  productForm.value = {
    code: '',
    name: '',
    product_type: '',
    unit: '',
    efficiency: null,
    is_active: true
  }
}

function closeFormulasModal () {
  showFormulasModal.value = false
  showAddFormulaModal.value = false
  selectedProduct.value = null
}

function formatDate (dateString) {
  return new Date(dateString).toLocaleDateString('tr-TR')
}

// Watch for filter changes to reset carousel index
watch([searchQuery, typeFilter, statusFilter], () => {
  currentProductIndex.value = 0
})

// ESC key handler for modals
function handleKeydown (event) {
  if (event.key === 'Escape') {
    if (showFormulasModal.value) {
      closeFormulasModal()
    } else if (showEditModal.value) {
      showEditModal.value = false
    } else if (showAddModal.value) {
      showAddModal.value = false
    }
  }
}

// Lifecycle
onMounted(() => {
  loadProducts()
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>
