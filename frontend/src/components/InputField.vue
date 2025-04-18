<template>
  <div class="w-full">
    <!-- Label -->
    <label v-if="label" :for="inputId" class="block text-sm font-medium text-gray-700 mb-1">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Input wrapper for prefix/suffix -->
    <div class="relative rounded-md shadow-sm">
      <!-- Prefix icon or text -->
      <div v-if="$slots.prefix || prefix" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <slot name="prefix">
          <span class="text-gray-500 sm:text-sm">{{ prefix }}</span>
        </slot>
      </div>

      <!-- Input element -->
      <input
        :id="inputId"
        :name="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :class="[
          'block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm py-2',
          { 'pl-7': $slots.prefix || prefix },
          { 'pr-7': $slots.suffix || suffix },
          { 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:outline-none focus:ring-red-500': error },
          { 'bg-gray-50 text-gray-500': disabled || readonly },
          customClass
        ]"
        @input="$emit('update:modelValue', $event.target.value)"
        v-bind="$attrs"
      />

      <!-- Suffix icon or text -->
      <div v-if="$slots.suffix || suffix" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
        <slot name="suffix">
          <span class="text-gray-500 sm:text-sm">{{ suffix }}</span>
        </slot>
      </div>
    </div>

    <!-- Helper text or error message -->
    <p v-if="error || helperText" class="mt-1 text-sm" :class="error ? 'text-red-600' : 'text-gray-500'">
      {{ error || helperText }}
    </p>
  </div>
</template>

<script setup>
// Define props first
const props = defineProps({
  // Input attributes
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
  name: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  placeholder: {
    type: String,
    default: ''
  },
  // Validation
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
  // State
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  // Decoration
  prefix: {
    type: String,
    default: ''
  },
  suffix: {
    type: String,
    default: ''
  },
  // Additional styling
  customClass: {
    type: String,
    default: ''
  }
})

// Generate ID if not provided
const inputId = props.id || `input-${Math.random().toString(36).substring(2, 9)}`

defineEmits(['update:modelValue'])
</script>
