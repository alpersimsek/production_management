<!--
GDPR Tool File List - File List Container Component

This component provides a container for displaying lists of files in the GDPR compliance tool.
It manages file items with processing status and handles file actions.

Key Features:
- File List Display: Shows a list of files with titles and actions
- Processing Status: Tracks processing status for individual files
- Empty State: Displays placeholder message when no files are present
- Action Handling: Manages file processing, download, and delete actions
- Responsive Grid: Grid layout for file items

Props:
- title: List title (string, required)
- files: Array of file objects (array, required)
- isProcessed: Whether files are processed (boolean, default: false)
- emptyMessage: Message when no files (string, default: 'No files')
- isProcessing: Function to check if file is processing (function, required)
- getProcessingStatus: Function to get processing status (function, required)

Events:
- process: Emitted when file processing is requested (fileId: string)
- download: Emitted when file download is requested (fileId: string)
- delete: Emitted when file deletion is requested (fileId: string)

Features:
- File Items: Renders FileItem components for each file
- Empty State: Shows placeholder when no files are present
- Processing Status: Passes processing status to file items
- Action Propagation: Forwards file actions to parent components
- Grid Layout: Responsive grid layout for file items

The component provides a comprehensive file list interface for file management
in the GDPR compliance tool with proper status tracking and action handling.
-->

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
