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
    error.value = `Failed to ${editing.value ? 'update' : 'create'} rule: ${err.message || err.data?.detail || 'Unknown error'}`
    emit('error', error.value)
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
              class="relative transform overflow-hidden rounded-xl bg-white px-6 py-8 shadow-2xl sm:my-8 sm:w-full sm:max-w-lg">
              <button type="button"
                class="absolute right-4 top-4 text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                @click="handleClose" aria-label="Close modal">
                <XMarkIcon class="h-6 w-6" />
              </button>
              <DialogTitle as="h3" class="text-lg font-bold text-gray-900">
                {{ editing ? 'Edit Rule' : 'Create New Rule' }}
              </DialogTitle>
              <div v-if="error" class="mt-4 rounded-md bg-red-50 p-3 flex items-center">
                <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
                <p class="ml-2 text-sm text-red-800">{{ error }}</p>
                <button type="button" @click="error = ''" class="ml-auto text-red-500 hover:text-red-700"
                  aria-label="Dismiss error">
                  <XMarkIcon class="h-6 w-6" />
                </button>
              </div>
              <div v-if="successMessage" class="mt-4 rounded-md bg-green-50 p-3 flex items-center">
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
                    class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
                  <label for="stay-open" class="ml-2 text-sm text-gray-700">Add another rule after saving</label>
                </div>
                <div class="mt-8 flex flex-row-reverse gap-3">
                  <AppButton type="submit" variant="primary" :loading="saving" :disabled="saving"
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
