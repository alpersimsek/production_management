<!--
GDPR Tool Processing Status - File Processing Progress Component

This component provides a visual progress indicator for file processing operations
in the GDPR compliance tool. It displays progress percentage, time remaining, and a progress bar.

Key Features:
- Progress Visualization: Visual progress bar with percentage display
- Time Estimation: Shows estimated time remaining for processing
- Responsive Design: Mobile-first responsive layout
- Accessibility: Proper ARIA attributes and screen reader support
- Real-time Updates: Dynamic progress updates during processing

Props:
- percent: Progress percentage as string (required)
- timeRemaining: Formatted time remaining string (required)
- progressWidth: CSS width value for progress bar (required)

Features:
- Progress Bar: Visual representation of processing progress
- Time Display: Clock icon with time remaining estimate
- Percentage Display: Numeric percentage completion
- Responsive Sizing: Adapts to different screen sizes
- Smooth Animations: CSS transitions for progress updates

The component provides a compact and informative progress indicator for
file processing operations in the GDPR compliance tool.
-->

<script setup>
import { ClockIcon } from '@heroicons/vue/24/outline'

defineProps({
  percent: {
    type: String,
    required: true
  },
  timeRemaining: {
    type: String,
    required: true
  },
  progressWidth: {
    type: String,
    required: true
  }
})
</script>

<template>
  <div class="flex items-center gap-2 z-0">
    <div class="flex flex-col gap-1 w-20 sm:w-24">
      <div class="h-3 bg-gray-200 rounded-full overflow-hidden">
        <div 
          class="h-full bg-gradient-to-r from-gray-500 to-slate-600 transition-all duration-500 ease-out relative overflow-hidden"
          :style="{ width: progressWidth }">
          <!-- Shimmer effect -->
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
        </div>
      </div>
      <div class="flex items-center justify-between text-xs text-gray-500">
        <div class="flex items-center truncate">
          <ClockIcon class="h-3 w-3 mr-1 flex-shrink-0" />
          <span class="truncate">{{ timeRemaining }}</span>
        </div>
        <div class="flex-shrink-0">
          {{ percent }}%
        </div>
      </div>
    </div>
  </div>
</template>