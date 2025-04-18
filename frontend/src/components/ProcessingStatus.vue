<template>
  <div class="flex items-center gap-2">
    <div class="flex flex-col gap-1 min-w-[150px]">
      <div class="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
        <div
          class="h-full bg-indigo-600 transition-all duration-200"
          :style="{
            width: progressWidth
          }"
        ></div>
      </div>
      <div class="flex items-center justify-between text-xs text-gray-500">
        <div class="flex items-center">
          <ClockIcon class="h-3 w-3 mr-1" />
          {{ timeRemaining }}
        </div>
        <div>
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
