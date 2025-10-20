<template>
  <button
    :class="buttonClasses"
    :disabled="disabled || loading"
    :type="type"
    @click="handleClick"
  >
    <!-- Loading Spinner -->
    <svg
      v-if="loading"
      class="animate-spin -ml-1 mr-2 h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        class="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        stroke-width="4"
      />
      <path
        class="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
      />
    </svg>

    <!-- Icon (if provided) -->
    <component
      v-if="icon && !loading"
      :is="icon"
      class="w-4 h-4 mr-2"
    />

    <!-- Button Content -->
    <slot />
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { componentVariants } from '@/design-system'

const props = defineProps({
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'success', 'warning', 'error', 'ghost'].includes(value)
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
  },
  disabled: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'button'
  },
  icon: {
    type: [String, Object],
    default: null
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['click'])

const buttonClasses = computed(() => {
  const baseClasses = [
    'inline-flex',
    'items-center',
    'justify-center',
    'font-medium',
    'rounded-md',
    'transition-colors',
    'duration-200',
    'focus:outline-none',
    'focus:ring-2',
    'focus:ring-offset-2',
    'disabled:cursor-not-allowed'
  ]

  // Size classes
  const sizeClasses = {
    xs: 'px-2.5 py-1.5 text-xs',
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-2 text-sm',
    lg: 'px-4 py-2 text-base',
    xl: 'px-6 py-3 text-base'
  }

  // Variant classes
  const variantClasses = componentVariants.button[props.variant]
  const variantClass = props.disabled
    ? variantClasses.disabled
    : props.loading
      ? variantClasses.loading
      : variantClasses.base

  // Width classes
  const widthClasses = props.fullWidth ? 'w-full' : ''

  // Focus ring color
  const focusRingClasses = {
    primary: 'focus:ring-primary-500',
    secondary: 'focus:ring-secondary-500',
    success: 'focus:ring-success-500',
    warning: 'focus:ring-warning-500',
    error: 'focus:ring-error-500',
    ghost: 'focus:ring-secondary-500'
  }

  return [
    ...baseClasses,
    sizeClasses[props.size],
    variantClass,
    widthClasses,
    focusRingClasses[props.variant]
  ].filter(Boolean).join(' ')
})

const handleClick = (event) => {
  if (!props.disabled && !props.loading) {
    emit('click', event)
  }
}
</script>
