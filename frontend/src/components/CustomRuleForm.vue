<template>
  <Dialog as="div" class="relative" style="z-index: 25;" @close="$emit('close')" :open="open">
    <div class="fixed inset-0 backdrop-blur-sm bg-gray-500/50 transition-opacity" @mousedown.stop style="z-index: 25;" />
    <div class="fixed inset-0 overflow-y-auto" style="z-index: 25;">
      <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
        <DialogPanel
          class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6"
        >
          <div class="absolute right-0 top-0 hidden pr-4 pt-4 sm:block">
            <button
              type="button"
              class="rounded-md bg-white text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              @click="$emit('close')"
            >
              <span class="sr-only">Close</span>
              <XMarkIcon class="h-6 w-6" aria-hidden="true" />
            </button>
          </div>
          <div>
            <div class="mt-3 text-center sm:mt-0 sm:text-left">
              <DialogTitle as="h3" class="text-base font-semibold leading-6 text-gray-900">
                {{ editing ? 'Edit Rule' : 'Create New Rule' }}
              </DialogTitle>
              <div class="mt-4 space-y-4">
                <div>
                  <label for="rule-name" class="block text-sm font-medium text-gray-700">Name</label>
                  <div class="mt-1">
                    <input
                      type="text"
                      id="rule-name"
                      v-model="form.name"
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      placeholder="Rule name"
                    />
                  </div>
                </div>

                <div>
                  <label for="rule-category" class="block text-sm font-medium text-gray-700">Category</label>
                  <div class="mt-1">
                    <select
                      id="rule-category"
                      v-model="form.category"
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    >
                      <option value="ipv4_addr">IPv4 Address</option>
                      <option value="mac_addr">MAC Address</option>
                      <option value="username">Username</option>
                      <option value="domain">Domain</option>
                      <option value="phone_num">Phone Number</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label for="rule-type" class="block text-sm font-medium text-gray-700">Type</label>
                  <div class="mt-1">
                    <select
                      id="rule-type"
                      v-model="form.type"
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    >
                      <option value="regex">Regular Expression</option>
                      <option value="builtin">Built-in Rule</option>
                      <option value="placeholder">Placeholder</option>
                    </select>
                  </div>
                </div>

                <div v-if="form.type === 'regex'">
                  <label for="rule-pattern" class="block text-sm font-medium text-gray-700">Pattern</label>
                  <div class="mt-1">
                    <input
                      type="text"
                      id="rule-pattern"
                      v-model="form.pattern"
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                      placeholder="Enter regex pattern"
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse">
            <button
              type="button"
              class="inline-flex w-full justify-center rounded-md bg-indigo-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-indigo-500 sm:ml-3 sm:w-auto"
              @click="saveRule"
              :disabled="saving"
            >
              {{ editing ? 'Update' : 'Create' }}
            </button>
            <button
              type="button"
              class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
              @click="$emit('close')"
            >
              Cancel
            </button>
          </div>
        </DialogPanel>
      </div>
    </div>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
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

// Form data
const form = ref({
  name: '',
  category: 'ipv4_addr',
  type: 'regex',
  pattern: ''
})

// Helper functions
const getConfigFromPattern = (type, pattern) => {
  if (type === 'regex') {
    return { pattern, type }
  }
  // For other types, return a config with just the type
  return { type }
}

const getPatternFromConfig = (config) => {
  return config && config.pattern ? config.pattern : ''
}

// Computed values
const editing = computed(() => !!props.rule)
const saving = ref(false)

// Watch for changes to props
watch(() => props.open, (isOpen) => {
  if (isOpen) {
    initializeForm()
  }
})

// Initialize form data
const initializeForm = () => {
  if (props.rule) {
    // Edit mode
    form.value = {
      name: props.rule.name,
      category: props.rule.category,
      type: props.rule.type || 'regex',
      pattern: getPatternFromConfig(props.rule.config)
    }
  } else {
    // Create mode
    form.value = {
      name: '',
      category: 'ipv4_addr',
      type: 'regex',
      pattern: ''
    }
  }
}

// Save rule
const saveRule = async () => {
  try {
    saving.value = true

    if (!form.value.name || !form.value.category || !form.value.type) {
      emit('error', 'Please fill in all required fields')
      return
    }

    // Validate pattern is provided if type is regex
    if (form.value.type === 'regex' && !form.value.pattern) {
      emit('error', 'Pattern is required for regex type rules')
      return
    }

    const ruleData = {
      name: form.value.name,
      category: form.value.category,
      config: getConfigFromPattern(form.value.type, form.value.pattern)
    }

    let response
    if (props.rule) {
      // Update existing rule
      response = await ApiService.updateRule(props.rule.id, ruleData)
    } else {
      // Create new rule
      response = await ApiService.createRule(ruleData)
    }

    emit('saved', response)
    emit('close')
  } catch (err) {
    emit('error', `Failed to ${props.rule ? 'update' : 'create'} rule: ${err.message || 'Unknown error'}`)
  } finally {
    saving.value = false
  }
}

// Initialize form when component is created
initializeForm()
</script>
