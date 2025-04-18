<template>
  <li class="group relative flex items-center space-x-3 rounded-lg border border-gray-300 bg-white px-5 py-4 shadow-sm" :class="customClass">
    <!-- Icon -->
    <div v-if="icon || $slots.icon" class="flex-shrink-0">
      <slot name="icon">
        <component
          :is="icon"
          class="h-6 w-6"
          :class="iconClass"
          aria-hidden="true"
        />
      </slot>
    </div>

    <!-- Content -->
    <div class="min-w-0 flex-1">
      <slot>
        <p class="text-sm font-medium text-gray-900 truncate">{{ title }}</p>
        <div v-if="subtitle || metadata" class="flex text-sm text-gray-500 gap-2">
          <p v-if="subtitle" class="truncate">{{ subtitle }}</p>
          <span v-if="subtitle && metadata">&middot;</span>
          <p v-if="metadata">{{ metadata }}</p>
        </div>
      </slot>
    </div>

    <!-- Actions -->
    <div v-if="$slots.actions" class="flex gap-2">
      <slot name="actions"></slot>
    </div>
  </li>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  metadata: {
    type: String,
    default: ''
  },
  icon: {
    type: [Object, null],
    default: null
  },
  iconClass: {
    type: String,
    default: 'text-gray-400'
  },
  customClass: {
    type: String,
    default: ''
  }
})
</script>
