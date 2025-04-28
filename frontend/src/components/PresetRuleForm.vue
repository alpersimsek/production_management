<template>
  <Dialog :open="open" @close="$emit('close')" class="relative z-20">
    <div class="fixed inset-0 bg-black/40 backdrop-blur-sm transition-opacity duration-300" aria-hidden="true" />
    <div class="fixed inset-0 flex items-center justify-center p-4">
      <DialogPanel
        class="w-full max-w-md transform overflow-hidden rounded-xl bg-white p-6 shadow-2xl transition-all duration-300">
        <DialogTitle as="h3" class="text-lg font-semibold text-gray-900">{{ isEdit ? 'Edit Rule for Preset' : 'Add Rule          to Preset' }}</DialogTitle>
        <div v-if="successMessage" class="mt-4 rounded-md bg-green-50 p-3 flex items-center animate-fade-in">
          <CheckCircleIcon class="h-5 w-5 text-green-400" />
          <p class="ml-2 text-sm text-green-800">{{ successMessage }}</p>
        </div>
        <div v-if="errorMessage" class="mt-4 rounded-md bg-red-50 p-3 flex items-center animate-fade-in">
          <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
          <p class="ml-2 text-sm text-red-800">{{ errorMessage }}</p>
          <button type="button" @click="errorMessage = ''" class="ml-auto text-red-500 hover:text-red-700"
            aria-label="Dismiss error">
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>
        <div class="mt-6 space-y-4">
          <div>
            <label for="rule" class="block text-sm font-medium text-gray-700">Rule</label>
            <select id="rule" v-model="formData.rule_id"
              class="mt-2 block w-full rounded-md border-gray-300 py-2.5 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              :class="{ 'border-red-300': errors.rule_id }" required @focus="clearError('rule_id')">
              <option value="" disabled>Select a rule</option>
              <option v-for="rule in availableRules" :key="rule.id" :value="rule.id">{{ rule.name }}</option>
            </select>
            <p v-if="errors.rule_id" class="mt-1 text-sm text-red-600">{{ errors.rule_id }}</p>
          </div>
        </div>
        <div class="mt-8 flex justify-end space-x-3">
          <button type="button" @click="$emit('close')"
            class="inline-flex rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-gray-300 hover:bg-gray-50"
            :disabled="saving">Cancel</button>
          <button type="button" @click="save" :disabled="!isValid || saving"
            class="inline-flex rounded-md bg-gradient-to-r from-indigo-600 to-indigo-700 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-indigo-400">
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

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import { XMarkIcon, CheckCircleIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'

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