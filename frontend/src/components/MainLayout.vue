<!--
GDPR Tool Main Layout - Application Layout Component

This component provides the main layout structure for the GDPR compliance tool application.
It includes the navigation bar and main content area with responsive design and styling.

Key Features:
- Navigation Integration: Includes the main navigation bar component
- Responsive Design: Mobile-first responsive layout with proper spacing
- Content Container: Provides consistent content width and padding
- Background Styling: Gradient background with smooth transitions
- Slot Support: Allows child components to be inserted into the main content area

Layout Structure:
- Header: Navigation bar with shadow styling
- Main Content: Centered content area with responsive padding
- Background: Gradient background from gray-50 to gray-100
- Container: Max-width container with responsive padding

The component serves as the base layout for all authenticated pages in the
GDPR compliance tool, providing consistent styling and structure.
-->

<script setup>
import AppNavbar from './NavBar.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <AppNavbar />
    <div class="py-8 sm:py-12">
      <main>
        <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <slot></slot>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
</style>