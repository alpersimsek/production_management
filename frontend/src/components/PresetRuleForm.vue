<template>
  <Dialog :open="open" @close="$emit('close')" class="relative z-20">
    <div class="fixed inset-0 bg-black/30" style="z-index: 20;" aria-hidden="true" @mousedown.stop />

    <div class="fixed inset-0 flex items-center justify-center p-4" style="z-index: 20;">
      <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
        <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
          {{ isEdit ? 'Edit Rule for Preset' : 'Add Rule to Preset' }}
        </DialogTitle>

        <div class="mt-4">
          <div class="space-y-4">
            <!-- Rule Selection -->
            <div>
              <label for="rule" class="block text-sm font-medium text-gray-700">Rule</label>
              <select
                id="rule"
                v-model="formData.rule_id"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
                :required="true"
              >
                <option value="" disabled>Select a rule</option>
                <option v-for="rule in availableRules" :key="rule.id" :value="rule.id">
                  {{ rule.name }}
                </option>
              </select>
            </div>

            <!-- Action Type -->
            <div>
              <label for="action-type" class="block text-sm font-medium text-gray-700">Action Type</label>
              <select
                id="action-type"
                v-model="formData.action.type"
                class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              >
                <option value="replace">Replace</option>
                <option value="redact">Redact</option>
                <option value="hash">Hash</option>
              </select>
            </div>

            <!-- Replacement Value (only shown for replace action) -->
            <div v-if="formData.action.type === 'replace'">
              <label for="replacement" class="block text-sm font-medium text-gray-700">Replacement Value</label>
              <input
                id="replacement"
                type="text"
                v-model="formData.action.value"
                class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="[REDACTED]"
              />
            </div>
          </div>
        </div>

        <div class="mt-6 flex justify-end space-x-3">
          <button
            type="button"
            @click="$emit('close')"
            class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
          >
            Cancel
          </button>
          <button
            type="button"
            @click="save"
            :disabled="!isValid || saving"
            class="inline-flex justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-indigo-300"
          >
            <svg v-if="saving" class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ isEdit ? 'Update' : 'Add' }} Rule
          </button>
        </div>
      </DialogPanel>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import ApiService from '../services/api'

const props = defineProps({
  open: {
    type: Boolean,
    required: true
  },
  presetId: {
    type: [Number, String],
    required: true
  },
  rules: {
    type: Array,
    required: true
  },
  presetRules: {
    type: Array,
    default: () => []
  },
  editRule: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved', 'error'])

// Form data
const formData = ref({
  rule_id: '',
  action: {
    type: 'replace',
    value: '[REDACTED]'
  }
})

// Loading state
const saving = ref(false)

// Compute available rules (exclude already added ones)
const availableRules = computed(() => {
  // If editing, we need to include the current rule
  if (props.editRule) {
    return props.rules
  }

  // For new rules, exclude those already added to the preset
  const existingRuleIds = props.presetRules.map(r => r.rule_id)
  return props.rules.filter(rule => !existingRuleIds.includes(rule.id))
})

// Check if form is in edit mode
const isEdit = computed(() => !!props.editRule)

// Form validation
const isValid = computed(() => {
  return formData.value.rule_id &&
         formData.value.action.type &&
         (formData.value.action.type !== 'replace' || !!formData.value.action.value)
})

// Initialize form when dialog opens or editRule changes
watch(
  [() => props.open, () => props.editRule],
  ([open, editRule]) => {
    if (open) {
      if (editRule) {
        // Edit mode - populate form with rule data
        formData.value = {
          rule_id: editRule.rule_id,
          action: {
            type: editRule.action.type || 'replace',
            value: editRule.action.value || '[REDACTED]'
          }
        }
      } else {
        // Create mode - reset form
        formData.value = {
          rule_id: '',
          action: {
            type: 'replace',
            value: '[REDACTED]'
          }
        }
      }
    }
  },
  { immediate: true }
)

// Save the rule
const save = async () => {
  if (!isValid.value) return

  saving.value = true

  try {
    const ruleData = {
      rule_id: formData.value.rule_id,
      action: {
        type: formData.value.action.type,
        ...(formData.value.action.type === 'replace' && { value: formData.value.action.value })
      }
    }

    if (isEdit.value) {
      // Update existing rule
      await ApiService.updatePresetRule(props.presetId, props.editRule.rule_id, ruleData)
    } else {
      // Create new rule
      const presetRuleData = {
        preset_id: props.presetId,
        ...ruleData
      }
      await ApiService.createPresetRule(presetRuleData)
    }

    emit('saved')
  } catch (error) {
    console.error('Error saving preset rule:', error)
    emit('error', error)
  } finally {
    saving.value = false
  }
}
</script>
