<!--
GDPR Tool Action Card - Navigation Action Component

This component provides a reusable action card component for the GDPR compliance tool.
It displays navigation actions with icons, descriptions, and links to other pages.

Key Features:
- Navigation Actions: Quick access to different sections of the application
- Icon Support: Optional icon display with slot support
- Link Integration: Router-link integration for navigation
- Flexible Content: Slot-based content system for customization
- Responsive Design: Mobile-first responsive layout
- Custom Styling: Additional CSS classes support

Props:
- title: Card title (required)
- description: Optional description text
- icon: Optional icon component (Heroicons compatible)
- linkTo: Router link destination
- linkText: Text for the action link (default: 'View')
- customClass: Additional CSS classes

Slots:
- icon: Custom icon slot
- description: Custom description slot
- actions: Custom actions slot (overrides default link)

The component provides a consistent action card interface for navigation
and quick access to different sections of the GDPR compliance tool.
-->

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
  icon: {
    type: [Object, Function, null], // Allow Object, Function, or null for Heroicons
    default: null,
  },
  linkTo: {
    type: String,
    default: '',
  },
  linkText: {
    type: String,
    default: 'View',
  },
  customClass: {
    type: String,
    default: '',
  },
})
</script>

<template>
  <div class="overflow-hidden rounded-lg bg-white shadow" :class="customClass">
    <div class="p-6">
      <div class="flex items-center">
        <div v-if="$slots.icon || icon" class="flex-shrink-0">
          <slot name="icon">
            <component :is="icon" class="h-8 sm:h-10 w-8 sm:w-10 text-indigo-600 flex-shrink-0" aria-hidden="true" />
          </slot>
        </div>
        <div :class="{ 'ml-3': $slots.icon || icon }" class="w-0 flex-1">
          <h3 class="text-base font-semibold text-gray-900">{{ title }}</h3>
          <p v-if="description" class="mt-1 text-sm text-gray-500">{{ description }}</p>
          <slot name="description"></slot>
        </div>
      </div>
      <div class="mt-6">
        <slot name="actions">
          <router-link v-if="linkTo" :to="linkTo"
            class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-primary shadow-sm ring-1 ring-inset ring-primary hover:bg-gray-50">
            {{ linkText }}
          </router-link>
        </slot>
      </div>
    </div>
  </div>
</template>
