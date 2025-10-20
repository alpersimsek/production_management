<template>
  <Teleport to="body">
    <Transition
      enter-active-class="duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="isOpen"
        class="fixed inset-0 z-50 overflow-y-auto"
        @click="handleBackdropClick"
      >
        <!-- Backdrop -->
        <div class="fixed inset-0 bg-black bg-opacity-50 transition-opacity" />

        <!-- Modal Container -->
        <div class="flex min-h-full items-center justify-center p-4">
          <Transition
            enter-active-class="duration-300 ease-out"
            enter-from-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
            enter-to-class="opacity-100 translate-y-0 sm:scale-100"
            leave-active-class="duration-200 ease-in"
            leave-from-class="opacity-100 translate-y-0 sm:scale-100"
            leave-to-class="opacity-0 translate-y-4 sm:translate-y-0 sm:scale-95"
          >
            <div
              v-if="isOpen"
              :class="modalClasses"
              @click.stop
            >
              <!-- Header -->
              <div
                v-if="title || $slots.header"
                class="flex items-center justify-between px-6 py-4 border-b border-secondary-200"
              >
                <div class="flex items-center">
                  <!-- Icon -->
                  <div
                    v-if="icon"
                    :class="iconClasses"
                  >
                    <component :is="icon" class="w-6 h-6" />
                  </div>

                  <!-- Title -->
                  <h3 class="text-lg font-semibold text-secondary-900 ml-3">
                    <slot name="header">{{ title }}</slot>
                  </h3>
                </div>

                <!-- Close Button -->
                <button
                  v-if="closable"
                  type="button"
                  class="text-secondary-400 hover:text-secondary-600 transition-colors duration-200"
                  @click="handleClose"
                >
                  <svg class="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <!-- Body -->
              <div class="px-6 py-4">
                <slot />
              </div>

              <!-- Footer -->
              <div
                v-if="$slots.footer"
                class="flex items-center justify-end gap-3 px-6 py-4 border-t border-secondary-200 bg-secondary-50"
              >
                <slot name="footer" />
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, watch, nextTick } from 'vue'

const props = defineProps({
  isOpen: {
    type: Boolean,
    default: false
  },
  title: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl', '2xl', 'full'].includes(value)
  },
  closable: {
    type: Boolean,
    default: true
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  },
  icon: {
    type: [String, Object],
    default: null
  },
  iconColor: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'success', 'warning', 'error', 'secondary'].includes(value)
  }
})

const emit = defineEmits(['close', 'open'])

const modalClasses = computed(() => {
  const baseClasses = [
    'relative',
    'bg-white',
    'rounded-lg',
    'shadow-xl',
    'transform',
    'transition-all',
    'duration-300',
    'w-full',
    'max-h-[90vh]',
    'overflow-hidden'
  ]

  // Size classes
  const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-lg',
    xl: 'max-w-xl',
    '2xl': 'max-w-2xl',
    full: 'max-w-full mx-4'
  }

  return [...baseClasses, sizeClasses[props.size]].join(' ')
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
    'w-10',
    'h-10',
    'rounded-full',
    colorClasses[props.iconColor]
  ].join(' ')
})

const handleClose = () => {
  emit('close')
}

const handleBackdropClick = () => {
  if (props.closeOnBackdrop) {
    handleClose()
  }
}

// Handle escape key
const handleEscape = (event) => {
  if (event.key === 'Escape' && props.isOpen) {
    handleClose()
  }
}

// Watch for modal open/close
watch(() => props.isOpen, (isOpen) => {
  if (isOpen) {
    document.addEventListener('keydown', handleEscape)
    document.body.style.overflow = 'hidden'
    emit('open')
  } else {
    document.removeEventListener('keydown', handleEscape)
    document.body.style.overflow = ''
  }
})

// Cleanup on unmount
import { onUnmounted } from 'vue'
onUnmounted(() => {
  document.removeEventListener('keydown', handleEscape)
  document.body.style.overflow = ''
})
</script>