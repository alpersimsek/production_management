<template>
  <div class="w-full">
    <!-- Label -->
    <label v-if="label" :for="inputId" class="block text-sm font-semibold text-gray-900 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <div class="relative rounded-md shadow-sm">
      <!-- Select element -->
      <select :id="inputId" :name="inputId" :value="modelValue" :disabled="disabled" :required="required" :class="[
        'block w-full rounded-md bg-white/95 border border-gray-200 shadow-sm focus:border-primary focus:ring-primary focus:ring-offset-1 sm:text-sm py-2 pr-8 appearance-none',
        { 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:outline-none focus:ring-red-500': error },
        { 'bg-gray-50 text-gray-500': disabled },
        customClass
      ]" @change="$emit('update:modelValue', $event.target.value)" v-bind="$attrs">
        <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
        <slot></slot>
      </select>
      <!-- Custom arrow -->
      <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-3">
        <svg class="h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"
          aria-hidden="true">
          <path fill-rule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clip-rule="evenodd" />
        </svg>
      </div>
    </div>

    <!-- Helper text or error message -->
    <p v-if="error || helperText" class="mt-1 text-sm" :class="error ? 'text-red-500' : 'text-gray-500'">
      {{ error || helperText }}
    </p>
  </div>
</template>

<script setup>
// Generate a unique ID for this component instance
const instanceId = `select-${Math.random().toString(36).substring(2, 9)}`

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  label: {
    type: String,
    default: ''
  },
  id: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  customClass: {
    type: String,
    default: ''
  }
})

// Generate ID if not provided
const inputId = props.id || instanceId

defineEmits(['update:modelValue'])
</script>