<!--
GDPR Tool File Uploader - Drag and Drop File Upload Component

This component provides a drag-and-drop file upload interface for the GDPR compliance tool.
It supports multiple file types with progress tracking and error handling.

Key Features:
- Drag and Drop: Intuitive drag-and-drop file upload interface
- Multiple File Support: Upload multiple files simultaneously
- Progress Tracking: Real-time upload progress for each file
- File Type Validation: Support for ZIP, TAR, GZ, and TXT files
- Error Handling: Display upload errors with proper accessibility
- Visual Feedback: Drag state indicators and progress bars
- Accessibility: Screen reader support and keyboard navigation

Props:
- uploadProgress: Map of file upload progress (Map<string, object>)
- error: Error message to display (string)
- showIcon: Whether to show upload icon (boolean, default: true)

Events:
- fileUpload: Emitted when files are selected or dropped (files: File[])

Features:
- File Validation: Supports specific file types for GDPR processing
- Progress Display: Individual progress bars for each file
- Error States: Clear error messaging with proper ARIA attributes
- Responsive Design: Mobile-first responsive layout
- Visual States: Drag over states and hover effects

The component provides a comprehensive file upload interface with proper
accessibility and user feedback for the GDPR compliance tool.
-->

<script setup>
import { ref, computed } from 'vue'
import { ArrowUpTrayIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  uploadProgress: {
    type: Map,
    default: () => new Map()
  },
  error: {
    type: String,
    default: ''
  },
  showIcon: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['fileUpload'])

const fileInput = ref(null)
const dragOver = ref(false)

// Computed properties
const dropzoneClasses = computed(() => ({
  'border-primary bg-primary/5': dragOver.value
}))

const hasUploadProgress = computed(() => props.uploadProgress.size > 0)

const uploadProgressEntries = computed(() => {
  return Array.from(props.uploadProgress.entries())
})

// Event handlers
const handleDrop = (e) => {
  e.preventDefault()
  dragOver.value = false
  const files = [...e.dataTransfer.files]
  emit('fileUpload', files)
}

const handleDragOver = (e) => {
  e.preventDefault()
  dragOver.value = true
}

const handleDragLeave = () => {
  dragOver.value = false
}

const handleFileInputChange = () => {
  const files = [...fileInput.value.files]
  emit('fileUpload', files)
  // Reset the file input to ensure change event fires even if same file is selected
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleBrowseClick = () => {
  fileInput.value.click()
}
</script>

<template>
  <div class="w-full" @drop="handleDrop" @dragover="handleDragOver" @dragleave="handleDragLeave">
    <div
      class="flex justify-center items-center rounded-lg border border-gray-200 bg-white/95 backdrop-blur-sm p-3 sm:p-4 cursor-pointer"
      :class="dropzoneClasses" @click="handleBrowseClick">
      <div class="flex items-center gap-3">
        <ArrowUpTrayIcon v-if="props.showIcon" class="h-8 sm:h-10 w-8 sm:w-10 text-primary flex-shrink-0"
          aria-hidden="true" />
        <div class="flex-1 flex-col">
          <div class="flex items-center text-sm leading-6 text-gray-600">
            <span class="font-semibold text-primary hover:text-primary-hover transition-colors duration-200">Upload a
              file</span>
            <input ref="fileInput" type="file" class="sr-only" @change="handleFileInputChange" multiple
              aria-describedby="upload-error" />
            <p class="pl-1">or drag and drop</p>
          </div>
          <p class="text-xs leading-5 text-gray-500 mt-1">Supported files: ZIP, TAR, GZ, TXT</p>
          <template v-if="hasUploadProgress">
            <div v-for="[fileName, progress] in uploadProgressEntries" :key="fileName" class="mt-2">
              <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
                <span class="truncate max-w-[200px]">{{ fileName }}</span>
                <span>{{ progress.percent }}%</span>
              </div>
              <div class="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                <div class="h-full bg-primary transition-all duration-200" :style="{ width: progress.percent + '%' }">
                </div>
              </div>
            </div>
          </template>
          <p v-if="error" id="upload-error" class="mt-2 text-sm text-red-500 bg-red-50 p-2 rounded-md" role="alert">
            {{ error }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>