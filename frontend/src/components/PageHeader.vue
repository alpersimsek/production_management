<!--
GDPR Tool Page Header - Standardized Page Header Component

This component provides a standardized page header for the GDPR compliance tool.
It displays page titles, descriptions, and action buttons with consistent styling.

Key Features:
- Page Title: Displays the main page title
- Description: Optional description text below the title
- Action Buttons: Slot for action buttons on the right side
- Responsive Design: Mobile-first responsive layout
- Flexible Content: Slot-based content system for customization

Props:
- title: Page title (string, required)
- description: Optional description text (string, optional)

Slots:
- description: Custom description slot (overrides prop description)
- actions: Action buttons slot for the right side

Features:
- Title Display: Clear, prominent page title
- Description Support: Optional description with slot override
- Action Area: Dedicated area for action buttons
- Responsive Layout: Adapts to different screen sizes
- Consistent Styling: Standardized header appearance

The component provides a consistent page header interface for all pages
in the GDPR compliance tool with proper responsive design and flexibility.
-->

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div class="sm:flex sm:items-center mb-8">
    <div class="sm:flex-auto">
      <h1 class="text-2xl font-semibold text-gray-900">{{ title }}</h1>
      <p v-if="description" class="mt-2 text-sm text-gray-700">
        {{ description }}
      </p>
      <slot name="description"></slot>
    </div>
    <div v-if="$slots.actions" class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
      <slot name="actions"></slot>
    </div>
  </div>
</template>
