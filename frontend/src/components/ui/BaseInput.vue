<template>
  <div class="space-y-1">
    <!-- Label -->
    <label
      v-if="label"
      :for="inputId"
      class="block text-sm font-medium text-secondary-700"
    >
      {{ label }}
      <span v-if="required" class="text-error-500 ml-1">*</span>
    </label>

    <!-- Input Container -->
    <div class="relative">
      <!-- Prefix Icon -->
      <div
        v-if="prefixIcon"
        class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
      >
        <component
          :is="prefixIcon"
          class="h-5 w-5 text-secondary-400"
        />
      </div>

      <!-- Input Field -->
      <input
        :id="inputId"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :class="inputClasses"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />

      <!-- Suffix Icon -->
      <div
        v-if="suffixIcon"
        class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none"
      >
        <component
          :is="suffixIcon"
          class="h-5 w-5 text-secondary-400"
        />
      </div>

      <!-- Clear Button -->
      <button
        v-if="clearable && modelValue && !disabled"
        type="button"
        class="absolute inset-y-0 right-0 pr-3 flex items-center"
        @click="handleClear"
      >
        <svg class="h-5 w-5 text-secondary-400 hover:text-secondary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>

    <!-- Helper Text -->
    <p
      v-if="helperText && !error"
      class="text-sm text-secondary-500"
    >
      {{ helperText }}
    </p>

    <!-- Error Message -->
    <p
      v-if="error"
      class="text-sm text-error-600"
    >
      {{ error }}
    </p>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { componentVariants } from '@/design-system'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  label: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  },
  disabled: {
    type: Boolean,
    default: false
  },
  readonly: {
    type: Boolean,
    default: false
  },
  required: {
    type: Boolean,
    default: false
  },
  clearable: {
    type: Boolean,
    default: false
  },
  prefixIcon: {
    type: [String, Object],
    default: null
  },
  suffixIcon: {
    type: [String, Object],
    default: null
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus', 'clear'])

const inputId = ref(`input-${Math.random().toString(36).substr(2, 9)}`)

const inputClasses = computed(() => {
  const baseClasses = [
    'block',
    'w-full',
    'rounded-md',
    'border',
    'shadow-sm',
    'transition-colors',
    'duration-200',
    'focus:outline-none',
    'focus:ring-2',
    'focus:ring-offset-0'
  ]

  // Size classes
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  }

  // State classes
  let stateClasses = ''
  if (props.error) {
    stateClasses = 'border-error-500 focus:ring-error-500 focus:border-error-500'
  } else if (props.disabled) {
    stateClasses = 'bg-secondary-50 text-secondary-500 cursor-not-allowed border-secondary-200'
  } else {
    stateClasses = 'border-secondary-300 focus:ring-primary-500 focus:border-primary-500'
  }

  // Padding adjustments for icons
  const paddingClasses = []
  if (props.prefixIcon) {
    paddingClasses.push('pl-10')
  }
  if (props.suffixIcon || props.clearable) {
    paddingClasses.push('pr-10')
  }

  return [
    ...baseClasses,
    sizeClasses[props.size],
    stateClasses,
    ...paddingClasses
  ].join(' ')
})

const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleFocus = (event) => {
  emit('focus', event)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
}
</script>