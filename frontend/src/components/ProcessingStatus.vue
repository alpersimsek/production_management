<template>
  <div class="flex items-center gap-2 z-0">
    <div class="flex flex-col gap-1 w-20 sm:w-24">
      <div class="h-2 bg-gray-200 rounded-full overflow-hidden">
        <div class="h-full bg-indigo-600 transition-all duration-200" :style="{ width: progressWidth }"></div>
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