<template>
  <div>
    <div class="border-t border-gray-200">
      <!-- Header with title and add button -->
      <div class="px-4 py-3 sm:px-6 bg-gray-50 flex justify-between items-center">
        <h4 class="text-md font-medium text-gray-700">Rules</h4>
        <button
          @click="$emit('addRule')"
          class="inline-flex items-center text-sm font-medium text-indigo-600 hover:text-indigo-500"
        >
          <PlusIcon class="h-4 w-4 mr-1" />
          Add Rule
        </button>
      </div>

      <!-- Loading state -->
      <div v-if="loading" class="px-4 py-5 sm:p-6 flex justify-center">
        <svg class="h-6 w-6 animate-spin text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>

      <!-- Rules list -->
      <div v-else class="px-4 py-5 sm:p-6">
        <div v-if="presetRules && presetRules.length > 0" class="divide-y divide-gray-200">
          <div v-for="rule in presetRules" :key="`${presetId}-${rule.rule_id}`" class="py-3 flex justify-between items-center">
            <div>
              <p class="text-sm font-medium text-gray-900">{{ getRuleName(rule.rule_id) }}</p>
              <p class="mt-1 text-sm text-gray-500">
                Action: {{ rule.action.type || 'replace' }}
              </p>
            </div>
            <div class="flex space-x-2">
              <button
                @click="$emit('editRule', rule)"
                class="text-indigo-600 hover:text-indigo-900"
                title="Edit rule"
              >
                <PencilIcon class="h-5 w-5" />
              </button>
              <button
                @click="$emit('deleteRule', { preset_id: presetId, rule_id: rule.rule_id })"
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
</template>

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

defineEmits(['addRule', 'editRule', 'deleteRule'])

// Method to get rule name by ID
const getRuleName = (ruleId) => {
  const rule = props.allRules.find(r => r.id === ruleId)
  return rule ? rule.name : 'Unknown'
}
</script>
