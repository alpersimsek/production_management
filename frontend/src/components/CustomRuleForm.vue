<!--
GDPR Tool Custom Rule Form - Rule Creation and Editing Modal Component

This component provides a modal dialog for creating and editing custom GDPR rules
in the GDPR compliance tool. It allows users to define regex patterns for data masking.

Key Features:
- Rule Creation: Form for creating new custom rules
- Rule Editing: Edit existing rules with pre-populated data
- Regex Validation: Validates regex patterns before saving
- Category Selection: Choose from predefined rule categories
- Form Validation: Comprehensive field validation with error handling
- Stay Open Option: Option to add multiple rules without closing modal
- Success Feedback: Clear success messages and error handling

Props:
- open: Whether the modal is open (boolean, required)
- rule: Rule object for editing (object, optional)

Events:
- close: Emitted when modal is closed
- saved: Emitted when rule is successfully saved
- error: Emitted when an error occurs

Features:
- Rule Categories: Predefined categories (ipv4_addr, mac_addr, username, domain, phone_num)
- Regex Validation: Validates regex patterns before submission
- Form Reset: Automatic form reset after successful creation
- Focus Management: Proper focus handling for accessibility
- Loading States: Visual feedback during save operations
- Error Handling: Clear error messages with dismiss functionality

The component provides a comprehensive interface for rule management in the
GDPR compliance tool with proper validation and user feedback.
-->

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import AppButton from './AppButton.vue'
import InputField from './InputField.vue'
import SelectField from './SelectField.vue'
import { XMarkIcon, ExclamationCircleIcon, CheckCircleIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'

const props = defineProps({ open: { type: Boolean, required: true }, rule: { type: Object, default: null } })
const emit = defineEmits(['close', 'saved', 'error'])

const form = ref({
  name: '',
  category: '',
  pattern: '',
})
const errors = ref({})
const error = ref('')
const saving = ref(false)
const successMessage = ref('')
const editing = computed(() => !!props.rule?.id)
const nameInput = ref(null)
const stayOpen = ref(false)

// Rule categories from RuleCategory enum
const categories = ['ipv4_addr', 'mac_addr', 'username', 'domain', 'phone_num']

// Initialize form
watch(() => props.rule, (newRule) => {
  try {
    if (newRule?.id) {
      form.value = {
        name: newRule.name || '',
        category: newRule.category || '',
        pattern: newRule.config?.pattern || '',
      }
    } else {
      form.value = { name: '', category: '', pattern: '' }
    }
    errors.value = {}
    error.value = ''
    successMessage.value = ''
  } catch (err) {
    error.value = `Failed to initialize form: ${err.message || 'Unknown error'}`
  }
}, { immediate: true })

// Focus name input when modal opens
watch(() => props.open, async (newOpen) => {
  if (newOpen) {
    await nextTick()
    try {
      if (nameInput.value && typeof nameInput.value.focus === 'function') {
        nameInput.value.focus()
      } else {
        // Fallback: focus the first focusable element (e.g., Cancel button)
        const dialog = document.querySelector('.relative.z-30 [role="dialog"]')
        if (dialog) {
          const focusable = dialog.querySelector('button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])')
          if (focusable && typeof focusable.focus === 'function') {
            focusable.focus()
          }
        }
      }
    } catch (err) {
      console.warn(`Failed to set focus: ${err.message}`)
    }
  }
}, { immediate: true })

const clearFieldError = (field) => {
  errors.value = { ...errors.value, [field]: '' }
}

const handleClose = () => {
  if (!saving.value) {
    form.value = { name: '', category: '', pattern: '' }
    errors.value = {}
    error.value = ''
    successMessage.value = ''
    stayOpen.value = false
    emit('close')
  }
}

const saveRule = async () => {
  try {
    saving.value = true
    errors.value = {}
    error.value = ''
    // Validation
    if (!form.value.name) errors.value.name = 'Name is required'
    if (!form.value.category) errors.value.category = 'Category is required'
    if (!form.value.pattern) {
      errors.value.pattern = 'Pattern is required'
    } else {
      try {
        new RegExp(form.value.pattern)
      } catch {
        errors.value.pattern = 'Invalid regex pattern'
      }
    }
    if (Object.keys(errors.value).length) return

    const ruleData = {
      name: form.value.name,
      category: form.value.category,
      config: {
        type: 'regex',
        pattern: form.value.pattern,
        patcher_cfg: { type: 'replace' },
      }
    }
    const response = editing.value
      ? await ApiService.updateRule(props.rule.id, ruleData)
      : await ApiService.createRule(ruleData)
    
    successMessage.value = editing.value ? 'Rule updated successfully' : 'Rule created successfully'
    if (stayOpen.value && !editing.value) {
      form.value = { name: '', category: '', pattern: '' }
      errors.value = {}
      successMessage.value = 'Rule created successfully. Add another rule below.'
      await nextTick()
      if (nameInput.value && typeof nameInput.value.focus === 'function') {
        nameInput.value.focus()
      }
    } else {
      setTimeout(() => {
        emit('saved', response)
        emit('close')
      }, 2000)
    }
  } catch (err) {
    const errorMessage = `Failed to ${editing.value ? 'update' : 'create'} rule: ${err.message || err.data?.detail || 'Unknown error'}`
    error.value = errorMessage
    emit('error', errorMessage)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-30" :open="open" @close="handleClose">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
        leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/60 transition-opacity" />
      </TransitionChild>
      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel
              class="relative transform overflow-hidden rounded-2xl bg-white/90 backdrop-blur-sm border border-slate-200/60 px-6 py-8 shadow-2xl sm:my-8 sm:w-full sm:max-w-lg">
              <button type="button"
                class="absolute right-4 top-4 text-slate-400 hover:text-slate-600 focus:outline-none focus:ring-2 focus:ring-gray-400 rounded-lg p-1 transition-all duration-200"
                @click="handleClose" aria-label="Close modal">
                <XMarkIcon class="h-6 w-6" />
              </button>
              <DialogTitle as="h3" class="text-2xl font-bold text-slate-900">
                {{ editing ? 'Edit Rule' : 'Create New Rule' }}
              </DialogTitle>
              <div v-if="error" class="mt-4 rounded-2xl bg-red-50/80 backdrop-blur-sm border border-red-200/60 p-4 flex items-center">
                <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
                <p class="ml-2 text-sm text-red-800">{{ error }}</p>
                <button type="button" @click="error = ''" class="ml-auto text-red-500 hover:text-red-700 rounded-lg p-1 transition-all duration-200"
                  aria-label="Dismiss error">
                  <XMarkIcon class="h-6 w-6" />
                </button>
              </div>
              <div v-if="successMessage" class="mt-4 rounded-2xl bg-green-50/80 backdrop-blur-sm border border-green-200/60 p-4 flex items-center">
                <CheckCircleIcon class="h-5 w-5 text-green-400" />
                <p class="ml-2 text-sm text-green-800">{{ successMessage }}</p>
              </div>
              <form @submit.prevent="saveRule" class="mt-6 space-y-6">
                <InputField :input-ref="nameInput" id="rule-name" v-model="form.name" label="Name" type="text"
                  required placeholder="e.g., IP Address Masking" :error="errors.name"
                  aria-describedby="rule-name-error" @focus="clearFieldError('name')" />
                <SelectField id="rule-category" v-model="form.category" label="Category" required
                  :error="errors.category" aria-describedby="rule-category-error"
                  @focus="clearFieldError('category')">
                  <option value="" disabled>Select a category</option>
                  <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
                </SelectField>
                <InputField id="rule-pattern" v-model="form.pattern"
                  label="Pattern" type="text" placeholder="e.g., \b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"
                  :error="errors.pattern" aria-describedby="rule-pattern-error"
                  @focus="clearFieldError('pattern')" />
                <div v-if="!editing" class="flex items-center">
                  <input id="stay-open" type="checkbox" v-model="stayOpen"
                    class="h-4 w-4 rounded border-gray-300 text-gray-600 focus:ring-gray-400" />
                  <label for="stay-open" class="ml-2 text-sm text-slate-700">Add another rule after saving</label>
                </div>
                <div class="mt-8 flex flex-row-reverse gap-3">
                  <AppButton type="submit" variant="primary" :loading="saving" :disabled="saving"
                    class="rounded-2xl bg-gradient-to-r from-gray-500 to-slate-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:from-gray-600 hover:to-slate-700 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
                    :aria-label="editing ? 'Update rule' : 'Create rule'">
                    <span v-if="saving" class="flex items-center">
                      <svg class="animate-spin h-5 w-5 mr-2 text-white" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                        <path class="opacity-75" fill="currentColor"
                          d="M4 12a8 8 0 018-8v8h8a8 8 0 01-8 8 8 8 0 01-8-8z" />
                      </svg>
                      Saving...
                    </span>
                    <span v-else>{{ editing ? 'Update' : 'Create' }}</span>
                  </AppButton>
                  <AppButton type="button" variant="secondary" @click="handleClose" :disabled="saving"
                    class="rounded-2xl border border-gray-200/60 bg-white/80 backdrop-blur-sm px-4 py-2 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-100/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
                    aria-label="Cancel">Cancel</AppButton>
                </div>
              </form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<style scoped>
.transition-all {
  transition: all 0.3s ease-in-out;
}
</style>
