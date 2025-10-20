<template>
  <div :class="cardClasses">
    <!-- Header -->
    <div
      v-if="title || $slots.header"
      class="px-6 py-4 border-b border-secondary-200"
    >
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <!-- Icon -->
          <div
            v-if="icon"
            :class="iconClasses"
          >
            <component :is="icon" class="w-5 h-5" />
          </div>

          <!-- Title -->
          <h3 class="text-lg font-semibold text-secondary-900 ml-3">
            <slot name="header">{{ title }}</slot>
          </h3>
        </div>

        <!-- Actions -->
        <div v-if="$slots.actions" class="flex items-center space-x-2">
          <slot name="actions" />
        </div>
      </div>

      <!-- Subtitle -->
      <p
        v-if="subtitle"
        class="mt-1 text-sm text-secondary-500"
      >
        {{ subtitle }}
      </p>
    </div>

    <!-- Body -->
    <div :class="bodyClasses">
      <slot />
    </div>

    <!-- Footer -->
    <div
      v-if="$slots.footer"
      class="px-6 py-4 border-t border-secondary-200 bg-secondary-50"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'base',
    validator: (value) => ['base', 'elevated', 'flat'].includes(value)
  },
  padding: {
    type: String,
    default: 'md',
    validator: (value) => ['none', 'sm', 'md', 'lg'].includes(value)
  },
  icon: {
    type: [String, Object],
    default: null
  },
  iconColor: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'error', 'secondary'].includes(value)
  },
  hover: {
    type: Boolean,
    default: false
  }
})

const cardClasses = computed(() => {
  const baseClasses = [
    'bg-white',
    'rounded-lg',
    'border',
    'border-secondary-200',
    'overflow-hidden'
  ]

  // Variant classes
  const variantClasses = {
    base: 'shadow-md',
    elevated: 'shadow-lg',
    flat: 'shadow-none'
  }

  // Hover effect
  const hoverClasses = props.hover ? 'hover:shadow-lg transition-shadow duration-200' : ''

  return [
    ...baseClasses,
    variantClasses[props.variant],
    hoverClasses
  ].join(' ')
})

const bodyClasses = computed(() => {
  const paddingClasses = {
    none: '',
    sm: 'px-4 py-3',
    md: 'px-6 py-4',
    lg: 'px-8 py-6'
  }

  return paddingClasses[props.padding]
})

const iconClasses = computed(() => {
  const colorClasses = {
    primary: 'text-primary-600 bg-primary-100',
    success: 'text-success-600 bg-success-100',
    warning: 'text-warning-600 bg-warning-100',
    error: 'text-error-600 bg-error-100',
    secondary: 'text-secondary-600 bg-secondary-100'
  }

  return [
    'flex',
    'items-center',
    'justify-center',
    'w-8',
    'h-8',
    'rounded-full',
    colorClasses[props.iconColor]
  ].join(' ')
})
</script>
