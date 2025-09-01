<!--
GDPR Tool Preset Rules List - Preset Rules Management Component

This component provides a list interface for managing rules within presets
in the GDPR compliance tool. It displays preset rules with add, edit, and delete actions.

Key Features:
- Rules Display: Shows all rules associated with a preset
- Rule Management: Add, edit, and delete rules from presets
- Loading States: Visual feedback during rule operations
- Empty State: Displays message when no rules are present
- Action Buttons: Edit and delete buttons for each rule
- Rule Information: Shows rule names and action types

Props:
- presetId: ID of the preset (number/string, required)
- presetRules: Array of preset rules (array, default: [])
- allRules: Array of all available rules (array, default: [])
- loading: Whether rules are loading (boolean, default: false)

Events:
- addRule: Emitted when add rule button is clicked (presetId: number/string)
- editRule: Emitted when edit rule button is clicked (rule: object)
- deleteRule: Emitted when delete rule button is clicked (data: object)

Features:
- Rule List: Displays all rules associated with the preset
- Add Button: Button to add new rules to the preset
- Edit Actions: Edit buttons for each rule
- Delete Actions: Delete buttons for each rule
- Loading State: Spinner during rule operations
- Empty State: Message when no rules are present
- Rule Names: Displays rule names from allRules array

The component provides a comprehensive interface for preset rule management in the
GDPR compliance tool with proper action handling and user feedback.
-->

<script setup>
import { PlusIcon, PencilIcon, TrashIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  presetId: {
    type: [Number, String],
    required: true
  },
  presetRules: {
    type: Array,
    default: () => []
  },
  allRules: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['addRule', 'editRule', 'deleteRule'])

// Method to get rule name by ID
const getRuleName = (ruleId) => {
  const rule = props.allRules.find(r => r.id === ruleId)
  if (!rule) {
    console.warn(`Rule with ID ${ruleId} not found in allRules array for presetId: ${props.presetId}`)
  }
  return rule ? rule.name : 'Unknown'
}

// Event emission with debug logs
const emitAddRule = () => {
  console.log('Emitting addRule for presetId:', props.presetId)
  emit('addRule', props.presetId)
}

const emitEditRule = (rule) => {
  console.log('Emitting editRule for presetId:', props.presetId, 'ruleId:', rule.rule_id)
  emit('editRule', rule)
}

const emitDeleteRule = (data) => {
  console.log('Emitting deleteRule for presetId:', data.preset_id, 'ruleId:', data.rule_id)
  emit('deleteRule', data)
}
</script>

<template>
  <div>
    <div class="border-t border-gray-200">
      <!-- Header with title and add button -->
      <div class="px-4 py-3 sm:px-6 bg-gray-50 flex justify-between items-center">
        <h4 class="text-md font-medium text-gray-700">Rules</h4>
        <button @click="emitAddRule"
          class="inline-flex items-center rounded-lg bg-indigo-600 px-3 py-2 text-base font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          aria-label="Add rule to preset">
          <PlusIcon class="h-5 w-5 mr-1.5" />
          Add Rule
        </button>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="px-4 py-5 sm:p-6 flex justify-center">
        <svg class="h-8 w-8 animate-spin text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none"
          viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
          </path>
        </svg>
      </div>

      <!-- Rules list -->
      <div v-else class="px-4 py-5 sm:p-6">
        <div v-if="presetRules && presetRules.length > 0" class="divide-y divide-gray-200">
          <div v-for="rule in presetRules" :key="`${presetId}-${rule.rule_id}`"
            class="py-4 flex justify-between items-center hover:bg-gray-50 transition-all" role="listitem">
            <div>
              <p class="text-base font-medium text-gray-900">{{ getRuleName(rule.rule_id) }}</p>
              <p class="mt-1 text-sm text-gray-500">Action: {{ rule.action.type || 'replace' }}</p>
            </div>
            <div class="flex space-x-2">
              <button @click="emitEditRule(rule)" class="text-indigo-600 hover:text-indigo-900" title="Edit rule"
                aria-label="Edit rule">
                <PencilIcon class="h-5 w-5" />
              </button>
              <button @click="emitDeleteRule({ preset_id: presetId, rule_id: rule.rule_id })"
                class="text-red-600 hover:text-red-900" title="Delete rule" aria-label="Delete rule">
                <TrashIcon class="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
        <div v-else class="text-center py-4">
          <p class="text-base text-gray-500">No rules added to this preset.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Smooth transitions for hover effects */
.transition-all {
  transition: all 0.3s ease-in-out;
}
</style>