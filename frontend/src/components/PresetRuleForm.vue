<!--
GDPR Tool Preset Rule Form - Preset Rule Management Modal Component

This component provides a modal dialog for adding and editing rules within presets
in the GDPR compliance tool. It allows users to associate rules with specific presets.

Key Features:
- Rule Association: Add rules to presets
- Rule Editing: Edit existing preset rules
- Rule Selection: Select from available rules
- Duplicate Prevention: Prevents adding duplicate rules to presets
- Form Validation: Required field validation with error handling
- Success Feedback: Clear success messages and error handling

Props:
- open: Whether the modal is open (boolean, required)
- presetId: ID of the preset (number/string, required)
- rules: Array of available rules (array, required)
- presetRules: Array of existing preset rules (array, default: [])
- editRule: Rule object for editing (object, optional)

Events:
- close: Emitted when modal is closed
- saved: Emitted when rule is successfully saved
- error: Emitted when an error occurs

Features:
- Rule Selection: Dropdown for selecting available rules
- Duplicate Prevention: Filters out already assigned rules
- Form Validation: Ensures rule selection before submission
- Success Messages: Clear feedback for successful operations
- Error Handling: Comprehensive error handling and display
- Loading States: Visual feedback during save operations

The component provides a comprehensive interface for preset rule management in the
GDPR compliance tool with proper validation and user feedback.
-->

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { XMarkIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'
import CustomSelect from './CustomSelect.vue'

const props = defineProps({
  open: { type: Boolean, required: true },
  presetId: { type: [Number, String], required: true },
  rules: { type: Array, required: true },
  presetRules: { type: Array, default: () => [] },
  editRule: { type: Object, default: null }
})

const emit = defineEmits(['close', 'saved', 'error'])

const formData = ref({ rule_id: '' })
const errors = ref({})
const saving = ref(false)
const successMessage = ref('')
const errorMessage = ref('')

const availableRules = computed(() => {
  if (props.editRule) return props.rules
  const existingRuleIds = props.presetRules.map(r => r.rule_id)
  return props.rules.filter(rule => !existingRuleIds.includes(rule.id))
})

const isEdit = computed(() => !!props.editRule)

const isValid = computed(() => !!formData.value.rule_id)

const clearError = (field) => {
  if (errors.value[field]) {
    errors.value = { ...errors.value, [field]: '' }
  }
}

watch(
  [() => props.open, () => props.editRule],
  ([open, editRule]) => {
    if (open) {
      successMessage.value = ''
      errorMessage.value = ''
      errors.value = {}
      formData.value = editRule ? { rule_id: editRule.rule_id } : { rule_id: '' }
    }
  },
  { immediate: true }
)

const save = async () => {
  errors.value = {}
  if (!formData.value.rule_id) {
    errors.value.rule_id = 'Please select a rule'
    return
  }

  saving.value = true
  try {
    // Include default action to satisfy backend schema
    const ruleData = {
      rule_id: formData.value.rule_id,
      action: { type: 'replace', value: '[REDACTED]' }
    }
    let response
    if (isEdit.value) {
      response = await ApiService.updatePresetRule(props.presetId, props.editRule.rule_id, ruleData)
      successMessage.value = 'Rule updated successfully'
    } else {
      const presetRuleData = { preset_id: props.presetId, ...ruleData }
      response = await ApiService.createPresetRule(presetRuleData)
      successMessage.value = 'Rule added successfully'
    }
    setTimeout(() => {
      emit('saved', response)
      emit('close')
    }, 1000)
  } catch (error) {
    // Handle complex error responses
    let message = 'Failed to save rule'
    if (error.status === 422 && error.data?.detail) {
      if (Array.isArray(error.data.detail)) {
        message = error.data.detail.map(err => err.msg).join('; ') || message
      } else {
        message = error.data.detail || message
      }
    } else {
      message = error.message || message
    }
    errorMessage.value = message
    emit('error', message)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <Dialog :open="open" @close="$emit('close')" class="relative z-20">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/60 transition-opacity duration-300" aria-hidden="true" />
    <div class="fixed inset-0 flex items-center justify-center p-4">
      <DialogPanel
        class="w-full max-w-md transform overflow-visible rounded-2xl bg-white/90 backdrop-blur-sm border border-slate-200/60 p-6 shadow-2xl transition-all duration-300">
        <DialogTitle as="h3" class="text-2xl font-bold text-slate-900">{{ isEdit ? 'Edit Rule for Preset' : 'Add Rule to Preset' }}</DialogTitle>
        <p class="mt-2 text-sm text-slate-600">
          {{ isEdit ? 'Update the masking rule configuration for this preset' : 'Select a masking rule to apply when this preset is used for file processing' }}
        </p>
        <div v-if="successMessage" class="mt-4 rounded-2xl bg-green-50/80 backdrop-blur-sm border border-green-200/60 p-4 flex items-center animate-fade-in">
          <CheckCircleIcon class="h-5 w-5 text-green-400" />
          <p class="ml-2 text-sm text-green-800">{{ successMessage }}</p>
        </div>
        <div v-if="errorMessage" class="mt-4 rounded-2xl bg-red-50/80 backdrop-blur-sm border border-red-200/60 p-4 flex items-center animate-fade-in">
          <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
          <p class="ml-2 text-sm text-red-800">{{ errorMessage }}</p>
          <button type="button" @click="errorMessage = ''" class="ml-auto text-red-500 hover:text-red-700 rounded-lg p-1 transition-all duration-200"
            aria-label="Dismiss error">
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>
        <div class="mt-6 space-y-4">
          <CustomSelect
            v-model="formData.rule_id"
            :options="availableRules.map(rule => ({ value: rule.id, label: rule.name }))"
            label="Rule"
            placeholder="Select a rule"
            :required="true"
            :error="errors.rule_id"
          />
        </div>
        <div class="mt-8 flex justify-end space-x-3">
          <button type="button" @click="$emit('close')"
            class="inline-flex rounded-2xl border border-gray-200/60 bg-white/80 backdrop-blur-sm px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-100/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
            :disabled="saving">Cancel</button>
          <button type="button" @click="save" :disabled="!isValid || saving"
            class="inline-flex rounded-2xl bg-gradient-to-r from-gray-500 to-slate-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:from-gray-600 hover:to-slate-700 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 disabled:from-gray-400 disabled:to-slate-500 transition-all duration-200">
            <svg v-if="saving" class="animate-spin h-5 w-5 mr-2 text-white" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8h8a8 8 0 01-8 8 8 8 0 01-8-8z"></path>
            </svg>
            {{ isEdit ? 'Update' : 'Add' }} Rule
          </button>
        </div>
      </DialogPanel>
    </div>
  </Dialog>
</template>

<style scoped>
.transition-all {
  transition: all 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}
</style>