<!--
GDPR Tool Select Field - Reusable Select Component

This component provides a reusable select dropdown component for the GDPR compliance tool.
It supports validation states, custom styling, and accessibility features for form inputs.

Key Features:
- Custom Styling: Tailwind CSS with custom arrow and focus states
- Validation States: Error states with visual feedback
- Accessibility: Proper labeling and ARIA attributes
- Helper Text: Optional helper text and error messages
- v-model Support: Two-way data binding
- Placeholder Support: Optional placeholder option
- Custom Styling: Additional CSS classes support

Props:
- modelValue: Select value (v-model)
- label: Select label text
- id: Select ID (auto-generated if not provided)
- placeholder: Placeholder text for first option
- required: Whether select is required
- error: Error message to display
- helperText: Helper text to display
- disabled: Whether select is disabled
- customClass: Additional CSS classes

Slots:
- default: Option elements for the select

Events:
- update:modelValue: Emitted when select value changes

The component provides consistent select styling and behavior across the
GDPR compliance tool with proper validation and accessibility support.
-->

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

<template>
  <div class="w-full">
    <!-- Label -->
    <label v-if="label" :for="inputId" class="block text-sm font-semibold text-slate-900 mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <div class="relative group">
      <!-- Select element -->
      <select :id="inputId" :name="inputId" :value="modelValue" :disabled="disabled" :required="required" :class="[
        'block w-full rounded-2xl bg-white/95 backdrop-blur-sm border border-slate-200/80 shadow-sm focus:border-slate-400 focus:ring-2 focus:ring-slate-400/20 focus:ring-offset-0 sm:text-sm py-3.5 px-4 pr-12 appearance-none transition-all duration-300 hover:border-slate-300/90 hover:shadow-md focus:shadow-lg hover:bg-white/98 focus:bg-white',
        { 'border-red-300 text-red-900 placeholder-red-300 focus:border-red-500 focus:ring-red-500/20 focus:outline-none': error },
        { 'bg-slate-50/90 text-slate-500 cursor-not-allowed hover:bg-slate-50/90': disabled },
        customClass
      ]" @change="$emit('update:modelValue', $event.target.value)" v-bind="$attrs">
        <option v-if="placeholder" value="" disabled>{{ placeholder }}</option>
        <slot></slot>
      </select>
      <!-- Custom arrow with enhanced styling -->
      <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-4">
        <svg class="h-5 w-5 text-slate-400 transition-all duration-200 group-hover:text-slate-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor"
          aria-hidden="true">
          <path fill-rule="evenodd"
            d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"
            clip-rule="evenodd" />
        </svg>
      </div>
    </div>

    <!-- Helper text or error message -->
    <p v-if="error || helperText" class="mt-2 text-sm flex items-center" :class="error ? 'text-red-600' : 'text-slate-600'">
      <svg v-if="error" class="h-4 w-4 mr-1.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      {{ error || helperText }}
    </p>
  </div>
</template>