<template>
  <div>
    <h2 class="text-lg font-medium text-gray-900">{{ title }}</h2>
    <ul role="list" class="mt-4 grid grid-cols-1 gap-4">
      <FileItem
        v-if="files.length === 0"
        :placeholder="emptyMessage"
      />
      <FileItem
        v-for="file in files"
        :key="file.id"
        :file="file"
        :is-processed="isProcessed"
        :is-processing="isProcessing(file.id)"
        :status="getProcessingStatus(file)"
        @process="$emit('process', $event)"
        @download="$emit('download', $event)"
        @delete="$emit('delete', $event)"
      />
    </ul>
  </div>
</template>

<script setup>
import FileItem from './FileItem.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  files: {
    type: Array,
    required: true
  },
  isProcessed: {
    type: Boolean,
    default: false
  },
  emptyMessage: {
    type: String,
    default: 'No files'
  },
  isProcessing: {
    type: Function,
    required: true
  },
  getProcessingStatus: {
    type: Function,
    required: true
  }
})

defineEmits(['process', 'download', 'delete'])
</script>
