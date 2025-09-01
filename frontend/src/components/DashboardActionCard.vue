<!--
GDPR Tool Dashboard Action Card - Dashboard Action Component

This component provides a specialized action card component for the GDPR compliance tool dashboard.
It displays dashboard actions with icons, descriptions, and navigation links.

Key Features:
- Dashboard Actions: Quick access to different sections of the application
- Icon Display: Required icon display for visual identification
- Link Integration: Router-link integration for navigation
- Responsive Design: Mobile-first responsive layout
- Custom Styling: Additional CSS classes support
- Consistent Layout: Standardized card layout for dashboard actions

Props:
- title: Card title (required)
- description: Card description (required)
- icon: Icon component (required)
- linkTo: Router link destination (required)
- linkText: Text for the action link (required)
- customClass: Additional CSS classes (optional)

Features:
- Icon Support: Required icon display with proper sizing
- Navigation Links: Router-link integration for seamless navigation
- Hover Effects: Interactive hover states for better UX
- Responsive Design: Mobile-first responsive layout
- Custom Styling: Additional CSS classes for customization

The component provides a consistent action card interface for dashboard
navigation in the GDPR compliance tool with proper styling and accessibility.
-->

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: Object,
    required: true
  },
  linkTo: {
    type: String,
    required: true
  },
  linkText: {
    type: String,
    required: true
  },
  customClass: {
    type: String,
    default: ''
  }
})
</script>

<template>
  <div class="overflow-hidden rounded-lg bg-white shadow" :class="customClass">
    <div class="p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <component :is="icon" class="h-6 w-6 text-gray-400" aria-hidden="true" />
        </div>
        <div class="ml-3 w-0 flex-1">
          <h3 class="text-base font-semibold text-gray-900">{{ title }}</h3>
          <p class="mt-1 text-sm text-gray-500">{{ description }}</p>
        </div>
      </div>
      <div class="mt-6">
        <router-link
          :to="linkTo"
          class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-primary shadow-sm ring-1 ring-inset ring-primary hover:bg-gray-50"
        >
          {{ linkText }}
        </router-link>
      </div>
    </div>
  </div>
</template>
