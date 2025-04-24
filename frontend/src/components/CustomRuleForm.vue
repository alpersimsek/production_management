<template>
  <TransitionRoot as="template" :show="open">
    <Dialog class="relative z-30" :open="open" @close="handleClose">
      <TransitionChild as="template" enter="ease-out duration-300" enter-from="opacity-0" enter-to="opacity-100"
        leave="ease-in duration-200" leave-from="opacity-100" leave-to="opacity-0">
        <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/50 transition-opacity" @click="handleClose" />
      </TransitionChild>

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4 sm:p-0">
          <TransitionChild as="template" enter="ease-out duration-300"
            enter-from="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to="opacity-100 translate-y-0 sm:scale-100" leave="ease-in duration-200"
            leave-from="opacity-100 translate-y-0 sm:scale-100"
            leave-to="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95">
            <DialogPanel
              class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 shadow-xl sm:my-8 sm:w-full sm:max-w-lg sm:p-6"
              :focus-trap="isFocusable" tabindex="0" @click.stop @mousedown.stop>
              <!-- Close Button -->
              <div class="absolute right-0 top-0 pr-4 pt-4">
                <button type="button"
                  class="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
                  @click="handleClose">
                  <span class="sr-only">Close</span>
                  <XMarkIcon class="h-6 w-6" aria-hidden="true" />
                </button>
              </div>

              <!-- Form -->
              <DialogTitle as="h3" class="text-lg font-semibold text-gray-900">
                {{ editing ? 'Edit Rule' : 'Create New Rule' }}
              </DialogTitle>
              <form @submit.prevent="saveRule" class="mt-4 space-y-4" @click.stop @mousedown.stop>
                <!-- Name -->
                <div>
                  <label for="rule-name" class="block text-sm font-medium text-gray-700">Name</label>
                  <input ref="nameInput" type="text" id="rule-name" v-model="form.name" tabindex="0"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    placeholder="Rule name" required @focus="logFocus('Name input')" />
                </div>

                <!-- Category -->
                <div>
                  <label for="rule-category" class="block text-sm font-medium text-gray-700">Category</label>
                  <select id="rule-category" v-model="form.category" tabindex="0"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    required @focus="logFocus('Category select')">
                    <option value="ipv4_addr">IPv4 Address</option>
                    <option value="mac_addr">MAC Address</option>
                    <option value="username">Username</option>
                    <option value="domain">Domain</option>
                    <option value="phone_num">Phone Number</option>
                  </select>
                </div>

                <!-- Type -->
                <div>
                  <label for="rule-type" class="block text-sm font-medium text-gray-700">Type</label>
                  <select id="rule-type" v-model="form.type" tabindex="0"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    required @focus="logFocus('Type select')">
                    <option value="regex">Regular Expression</option>
                    <option value="builtin">Built-in Rule</option>
                    <option value="placeholder">Placeholder</option>
                  </select>
                </div>

                <!-- Pattern (for regex) -->
                <div v-if="form.type === 'regex'">
                  <label for="rule-pattern" class="block text-sm font-medium text-gray-700">Pattern</label>
                  <input type="text" id="rule-pattern" v-model="form.pattern" tabindex="0"
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    placeholder="Enter regex pattern" required @focus="logFocus('Pattern input')" />
                </div>

                <!-- Buttons -->
                <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
                  <button type="submit" tabindex="0"
                    class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:ml-3 sm:w-auto disabled:bg-indigo-400"
                    :disabled="saving" @focus="logFocus('Submit button')">
                    <svg v-if="saving" class="animate-spin h-5 w-5 mr-2 text-white" viewBox="0 0 24 24">
                      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8h8a8 8 0 01-8 8 8 8 0 01-8-8z">
                      </path>
                    </svg>
                    {{ editing ? 'Update' : 'Create' }}
                  </button>
                  <button type="button" tabindex="0"
                    class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto disabled:bg-gray-100"
                    @click="handleClose" :disabled="saving" @focus="logFocus('Cancel button')">
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
import { XMarkIcon } from '@heroicons/vue/24/outline'
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

const saving = ref(false)
const editing = computed(() => !!props.rule && props.rule.id)
const nameInput = ref(null)
const isFocusable = ref(false)

// Initialize form when rule prop changes
watch(
  () => props.rule,
  (newRule) => {
    console.log('CustomRuleForm: Rule changed', newRule)
    if (newRule && typeof newRule === 'object' && newRule.id) {
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
  },
  { immediate: true }
)

// Handle modal open/close and focus
watch(
  () => props.open,
  async (newOpen) => {
    console.log('CustomRuleForm: Open changed', newOpen)
    if (newOpen) {
      await nextTick()
      // Delay focus trap to ensure fields are rendered
      setTimeout(async () => {
        isFocusable.value = true
        if (nameInput.value) {
          console.log('CustomRuleForm: Attempting to focus name input', nameInput.value)
          try {
            nameInput.value.focus()
            console.log('CustomRuleForm: Name input focused successfully')
          } catch (err) {
            console.error('CustomRuleForm: Failed to focus name input', err)
          }
        } else {
          console.error('CustomRuleForm: nameInput ref is null')
        }
      }, 100) // Delay to ensure DOM is ready
    } else {
      isFocusable.value = false
    }
  },
  { immediate: true }
)

// Log focus events for debugging
const logFocus = (field) => {
  console.log(`CustomRuleForm: ${field} focused`)
}

// Handle close
const handleClose = () => {
  if (!saving.value) {
    console.log('CustomRuleForm: Closing')
    form.value = { name: '', category: 'ipv4_addr', type: 'regex', pattern: '' }
    isFocusable.value = false
    emit('close')
  }
}

// Save rule
const saveRule = async () => {
  try {
    saving.value = true
    console.log('CustomRuleForm: Saving rule', form.value)

    // Client-side validation
    if (!form.value.name || !form.value.category || !form.value.type) {
      emit('error', 'Please fill in all required fields')
      return
    }
    if (form.value.type === 'regex') {
      if (!form.value.pattern) {
        emit('error', 'Pattern is required for regex type rules')
        return
      }
      try {
        new RegExp(form.value.pattern) // Validate regex syntax
      } catch {
        emit('error', 'Invalid regex pattern')
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
    emit('error', `Failed to ${editing.value ? 'update' : 'create'} rule: ${err.message || 'Unknown error'}`)
  } finally {
    saving.value = false
  }
}
</script>