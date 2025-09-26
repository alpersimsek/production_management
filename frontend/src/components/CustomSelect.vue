<!--
GDPR Tool Custom Select - Professional Dropdown Component

This component provides a fully customizable select dropdown with professional styling
for list items, borders, hover effects, and focus states. It replaces native select
elements with a custom implementation for better visual control.

Key Features:
- Custom List Styling: Full control over dropdown list appearance
- Professional Hover Effects: Smooth transitions and visual feedback
- Border Management: Clean borders with proper visibility
- Focus States: Enhanced keyboard navigation
- Accessibility: Proper ARIA attributes and keyboard support
- Search Support: Optional search functionality
- Loading States: Visual feedback during data loading

Props:
- modelValue: Selected value (v-model)
- options: Array of option objects { value, label, disabled }
- placeholder: Placeholder text
- label: Field label
- required: Whether field is required
- error: Error message
- disabled: Whether field is disabled
- searchable: Enable search functionality
- loading: Loading state

Events:
- update:modelValue: Emitted when selection changes
- search: Emitted when search query changes (if searchable)
-->

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ChevronDownIcon, MagnifyingGlassIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  placeholder: {
    type: String,
    default: 'Select an option...'
  },
  label: {
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
  disabled: {
    type: Boolean,
    default: false
  },
  searchable: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'search'])

// State
const isOpen = ref(false)
const searchQuery = ref('')
const selectedIndex = ref(-1)
const dropdownRef = ref(null)
const searchInputRef = ref(null)

// Computed
const filteredOptions = computed(() => {
  if (!props.searchable || !searchQuery.value) {
    return props.options
  }
  return props.options.filter(option => 
    option.label.toLowerCase().includes(searchQuery.value.toLowerCase())
  )
})

const selectedOption = computed(() => {
  return props.options.find(option => option.value === props.modelValue)
})

const displayText = computed(() => {
  if (selectedOption.value) {
    return selectedOption.value.label
  }
  return props.placeholder
})

// Check if dropdown is inside a modal
const isInsideModal = computed(() => {
  return dropdownRef.value?.closest('[role="dialog"]') !== null
})

// Dynamic z-index based on context
const dropdownZIndex = computed(() => {
  return isInsideModal.value ? 'z-[999999]' : 'z-[99999]'
})

// Simple dropdown positioning - no complex calculations needed

// Methods
const toggleDropdown = (event) => {
  if (props.disabled || props.loading) return
  
  // Prevent event propagation when inside a modal to avoid conflicts
  if (isInsideModal.value && event) {
    event.stopPropagation()
  }
  
  isOpen.value = !isOpen.value
  if (isOpen.value && props.searchable) {
    nextTick(() => {
      searchInputRef.value?.focus()
    })
  }
}

const selectOption = (option, event) => {
  if (option.disabled) return
  
  // Prevent event propagation when inside a modal to avoid conflicts
  if (isInsideModal.value && event) {
    event.stopPropagation()
  }
  
  emit('update:modelValue', option.value)
  isOpen.value = false
  searchQuery.value = ''
  selectedIndex.value = -1
}

const handleKeydown = (event) => {
  if (!isOpen.value) {
    if (event.key === 'Enter' || event.key === ' ' || event.key === 'ArrowDown') {
      event.preventDefault()
      toggleDropdown()
    }
    return
  }

  switch (event.key) {
    case 'ArrowDown':
      event.preventDefault()
      selectedIndex.value = Math.min(selectedIndex.value + 1, filteredOptions.value.length - 1)
      break
    case 'ArrowUp':
      event.preventDefault()
      selectedIndex.value = Math.max(selectedIndex.value - 1, -1)
      break
    case 'Enter':
      event.preventDefault()
      if (selectedIndex.value >= 0 && filteredOptions.value[selectedIndex.value]) {
        selectOption(filteredOptions.value[selectedIndex.value])
      }
      break
    case 'Escape':
      event.preventDefault()
      isOpen.value = false
      selectedIndex.value = -1
      break
  }
}

const handleSearch = (event) => {
  searchQuery.value = event.target.value
  emit('search', searchQuery.value)
  selectedIndex.value = -1
}

const closeDropdown = () => {
  isOpen.value = false
  selectedIndex.value = -1
  searchQuery.value = ''
}

// Body scroll lock methods - only lock if not inside a modal
const lockBodyScroll = () => {
  // Don't lock body scroll when inside a modal to avoid conflicts
  if (isInsideModal.value) {
    return
  }
  
  // Store the current scrollbar width
  const scrollbarWidth = window.innerWidth - document.documentElement.clientWidth
  document.body.style.overflow = 'hidden'
  document.body.style.paddingRight = `${scrollbarWidth}px`
}

const unlockBodyScroll = () => {
  // Don't unlock body scroll when inside a modal to avoid conflicts
  if (isInsideModal.value) {
    return
  }
  
  document.body.style.overflow = ''
  document.body.style.paddingRight = ''
}

// Click outside handler - improved for modal contexts
const handleClickOutside = (event) => {
  if (!dropdownRef.value || dropdownRef.value.contains(event.target)) {
    return
  }
  
  // Check if the click is on a modal backdrop or close button
  const isModalBackdrop = event.target.classList.contains('backdrop-blur-sm') || 
                         event.target.closest('[role="dialog"]')
  
  // If clicking on modal backdrop, don't close dropdown to avoid conflicts
  if (isModalBackdrop) {
    return
  }
  
  closeDropdown()
}

// Watchers
watch(() => props.modelValue, () => {
  selectedIndex.value = -1
})

// Watch dropdown open state to lock/unlock body scroll
watch(isOpen, (newValue) => {
  if (newValue) {
    lockBodyScroll()
    // Ensure focus stays within modal when dropdown opens
    if (isInsideModal.value) {
      nextTick(() => {
        const modal = dropdownRef.value?.closest('[role="dialog"]')
        if (modal && !modal.contains(document.activeElement)) {
          dropdownRef.value?.focus()
        }
      })
    }
  } else {
    unlockBodyScroll()
  }
})

// Lifecycle
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  // Ensure body scroll is unlocked when component is destroyed
  unlockBodyScroll()
})
</script>

<template>
  <div class="w-full">
    <!-- Label -->
    <label v-if="label" class="block text-sm font-semibold text-slate-900 mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Dropdown Container -->
    <div ref="dropdownRef" class="relative group">
      <!-- Trigger Button -->
      <button
        type="button"
        :disabled="disabled || loading"
        @click="toggleDropdown"
        @keydown="handleKeydown"
        :class="[
          'relative w-full rounded-2xl bg-white/95 backdrop-blur-sm border border-slate-200/80 shadow-sm focus:border-slate-400 focus:ring-2 focus:ring-slate-400/20 focus:ring-offset-0 sm:text-sm py-3.5 px-4 pr-12 appearance-none transition-all duration-300 hover:border-slate-300/90 hover:shadow-md focus:shadow-lg hover:bg-white/98 focus:bg-white text-left',
          { 'border-red-300 text-red-900 focus:border-red-500 focus:ring-red-500/20 focus:outline-none': error },
          { 'bg-slate-50/90 text-slate-500 cursor-not-allowed hover:bg-slate-50/90': disabled || loading }
        ]"
        :aria-expanded="isOpen"
        :aria-haspopup="true"
        :aria-label="label"
      >
        <span :class="{ 'text-slate-500': !selectedOption }">{{ displayText }}</span>
        
        <!-- Loading Spinner -->
        <div v-if="loading" class="absolute inset-y-0 right-0 flex items-center pr-4">
          <svg class="animate-spin h-5 w-5 text-slate-400" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </div>
        
        <!-- Chevron Icon -->
        <div v-else class="absolute inset-y-0 right-0 flex items-center pr-4">
          <ChevronDownIcon 
            :class="[
              'h-5 w-5 text-slate-400 transition-all duration-200',
              { 'rotate-180': isOpen, 'group-hover:text-slate-500': !disabled && !loading }
            ]"
          />
        </div>
      </button>

      <!-- Dropdown List -->
      <Transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform scale-95 opacity-0"
        enter-to-class="transform scale-100 opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="transform scale-100 opacity-100"
        leave-to-class="transform scale-95 opacity-0"
      >
        <div
          v-if="isOpen"
          :class="[
            'absolute top-full left-0 right-0 mt-1 rounded-2xl bg-white border border-slate-200 shadow-xl max-h-60 overflow-hidden',
            dropdownZIndex
          ]"
        >
          <!-- Search Input -->
          <div v-if="searchable" class="p-3 border-b border-slate-200/60">
            <div class="relative">
              <MagnifyingGlassIcon class="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                ref="searchInputRef"
                v-model="searchQuery"
                @input="handleSearch"
                type="text"
                placeholder="Search options..."
                class="w-full pl-10 pr-4 py-2 text-sm border border-slate-200/60 rounded-xl bg-white/80 focus:outline-none focus:ring-2 focus:ring-slate-400/20 focus:border-slate-400"
              />
            </div>
          </div>

          <!-- Options List -->
          <div class="max-h-48 overflow-y-auto">
            <div v-if="filteredOptions.length === 0" class="px-4 py-3 text-sm text-slate-500 text-center">
              {{ searchable && searchQuery ? 'No options found' : 'No options available' }}
            </div>
            
            <button
              v-for="(option, index) in filteredOptions"
              :key="option.value"
              type="button"
              :disabled="option.disabled"
              @click="selectOption(option, $event)"
              :class="[
                'w-full px-4 py-3 text-left text-sm transition-all duration-200 border-b border-slate-100/60 last:border-b-0',
                {
                  'bg-slate-50/80 text-slate-600 cursor-not-allowed': option.disabled,
                  'bg-slate-100/80 text-slate-900': selectedIndex === index && !option.disabled,
                  'hover:bg-slate-50/80 hover:text-slate-900': !option.disabled && selectedIndex !== index,
                  'bg-blue-50/80 text-blue-900 font-medium': option.value === modelValue && !option.disabled
                }
              ]"
            >
              <div class="flex items-center justify-between">
                <span>{{ option.label }}</span>
                <svg 
                  v-if="option.value === modelValue" 
                  class="h-4 w-4 text-blue-600" 
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </div>
            </button>
          </div>
        </div>
      </Transition>
    </div>

    <!-- Error Message -->
    <p v-if="error" class="mt-2 text-sm text-red-600 flex items-center">
      <svg class="h-4 w-4 mr-1.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
      </svg>
      {{ error }}
    </p>
  </div>
</template>
