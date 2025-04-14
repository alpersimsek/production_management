<template>
  <div>
    <!-- Loading state -->
    <div v-if="loading" class="mt-6 flex justify-center">
      <svg class="h-8 w-8 animate-spin text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Presets list -->
    <div v-if="!loading && productGroups" class="mt-8 space-y-8">
      <!-- Product section -->
      <div v-for="(group, productId) in productGroups" :key="productId" class="space-y-4">
        <!-- Product header - clickable -->
        <div
          class="bg-gray-50 px-4 py-3 rounded-lg border border-gray-200 flex justify-between items-center cursor-pointer hover:bg-gray-100"
          @click="toggleProductExpand(productId)"
        >
          <div>
            <h2 class="text-xl font-semibold text-gray-800">
              {{ group.product.name }}
            </h2>
            <p class="text-sm text-gray-500">{{ group.presets.length }} preset{{ group.presets.length !== 1 ? 's' : '' }}</p>
          </div>
          <!-- Expansion indicator -->
          <svg
            class="h-5 w-5 text-gray-500 transition-transform duration-200"
            :class="{ 'rotate-180': isProductExpanded(productId) }"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </div>

        <!-- Presets for this product - only show when expanded -->
        <div v-if="isProductExpanded(productId)" class="space-y-4">
          <div v-if="group.presets.length === 0" class="bg-white overflow-hidden shadow rounded-lg ml-4 p-6 text-center">
            <p class="text-sm text-gray-500">No presets for this product yet.</p>
            <button
              type="button"
              @click="$emit('addPreset', productId)"
              class="mt-3 inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
            >
              <PlusIcon class="h-4 w-4 mr-1" />
              Add Preset
            </button>
          </div>
          <div v-for="preset in group.presets" :key="preset.id" class="bg-white overflow-hidden shadow rounded-lg ml-4">
            <div
              class="px-4 py-5 sm:px-6 flex justify-between items-center cursor-pointer hover:bg-gray-50"
              @click="togglePresetExpand(preset)"
            >
              <div>
                <h3 class="text-lg leading-6 font-medium text-gray-900">{{ preset.name }}</h3>
                <p class="mt-1 max-w-2xl text-sm text-gray-500">
                  Header: {{ preset.header }}
                </p>
              </div>
              <div class="flex space-x-2">
                <button
                  @click.stop="$emit('editPreset', preset)"
                  class="text-indigo-600 hover:text-indigo-900"
                  title="Edit preset"
                >
                  <PencilIcon class="h-5 w-5" />
                </button>
                <button
                  @click.stop="$emit('deletePreset', preset)"
                  class="text-red-600 hover:text-red-900"
                  title="Delete preset"
                >
                  <TrashIcon class="h-5 w-5" />
                </button>
              </div>
            </div>

            <!-- Preset rules section (expandable) -->
            <div v-if="preset.expanded" class="border-t border-gray-200">
              <div class="px-4 py-3 sm:px-6 bg-gray-50 flex justify-between items-center">
                <h4 class="text-md font-medium text-gray-700">Rules</h4>
                <button
                  @click.stop="$emit('addRuleToPreset', preset.id)"
                  class="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
                >
                  <PlusIcon class="h-4 w-4 mr-1" />
                  Add Rule
                </button>
              </div>

              <div class="px-4 py-5 sm:p-6">
                <div v-if="preset.rules && preset.rules.length > 0" class="divide-y divide-gray-200">
                  <div v-for="rule in preset.rules" :key="`${preset.id}-${rule.rule_id}`" class="py-3 flex justify-between items-center">
                    <div>
                      <p class="text-sm font-medium text-gray-900">{{ getRuleName(rule.rule_id) }}</p>
                      <p class="mt-1 text-sm text-gray-500">
                        Action: {{ rule.action.type || 'replace' }}
                      </p>
                    </div>
                    <div class="flex space-x-2">
                      <button
                        @click.stop="$emit('editPresetRule', { presetId: preset.id, rule })"
                        class="text-indigo-600 hover:text-indigo-900"
                        title="Edit rule"
                      >
                        <PencilIcon class="h-5 w-5" />
                      </button>
                      <button
                        @click.stop="$emit('deletePresetRule', { preset_id: preset.id, rule_id: rule.rule_id })"
                        class="text-red-600 hover:text-red-900"
                        title="Delete rule"
                      >
                        <TrashIcon class="h-5 w-5" />
                      </button>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-4">
                  <p class="text-sm text-gray-500">No rules added to this preset.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && (!productGroups || Object.keys(productGroups).length === 0)" class="mt-12 text-center">
      <svg
        class="mx-auto h-12 w-12 text-gray-400"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
        />
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
        />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">No presets found</h3>
      <p class="mt-1 text-sm text-gray-500">
        Get started by creating a new preset.
      </p>
      <div class="mt-6">
        <button
          type="button"
          @click="$emit('addPreset')"
          class="inline-flex items-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600"
        >
          <PlusIcon class="-ml-0.5 mr-1.5 h-5 w-5" />
          Add Preset
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  presets: {
    type: Array,
    required: true
  },
  products: {
    type: Array,
    required: true
  },
  rules: {
    type: Array,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits([
  'addPreset',
  'editPreset',
  'deletePreset',
  'addRuleToPreset',
  'editPresetRule',
  'deletePresetRule',
  'loadPresetRules'
])

// Product groups
const productGroups = ref({})

// Track expanded state for products
const expandedProducts = ref({})

// Method to get rule name by ID
const getRuleName = (ruleId) => {
  const rule = props.rules.find(r => r.id === ruleId)
  return rule ? rule.name : 'Unknown'
}

// Group presets by product
const updateProductGroups = () => {
  const grouped = {}

  // First ensure products are loaded
  if (props.products.length === 0) return

  // Initialize all products with empty arrays
  props.products.forEach(product => {
    grouped[product.id] = {
      product: product,
      presets: []
    }
  })

  // Add presets to their respective product groups
  props.presets.forEach(preset => {
    if (grouped[preset.product_id]) {
      grouped[preset.product_id].presets.push(preset)
    } else {
      // Handle case where a preset might have an invalid product_id
      if (!grouped['unknown']) {
        grouped['unknown'] = {
          product: { id: 'unknown', name: 'Unknown Product' },
          presets: []
        }
      }
      grouped['unknown'].presets.push(preset)
    }
  })

  // Auto-expand the first product or if there's only one product with presets
  const productsWithPresets = Object.values(grouped).filter(group => group.presets.length > 0)
  if (productsWithPresets.length === 1 && Object.keys(expandedProducts.value).length === 0) {
    // Only auto-expand on initial load
    expandedProducts.value[productsWithPresets[0].product.id] = true
  }

  productGroups.value = grouped
}

// Toggle product expansion
const toggleProductExpand = (productId) => {
  expandedProducts.value[productId] = !expandedProducts.value[productId]
}

// Check if a product is expanded
const isProductExpanded = (productId) => {
  return !!expandedProducts.value[productId]
}

// Toggle preset expansion
const togglePresetExpand = async (preset) => {
  preset.expanded = !preset.expanded
  if (preset.expanded && (!preset.rules || preset.rules.length === 0)) {
    emit('loadPresetRules', preset.id)
  }
}

// Watch for changes to presets or products
watch([() => props.presets, () => props.products], () => {
  updateProductGroups()
}, { immediate: true })
</script>
