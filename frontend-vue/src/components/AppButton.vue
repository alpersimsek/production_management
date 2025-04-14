<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="[
      'inline-flex flex-row items-center justify-center rounded-md text-sm font-medium focus:outline-none focus:ring-2 focus:ring-offset-2',
      sizeClasses,
      variantClasses,
      { 'opacity-50 cursor-not-allowed': disabled },
      { 'relative': loading },
      customClass
    ]"
    v-bind="$attrs"
    @click="$emit('click', $event)"
  >
    <!-- Loading spinner -->
    <span v-if="loading" class="absolute inset-0 flex items-center justify-center">
      <svg class="animate-spin h-5 w-5 text-current" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </span>

    <!-- Button content with opacity when loading -->
    <span :class="['flex flex-row items-center', { 'opacity-0': loading }]">
      <!-- Leading icon slot -->
      <slot name="icon-left"></slot>

      <!-- Button text -->
      <slot></slot>

      <!-- Trailing icon slot -->
      <slot name="icon-right"></slot>
    </span>
  </button>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  // Button appearance
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger', 'warning', 'success', 'text'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  // Button behavior
  type: {
    type: String,
    default: 'button'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  // Additional styling
  customClass: {
    type: String,
    default: ''
  }
})

defineEmits(['click'])

// Computed classes based on variant
const variantClasses = computed(() => {
  const variants = {
    primary: 'border border-transparent bg-indigo-600 text-white shadow-sm hover:bg-indigo-700 focus:ring-indigo-500',
    secondary: 'border border-gray-300 bg-white text-gray-700 shadow-sm hover:bg-gray-50 focus:ring-indigo-500',
    danger: 'border border-transparent bg-red-600 text-white shadow-sm hover:bg-red-700 focus:ring-red-500',
    warning: 'border border-transparent bg-yellow-600 text-white shadow-sm hover:bg-yellow-700 focus:ring-yellow-500',
    success: 'border border-transparent bg-green-600 text-white shadow-sm hover:bg-green-700 focus:ring-green-500',
    text: 'border-none bg-transparent text-indigo-600 hover:text-indigo-800 hover:underline focus:ring-indigo-500 shadow-none'
  }

  return variants[props.variant]
})

// Computed classes based on size
const sizeClasses = computed(() => {
  const sizes = {
    sm: 'px-2.5 py-1.5 text-xs',
    md: 'px-4 py-2 text-sm',
    lg: 'px-6 py-3 text-base'
  }

  return sizes[props.size]
})
</script>
