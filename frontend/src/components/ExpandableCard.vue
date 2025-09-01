<!--
GDPR Tool Expandable Card - Reusable Card Component

This component provides a reusable expandable card component for the GDPR compliance tool.
It displays content in a collapsible card format with optional icons, counts, and expandable sections.

Key Features:
- Expandable Content: Toggle between expanded and collapsed states
- Icon Support: Optional icon display with slot support
- Count Display: Optional numeric count display
- Flexible Content: Slot-based content system for maximum flexibility
- Responsive Design: Mobile-first responsive layout
- Event Emission: Emits expanded/collapsed events for parent components

Props:
- title: Card title (required)
- subtitle: Optional subtitle text
- icon: Optional icon component (Heroicons compatible)
- count: Optional numeric count to display
- expandable: Whether the card can be expanded (default: true)
- initialExpanded: Initial expansion state (default: false)

Slots:
- icon: Custom icon slot
- content: Main content area (shown when expanded)

Events:
- expanded: Emitted when card is expanded
- collapsed: Emitted when card is collapsed

The component provides a consistent card interface with smooth animations
and flexible content management for the GDPR compliance tool.
-->

<script setup>
import { ref, watch } from 'vue'
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  subtitle: {
    type: String,
    default: '',
  },
  icon: {
    type: [Object, Function, null], // Allow Object, Function, or null for Heroicons
    default: null,
  },
  count: {
    type: Number,
    default: undefined,
  },
  expandable: {
    type: Boolean,
    default: true,
  },
  initialExpanded: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['expanded', 'collapsed'])
const expanded = ref(props.initialExpanded)

watch(
  () => props.initialExpanded,
  (value) => {
    expanded.value = value
  },
)

const toggleExpanded = () => {
  if (!props.expandable) return

  expanded.value = !expanded.value
  emit(expanded.value ? 'expanded' : 'collapsed')
}
</script>

<template>
  <div class="relative overflow-hidden rounded-lg bg-white shadow">
    <div class="px-4 pb-5 pt-5 sm:px-6 sm:pt-6">
      <button @click="toggleExpanded" class="w-full text-left">
        <div class="relative">
          <div v-if="$slots.icon || icon" class="absolute rounded-md bg-primary p-3">
            <slot name="icon">
              <component :is="icon" class="h-6 w-6 text-white" aria-hidden="true" />
            </slot>
          </div>
          <div class="flex items-center justify-between" :class="{ 'ml-16': $slots.icon || icon }">
            <div>
              <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
              <p v-if="subtitle" class="text-sm text-gray-500">{{ subtitle }}</p>
            </div>
            <component :is="expanded ? ChevronUpIcon : ChevronDownIcon" class="h-5 w-5 text-gray-400"
              v-if="expandable" />
          </div>
          <div v-if="count !== undefined" :class="{ 'ml-16': $slots.icon || icon }" class="flex items-baseline pb-4">
            <p class="text-2xl font-semibold text-gray-900">
              {{ count }}
            </p>
          </div>
        </div>
      </button>

      <div v-if="!expandable || expanded" :class="{ 'mt-4 border-t pt-4': expandable }">
        <slot name="content"></slot>
      </div>
    </div>
  </div>
</template>
