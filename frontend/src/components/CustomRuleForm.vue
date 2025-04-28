<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-30" :open="open" @close="handleClose">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
        leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/50 transition-opacity" aria-hidden="true" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel
              class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 shadow-xl sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
              <!-- Close Button -->
              <div class="absolute right-0 top-0 pr-4 pt-4">
                <button type="button"
                  class="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  @click="handleClose" aria-label="Close">
                  <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                </button>
              </div>

              <!-- Form -->
              <DialogTitle as="h3" class="text-lg font-semibold text-gray-900">
                {{ editing ? 'Edit Rule' : 'Create New Rule' }}
              </DialogTitle>
              <!-- Error Message -->
              <div v-if="error" class="mt-3 rounded-md bg-red-50 p-3">
                <div class="flex items-center">
                  <ExclamationCircleIcon class="h-5 w-5 text-red-400" aria-hidden="true" />
                  <p class="ml-2 text-sm text-red-800">{{ error }}</p>
                  <button type="button" @click="error = ''" class="ml-auto text-red-500 hover:text-red-700"
                    aria-label="Dismiss error">
                    <XMarkIcon class="h-5 w-5" />
                  </button>
                </div>
              </div>

              <form @submit.prevent="saveRule" class="mt-4 space-y-5">
                <!-- Name -->
                <div>
                  <label for="rule-name" class="block text-sm font-medium text-gray-700">Name</label>
                  <input ref="nameInput" type="text" id="rule-name" v-model="form.name"
                    class="mt-2 block w-full rounded-lg border-gray-300 py-2.5 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    :class="{ 'border-red-300': errors.name }" placeholder="Rule name" required
                    aria-describedby="rule-name-error" @focus="clearFieldError('name')" />
                  <p v-if="errors.name" id="rule-name-error" class="mt-1 text-sm text-red-600">{{ errors.name }}</p>
                </div>

                <!-- Category -->
                <div>
                  <label for="rule-category" class="block text-sm font-medium text-gray-700">Category</label>
                  <select id="rule-category" v-model="form.category"
                    class="mt-2 block w-full rounded-lg border-gray-300 py-2.5 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    :class="{ 'border-red-300': errors.category }" required aria-describedby="rule-category-error"
                    @focus="clearFieldError('category')">
                    <option value="ipv4_addr">IPv4 Address</option>
                    <option value="mac_addr">MAC Address</option>
                    <option value="username">Username</option>
                    <option value="domain">Domain</option>
                    <option value="phone_num">Phone Number</option>
                  </select>
                  <p v-if="errors.category" id="rule-category-error" class="mt-1 text-sm text-red-600">{{
                    errors.category }}</p>
                </div>

                <!-- Type -->
                <div>
                  <label for="rule-type" class="block text-sm font-medium text-gray-700">Type</label>
                  <select id="rule-type" v-model="form.type" class="mt-2 block w-full rounded-lg border-gray-300 py-2.5 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo偶像直播版權所有 2025 xAI

                    class=" mt-2 block w-full rounded-lg border-gray-300 py-2.5 text-base shadow-sm
                    focus:border-indigo-500 focus:indigo-500 :class="{ 'border-red-300': errors.type }" required
                    aria-describedby="rule-type-error" @focus="clearFieldError('type')">
                    <option value="regex">Regular Expression</option>
                    <option value="builtin">Built-in Rule</option>
                    <option value="placeholder">Placeholder</option>
                  </select>
                  <p v-if="errors.type" id="rule-type-error" class="mt-1 text-sm text-red-600">{{ errors.type }}</p>
                </div>

                <!-- Pattern (for regex) -->
                <div v-if="form.type === 'regex'">
                  <label for="rule-pattern" class="block text-sm font-medium text-gray-700">Pattern</label>
                  <input type="text" id="rule-pattern" v-model="form.pattern"
                    class="mt-2 block w-full rounded-lg border-gray-300 py-2.5 text-base shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                    :class="{ 'border-red-300': errors.pattern }" placeholder="Enter regex pattern" required
                    aria-describedby="rule-pattern-error" @focus="clearFieldError('pattern')" />
                  <p v-if="errors.pattern" id="rule-pattern-error" class="mt-1 text-sm text-red-600">{{ errors.pattern
                    }}</p>
                </div>

                <!-- Buttons -->
                <div class="mt-6 flex flex-row-reverse gap-3">
                  <button type="submit"
                    class="inline-flex items-center rounded-md bg-indigo-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 disabled:bg-indigo-400"
                    :disabled="saving">
                    <svg v-if="saving" class="animate-spin h-5 w-5 mr-2 text-white" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8h8a8 8 0 01-8 8 8 8 0 01-8-8z">
                      </path>
                    </svg>
                    {{ editing ? 'Update' : 'Create' }}
                  </button>
                  <button type="button"
                    class="inline-flex rounded-md bg-white px-4 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-gray-300 hover:bg-gray-50 disabled:bg-gray-100"
                    @click="handleClose" :disabled="saving">
                    Cancel
                  </button>
                </div>
              </form>
            </DialogPanel>
          </TransitionChild>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot, TransitionChild } from '@headlessui/vue'
import { XMarkIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'

const props = defineProps({
  open: {
    type: Boolean,
    required: true
  },
  rule: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['close', 'saved', 'error'])

// Form state
const form = ref({
  name: '',
  category: 'ipv4_addr',
  type: 'regex',
  pattern: ''
})

const errors = ref({}) // Field-specific errors
const error = ref('') // General error message
const saving = ref(false)
const editing = computed(() => !!props.rule?.id)
const nameInput = ref(null)

// Initialize form when rule prop changes
watch(
  () => props.rule,
  (newRule) => {
    console.log('CustomRuleForm: Rule changed', newRule)
    if (newRule?.id) {
      form.value = {
        name: newRule.name || '',
        category: newRule.category || 'ipv4_addr',
        type: newRule.config?.type || 'regex',
        pattern: newRule.config?.pattern || ''
      }
    } else {
      form.value = {
        name: '',
        category: 'ipv4_addr',
        type: 'regex',
        pattern: ''
      }
    }
    errors.value = {}
    error.value = ''
  },
  { immediate: true }
)

// Focus management
watch(
  () => props.open,
  async (newOpen) => {
    console.log('CustomRuleForm: Open changed', newOpen)
    if (newOpen) {
      await nextTick()
      if (nameInput.value) {
        try {
          nameInput.value.focus()
          console.log('CustomRuleForm: Name input focused')
        } catch (err) {
          console.error('CustomRuleForm: Failed to focus name input', err)
        }
      }
    }
  },
  { immediate: true }
)

// Clear field-specific error
const clearFieldError = (field) => {
  if (errors.value[field]) {
    errors.value = { ...errors.value, [field]: '' }
  }
}

// Handle close
const handleClose = () => {
  if (!saving.value) {
    console.log('CustomRuleForm: Closing')
    form.value = { name: '', category: 'ipv4_addr', type: 'regex', pattern: '' }
    errors.value = {}
    error.value = ''
    emit('close')
  }
}

// Save rule
const saveRule = async () => {
  try {
    saving.value = true
    errors.value = {}
    error.value = ''
    console.log('CustomRuleForm: Saving rule', form.value)

    // Client-side validation
    if (!form.value.name) {
      errors.value.name = 'Name is required'
      return
    }
    if (!form.value.category) {
      errors.value.category = 'Category is required'
      return
    }
    if (!form.value.type) {
      errors.value.type = 'Type is required'
      return
    }
    if (form.value.type === 'regex') {
      if (!form.value.pattern) {
        errors.value.pattern = 'Pattern is required for regex rules'
        return
      }
      try {
        new RegExp(form.value.pattern) // Validate regex syntax
      } catch {
        errors.value.pattern = 'Invalid regex pattern'
        return
      }
    }

    // Prepare payload
    const ruleData = {
      name: form.value.name,
      category: form.value.category,
      config: form.value.type === 'regex' ? { type: form.value.type, pattern: form.value.pattern } : { type: form.value.type }
    }

    // Save to backend
    const response = editing.value
      ? await ApiService.updateRule(props.rule.id, ruleData)
      : await ApiService.createRule(ruleData)

    console.log('CustomRuleForm: Rule saved', response)
    emit('saved', response)
    emit('close')
  } catch (err) {
    console.error('CustomRuleForm: Save error', err)
    error.value = `Failed to ${editing.value ? 'update' : 'create'} rule: ${err.message || 'Unknown error'}`
    emit('error', error.value)
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
/* Smooth transitions */
.transition-all {
  transition: all 0.3s ease-in-out;
}
</style>