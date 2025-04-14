<template>
  <li
    class="group relative flex items-center space-x-3 rounded-lg border border-gray-300 bg-white px-5 py-4 shadow-sm"
    :class="{ 'hover:border-gray-400': !isPlaceholder, 'hover:border-indigo-400': isProcessed && !isPlaceholder }"
  >
    <div class="flex-shrink-0">
      <component
        :is="isProcessed ? DocumentCheckIcon : DocumentIcon"
        class="h-6 w-6"
        :class="isPlaceholder ? 'text-gray-300' : 'text-gray-400'"
        aria-hidden="true"
      />
    </div>
    <div class="min-w-0 flex-1">
      <p v-if="isPlaceholder" class="text-sm text-gray-500 italic">{{ placeholder }}</p>
      <template v-else>
        <p class="text-sm font-medium text-gray-900 truncate">
          {{ file.filename }}
        </p>
        <div class="flex text-sm text-gray-500 gap-2">
          <p class="truncate">{{ file.formattedSize }}</p>
          <span>&middot;</span>
          <p>{{ file.formattedDate }}</p>
        </div>
      </template>
    </div>

    <!-- Actions for real files (not placeholders) -->
    <div v-if="!isPlaceholder" class="flex gap-2">
      <!-- Processing action or status -->
      <template v-if="!isProcessed">
        <button
          v-if="!isProcessing"
          @click="$emit('process', file.id)"
          class="text-gray-400 hover:text-indigo-600 transition-colors"
          title="Process file"
        >
          <PlayIcon class="h-5 w-5" />
        </button>
        <ProcessingStatus
          v-else
          :percent="status.percent"
          :time-remaining="status.timeRemaining"
          :progress-width="status.progressWidth"
        />
      </template>

      <!-- Download action (processed files only) -->
      <button
        v-if="isProcessed"
        @click="$emit('download', file.id)"
        class="text-gray-400 hover:text-indigo-600 transition-colors"
        title="Download file"
      >
        <ArrowDownTrayIcon class="h-5 w-5" />
      </button>

      <!-- Delete action (all files) -->
      <button
        @click="$emit('delete', file.id)"
        class="text-gray-400 hover:text-red-600 transition-colors"
        title="Delete file"
      >
        <TrashIcon class="h-5 w-5" />
      </button>
    </div>
  </li>
</template>

<script setup>
import { computed } from 'vue'
import {
  DocumentIcon,
  DocumentCheckIcon,
  PlayIcon,
  TrashIcon,
  ArrowDownTrayIcon
} from '@heroicons/vue/24/outline'
import ProcessingStatus from './ProcessingStatus.vue'

const props = defineProps({
  file: {
    type: Object,
    default: null
  },
  isProcessed: {
    type: Boolean,
    default: false
  },
  isProcessing: {
    type: Boolean,
    default: false
  },
  status: {
    type: Object,
    default: null
  },
  placeholder: {
    type: String,
    default: 'No files'
  }
})

defineEmits(['process', 'download', 'delete'])

const isPlaceholder = computed(() => !props.file)
</script>
