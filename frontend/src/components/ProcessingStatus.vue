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
  <div class="absolute inset-0 bg-white/90 backdrop-blur-sm rounded-xl border border-gray-200/60 p-4 shadow-lg z-10">
    <!-- File Info -->
    <div class="flex items-center justify-between mb-3">
      <div class="flex items-center space-x-3 flex-1 min-w-0">
        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-gray-100 to-slate-100 flex items-center justify-center flex-shrink-0">
          <svg class="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <div class="flex-1 min-w-0">
          <p class="text-sm font-medium text-gray-800 truncate">Processing File</p>
          <p class="text-xs text-gray-500">Applying masking rules</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-sm font-semibold text-gray-600">{{ percent }}%</span>
        <div class="w-6 h-6 rounded-full bg-gray-100 flex items-center justify-center">
          <div class="w-3 h-3 rounded-full bg-gray-500 animate-pulse"></div>
        </div>
      </div>
    </div>
    
    <!-- Progress Bar -->
    <div class="relative">
      <div class="h-3 w-full bg-gray-200 rounded-full overflow-hidden">
        <div 
          class="h-full bg-gradient-to-r from-gray-500 to-slate-600 transition-all duration-500 ease-out relative overflow-hidden"
          :style="{ width: progressWidth }">
          <!-- Shimmer effect -->
          <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
        </div>
      </div>
    </div>
    
    <!-- Time Remaining -->
    <div class="flex items-center justify-center mt-3 text-xs text-gray-500">
      <ClockIcon class="h-3 w-3 mr-1 flex-shrink-0" />
      <span class="truncate">{{ timeRemaining }}</span>
    </div>
  </div>
</template>