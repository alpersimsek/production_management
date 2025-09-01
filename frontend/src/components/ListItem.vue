<!--
GDPR Tool List Item - Generic List Item Component

This component provides a generic list item for the GDPR compliance tool.
It displays content with icons, titles, subtitles, and action buttons.

Key Features:
- Flexible Content: Slot-based content system for customization
- Icon Support: Optional icon display with custom styling
- Title and Subtitle: Text content with metadata support
- Action Buttons: Slot for action buttons on the right side
- Custom Styling: Additional CSS classes support
- Responsive Design: Mobile-first responsive layout

Props:
- title: Main title text (string, optional)
- subtitle: Subtitle text (string, optional)
- metadata: Additional metadata text (string, optional)
- icon: Icon component (object, optional)
- iconClass: CSS classes for icon (string, default: 'text-gray-400')
- customClass: Additional CSS classes (string, optional)

Slots:
- default: Main content slot (overrides title/subtitle/metadata)
- icon: Custom icon slot (overrides icon prop)
- actions: Action buttons slot for the right side

Features:
- Icon Display: Optional icon with custom styling
- Content Flexibility: Slot-based content system
- Action Area: Dedicated area for action buttons
- Responsive Layout: Adapts to different screen sizes
- Custom Styling: Additional CSS classes for customization

The component provides a flexible list item interface for various content
types in the GDPR compliance tool with proper styling and accessibility.
-->

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
