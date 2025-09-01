<!--
GDPR Tool Dashboard Header - Welcome Header Component

This component provides a personalized welcome header for the GDPR compliance tool dashboard.
It displays a greeting message with the user's capitalized username.

Key Features:
- Personalized Greeting: Welcome message with user's name
- Username Capitalization: Automatically capitalizes the first letter of username
- Clean Design: Simple, clean header design
- Responsive Layout: Mobile-first responsive design

Props:
- username: Username to display in the greeting (string, required)

Features:
- Username Formatting: Capitalizes the first letter of the username
- Welcome Message: Personalized greeting for the user
- Clean Typography: Clear, readable text styling
- Responsive Design: Adapts to different screen sizes

The component provides a welcoming header interface for the dashboard
in the GDPR compliance tool with proper username formatting.
-->

<script setup>
import { computed } from 'vue'

const props = defineProps({
  username: {
    type: String,
    required: true
  }
})

const capitalizedUsername = computed(() => {
  if (!props.username) return ''
  return props.username.charAt(0).toUpperCase() + props.username.slice(1)
})
</script>

<template>
  <div class="mb-8">
    <h1 class="text-2xl font-semibold text-gray-900">
      Welcome back, {{ capitalizedUsername }}
    </h1>
  </div>
</template>
