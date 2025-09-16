<!--
GDPR Tool Presets List - Presets Management Component

This component provides a comprehensive interface for managing presets in the GDPR compliance tool.
It displays presets grouped by products with expandable sections for rules management.

Key Features:
- Product Grouping: Groups presets by their associated products
- Expandable Sections: Collapsible product and preset sections
- Preset Management: Add, edit, and delete presets
- Rule Management: Add, edit, and delete rules within presets
- Loading States: Visual feedback during operations
- Empty States: Messages when no presets or rules are present

Props:
- presets: Array of presets (array, required)
- products: Array of products (array, required)
- rules: Array of all available rules (array, required)
- loading: Whether data is loading (boolean, default: false)

Events:
- addPreset: Emitted when adding a new preset (productId: number/string)
- editPreset: Emitted when editing a preset (preset: object)
- deletePreset: Emitted when deleting a preset (preset: object)
- addRuleToPreset: Emitted when adding a rule to a preset (presetId: number/string)
- editPresetRule: Emitted when editing a preset rule (data: object)
- deletePresetRule: Emitted when deleting a preset rule (data: object)
- loadPresetRules: Emitted when loading preset rules (presetId: number/string)

Features:
- Product Grouping: Automatically groups presets by product
- Expandable UI: Collapsible sections for better organization
- Rule Display: Shows rules associated with each preset
- Action Buttons: Edit and delete buttons for presets and rules
- Loading States: Spinner during data operations
- Empty States: Helpful messages when no data is present

The component provides a comprehensive interface for preset and rule management in the
GDPR compliance tool with proper organization and user feedback.
-->

<script setup>
import { ref, watch } from 'vue'
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  presets: { type: Array, required: true },
  products: { type: Array, required: true },
  rules: { type: Array, required: true },
  loading: { type: Boolean, default: false }
})

const emit = defineEmits(['addPreset', 'editPreset', 'deletePreset', 'addRuleToPreset', 'editPresetRule', 'deletePresetRule', 'loadPresetRules', 'deleteProduct'])

const productGroups = ref({})
const expandedProducts = ref({})

const getRuleName = (ruleId) => {
  const rule = props.rules.find(r => r.id === ruleId)
  if (!rule) console.warn(`Rule with ID ${ruleId} not found in rules array`)
  return rule ? rule.name : 'Unknown'
}

const updateProductGroups = () => {
  const grouped = {}
  if (props.products.length === 0) return
  props.products.forEach(product => {
    grouped[product.id] = { product, presets: [] }
  })
  props.presets.forEach(preset => {
    if (grouped[preset.product_id]) {
      grouped[preset.product_id].presets.push(preset)
    } else {
      if (!grouped['unknown']) grouped['unknown'] = { product: { id: 'unknown', name: 'Unknown Product' }, presets: [] }
      grouped['unknown'].presets.push(preset)
    }
  })
  const productsWithPresets = Object.values(grouped).filter(group => group.presets.length > 0)
  if (productsWithPresets.length === 1 && Object.keys(expandedProducts.value).length === 0) {
    expandedProducts.value[productsWithPresets[0].product.id] = true
  }
  productGroups.value = grouped
}

const addPreset = (productId) => {
  emit('addPreset', productId)
}

const deleteProduct = (productId) => {
  emit('deleteProduct', productId)
}

const toggleProductExpand = (productId) => {
  expandedProducts.value[productId] = !expandedProducts.value[productId]
}

const isProductExpanded = (productId) => !!expandedProducts.value[productId]

const togglePresetExpand = async (preset) => {
  preset.expanded = !preset.expanded
  if (preset.expanded && (!preset.rules || preset.rules.length === 0)) {
    emit('loadPresetRules', preset.id)
  }
}

watch([() => props.presets, () => props.products], updateProductGroups, { immediate: true })
</script>

<template>
  <div>
    <!-- Loading state -->
    <div v-if="loading" class="mt-6 flex justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-2 border-gray-400/60 border-t-transparent"></div>
      <p class="ml-4 text-sm font-medium text-slate-600">Loading presets...</p>
    </div>

    <!-- Presets list -->
    <div v-if="!loading && productGroups" class="mt-8 space-y-6">
      <div v-for="(group, productId) in productGroups" :key="productId" class="space-y-4">
        <div
          class="bg-white/80 backdrop-blur-sm px-6 py-4 rounded-2xl border border-slate-200/60 shadow-lg hover:shadow-xl flex justify-between items-center transition-all duration-300"
          @click="toggleProductExpand(productId)" role="button" :aria-expanded="isProductExpanded(productId)"
          :aria-label="`Toggle ${group.product.name} presets`">
          <div class="cursor-pointer hover:bg-slate-50/60 rounded-lg p-2 -m-2 transition-colors duration-200">
            <h2 class="text-lg font-semibold text-slate-900">{{ group.product.name }}</h2>
            <p class="text-sm text-slate-600">{{ group.presets.length }} preset{{ group.presets.length !== 1 ? 's' : ''
              }}</p>
          </div>
          <div class="flex items-center space-x-4">
            <button type="button" @click.stop="addPreset(productId)"
              class="inline-flex items-center rounded-2xl bg-gradient-to-r from-gray-500 to-slate-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:from-gray-600 hover:to-slate-700 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
              aria-label="Add preset for this product">
              <PlusIcon class="h-5 w-5 mr-1.5" />
              Add Preset
            </button>
            <button type="button" @click.stop="deleteProduct(productId)"
              class="inline-flex items-center px-4 py-2 text-sm font-medium text-red-700 bg-red-100/80 backdrop-blur-sm border border-red-200/60 rounded-2xl hover:bg-red-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 transition-all duration-200"
              aria-label="Delete product">
              <TrashIcon class="h-5 w-5 mr-2" />
            </button>
            <svg class="h-6 w-6 text-slate-500 transition-transform duration-300"
              :class="{ 'rotate-180': isProductExpanded(productId) }" xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fill-rule="evenodd"
                d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
                clip-rule="evenodd" />
            </svg>
          </div>
        </div>

        <transition name="expand">
          <div v-if="isProductExpanded(productId)" class="space-y-4">
            <div v-if="group.presets.length === 0" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-200/60 shadow-lg ml-4 p-6 text-center">
              <p class="text-sm text-slate-600">No presets for this product yet.</p>
            </div>
            <div v-for="preset in group.presets" :key="preset.id" class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-200/60 shadow-lg hover:shadow-xl ml-4 transition-all duration-300">
              <div
                class="px-6 py-5 flex justify-between items-center cursor-pointer hover:bg-slate-50/60 transition-all duration-200"
                @click="togglePresetExpand(preset)" role="button" :aria-expanded="preset.expanded"
                :aria-label="`Toggle ${preset.name} rules`">
                <div>
                  <h3 class="text-base font-medium text-slate-900">{{ preset.name }}</h3>
                  <p class="mt-1 max-w-2xl text-sm text-slate-600">Header: {{ preset.header }}</p>
                </div>
                <div class="flex space-x-2">
                  <button @click.stop="$emit('editPreset', preset)"
                    class="inline-flex items-center px-3 py-2 text-xs font-medium text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 rounded-2xl hover:bg-gray-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
                    title="Edit preset" aria-label="Edit preset">
                    <PencilIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                    Edit
                  </button>
                  <button @click.stop="$emit('deletePreset', preset)"
                    class="inline-flex items-center px-3 py-2 text-xs font-medium text-red-700 bg-red-100/80 backdrop-blur-sm border border-red-200/60 rounded-2xl hover:bg-red-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 transition-all duration-200"
                    title="Delete preset" aria-label="Delete preset">
                    <TrashIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                    Delete
                  </button>
                </div>
              </div>

              <transition name="expand">
                <div v-if="preset.expanded" class="border-t border-slate-200/60">
                  <div class="px-6 py-4 bg-slate-50/60 backdrop-blur-sm flex justify-between items-center">
                    <h4 class="text-sm font-medium text-slate-700">Rules</h4>
                    <button @click.stop="$emit('addRuleToPreset', preset.id)"
                      class="inline-flex items-center rounded-2xl bg-gradient-to-r from-gray-500 to-slate-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:from-gray-600 hover:to-slate-700 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
                      aria-label="Add rule to preset">
                      <PlusIcon class="h-5 w-5 mr-1.5" />
                      Add Rule
                    </button>
                  </div>
                  <div class="px-6 py-5">
                    <div v-if="preset.rules && preset.rules.length > 0" class="divide-y divide-slate-200/60">
                      <div v-for="rule in preset.rules" :key="`${preset.id}-${rule.rule_id}`"
                        class="py-4 flex justify-between items-center hover:bg-slate-50/60 transition-all duration-200"
                        role="listitem">
                        <div>
                          <p class="text-sm font-medium text-slate-900">{{ getRuleName(rule.rule_id) }}</p>
                          <p class="mt-1 text-sm text-slate-600">Action: {{ rule.action.type || 'replace' }}</p>
                        </div>
                        <div class="flex space-x-2">
                          <button @click.stop="$emit('editPresetRule', { presetId: preset.id, rule })"
                            class="inline-flex items-center px-3 py-2 text-xs font-medium text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 rounded-2xl hover:bg-gray-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
                            title="Edit rule" aria-label="Edit rule">
                            <PencilIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                            Edit
                          </button>
                          <button
                            @click.stop="$emit('deletePresetRule', { preset_id: preset.id, rule_id: rule.rule_id })"
                            class="inline-flex items-center px-3 py-2 text-xs font-medium text-red-700 bg-red-100/80 backdrop-blur-sm border border-red-200/60 rounded-2xl hover:bg-red-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 transition-all duration-200"
                            title="Delete rule" aria-label="Delete rule">
                            <TrashIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                    <div v-else class="text-center py-4">
                      <p class="text-sm text-slate-600">No rules added to this preset.</p>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </transition>
      </div>
    </div>

    <!-- Empty state -->
    <div v-if="!loading && (!productGroups || Object.keys(productGroups).length === 0)" class="mt-12 text-center">
      <div class="w-20 h-20 mx-auto mb-4 bg-slate-100/60 backdrop-blur-sm rounded-2xl flex items-center justify-center">
        <svg class="h-10 w-10 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"
          aria-hidden="true">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </div>
      <h3 class="mt-2 text-base font-medium text-slate-900">No presets found</h3>
      <p class="mt-1 text-sm text-slate-600">Get started by creating a new preset.</p>
      <div class="mt-6">
        <button type="button" @click="$emit('addPreset')"
          class="inline-flex items-center rounded-2xl bg-gradient-to-r from-gray-500 to-slate-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:from-gray-600 hover:to-slate-700 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
          aria-label="Add new preset">
          <PlusIcon class="-ml-0.5 mr-1.5 h-5 w-5" />
          Add Preset
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.transition-all {
  transition: all 0.3s ease-in-out;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
}

.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  overflow: hidden;
}

.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 1000px;
}
</style>