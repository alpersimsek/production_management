<!--
GDPR Tool Toast Notification - Modern Toast Message Component

This component provides a modern, animated toast notification system for the GDPR tool.
It displays success, info, warning, and error messages with smooth animations and auto-dismiss.

Key Features:
- Modern Design: Clean, modern toast design with smooth animations
- Multiple Types: Success, info, warning, and error message types
- Auto Dismiss: Automatic dismissal after configurable duration
- Manual Dismiss: Click to dismiss functionality
- Stack Support: Multiple toasts can be displayed simultaneously
- Responsive: Mobile-first responsive design
- Accessibility: Proper ARIA labels and keyboard navigation

Props:
- open: Whether the toast is visible (boolean, required)
- type: Toast type - 'success', 'info', 'warning', 'error' (string, default: 'info')
- title: Toast title (string, optional)
- message: Toast message (string, required)
- duration: Auto-dismiss duration in ms (number, default: 5000)
- position: Toast position (string, default: 'top-right')

Events:
- close: Emitted when toast is closed
- dismiss: Emitted when toast is dismissed

Features:
- Smooth Animations: Slide-in and fade-out animations
- Icon Support: Type-specific icons for visual clarity
- Progress Bar: Visual countdown for auto-dismiss
- Hover Pause: Pauses auto-dismiss on hover
- Click to Dismiss: Click anywhere to dismiss
- Keyboard Support: ESC key to dismiss
-->

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { 
  CheckCircleIcon, 
  InformationCircleIcon, 
  ExclamationTriangleIcon, 
  XCircleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  open: { type: Boolean, required: true },
  type: { type: String, default: 'info', validator: (value) => ['success', 'info', 'warning', 'error'].includes(value) },
  title: { type: String, default: '' },
  message: { type: String, required: true },
  duration: { type: Number, default: 5000 },
  position: { type: String, default: 'top-right', validator: (value) => ['top-left', 'top-right', 'bottom-left', 'bottom-right'].includes(value) }
})

const emit = defineEmits(['close', 'dismiss'])

const isVisible = ref(false)
const isLeaving = ref(false)
const progress = ref(100)
const timer = ref(null)
const isHovered = ref(false)

const toastConfig = computed(() => {
  const configs = {
    success: {
      icon: CheckCircleIcon,
      iconColor: 'text-green-500',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-800',
      titleColor: 'text-green-900',
      progressColor: 'bg-green-500'
    },
    info: {
      icon: InformationCircleIcon,
      iconColor: 'text-blue-500',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-200',
      textColor: 'text-blue-800',
      titleColor: 'text-blue-900',
      progressColor: 'bg-blue-500'
    },
    warning: {
      icon: ExclamationTriangleIcon,
      iconColor: 'text-yellow-500',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-800',
      titleColor: 'text-yellow-900',
      progressColor: 'bg-yellow-500'
    },
    error: {
      icon: XCircleIcon,
      iconColor: 'text-red-500',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-800',
      titleColor: 'text-red-900',
      progressColor: 'bg-red-500'
    }
  }
  
  return configs[props.type] || configs.info
})

const positionClasses = computed(() => {
  const positions = {
    'top-left': 'top-4 left-4',
    'top-right': 'top-4 right-4',
    'bottom-left': 'bottom-4 left-4',
    'bottom-right': 'bottom-4 right-4'
  }
  return positions[props.position] || positions['top-right']
})

const startTimer = () => {
  if (timer.value) clearInterval(timer.value)
  
  progress.value = 100
  const interval = 50 // Update every 50ms for smooth animation
  const decrement = (100 / (props.duration / interval))
  
  timer.value = setInterval(() => {
    if (!isHovered.value) {
      progress.value -= decrement
      if (progress.value <= 0) {
        dismiss()
      }
    }
  }, interval)
}

const pauseTimer = () => {
  if (timer.value) {
    clearInterval(timer.value)
    timer.value = null
  }
}

const resumeTimer = () => {
  if (!isHovered.value && props.duration > 0) {
    startTimer()
  }
}

const dismiss = () => {
  isLeaving.value = true
  pauseTimer()
  
  // Remove event listener when dismissing
  document.removeEventListener('keydown', handleKeydown)
  
  setTimeout(() => {
    emit('dismiss')
    emit('close')
  }, 300) // Wait for animation to complete
}

const handleClose = () => {
  dismiss()
}

const handleKeydown = (event) => {
  if (event.key === 'Escape' && isVisible.value && !isLeaving.value) {
    event.stopPropagation()
    event.preventDefault()
    dismiss()
  }
}

onMounted(() => {
  if (props.open) {
    // Small delay to ensure smooth animation
    setTimeout(() => {
      isVisible.value = true
      if (props.duration > 0) {
        startTimer()
      }
    }, 10)
  }
})

onUnmounted(() => {
  pauseTimer()
  document.removeEventListener('keydown', handleKeydown)
})

// Watch for open prop changes
watch(() => props.open, (newValue) => {
  if (newValue) {
    isVisible.value = true
    isLeaving.value = false
    if (props.duration > 0) {
      startTimer()
    }
    // Add event listener when toast becomes visible (remove first to prevent duplicates)
    document.removeEventListener('keydown', handleKeydown)
    document.addEventListener('keydown', handleKeydown)
  } else {
    // Remove event listener when toast is closed
    document.removeEventListener('keydown', handleKeydown)
    dismiss()
  }
}, { immediate: true })
</script>

<template>
  <Transition
    enter-active-class="transform transition-all duration-300 ease-out"
    enter-from-class="translate-x-full opacity-0 scale-95"
    enter-to-class="translate-x-0 opacity-100 scale-100"
    leave-active-class="transform transition-all duration-300 ease-in"
    leave-from-class="translate-x-0 opacity-100 scale-100"
    leave-to-class="translate-x-full opacity-0 scale-95"
  >
    <div
      v-if="open && isVisible && !isLeaving"
      :class="[
        'fixed z-50 max-w-sm w-full shadow-lg rounded-lg border p-4 cursor-pointer',
        positionClasses,
        toastConfig.bgColor,
        toastConfig.borderColor
      ]"
      @click="handleClose"
      @mouseenter="isHovered = true; pauseTimer()"
      @mouseleave="isHovered = false; resumeTimer()"
      role="alert"
      :aria-live="type === 'error' ? 'assertive' : 'polite'"
    >
      <!-- Progress Bar -->
      <div
        v-if="duration > 0"
        class="absolute top-0 left-0 h-1 rounded-t-lg transition-all duration-75 ease-linear"
        :class="toastConfig.progressColor"
        :style="{ width: `${progress}%` }"
      ></div>

      <div class="flex items-start">
        <!-- Icon -->
        <div class="flex-shrink-0">
          <component 
            :is="toastConfig.icon" 
            :class="['h-5 w-5', toastConfig.iconColor]" 
            aria-hidden="true" 
          />
        </div>

        <!-- Content -->
        <div class="ml-3 flex-1">
          <h3 v-if="title" :class="['text-sm font-semibold', toastConfig.titleColor]">
            {{ title }}
          </h3>
          <p :class="['text-sm', toastConfig.textColor, { 'mt-1': title }]">
            {{ message }}
          </p>
        </div>

        <!-- Close Button -->
        <div class="ml-4 flex-shrink-0">
          <button
            type="button"
            @click.stop="handleClose"
            :class="[
              'inline-flex rounded-md p-1.5 focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors duration-200',
              toastConfig.iconColor,
              'hover:bg-black hover:bg-opacity-5 focus:ring-gray-500'
            ]"
            aria-label="Close notification"
          >
            <XMarkIcon class="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<style scoped>
/* Custom animations for different positions */
.top-left .transform {
  transform-origin: top left;
}

.top-right .transform {
  transform-origin: top right;
}

.bottom-left .transform {
  transform-origin: bottom left;
}

.bottom-right .transform {
  transform-origin: bottom right;
}
</style>
