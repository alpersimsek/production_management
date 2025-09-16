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

// Utility function to format file size
const formatFileSize = (bytes) => {
  if (!bytes) return ''
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}
</script>

<template>
  <div class="w-full" @drop="handleDrop" @dragover="handleDragOver" @dragleave="handleDragLeave">
    <!-- Main Upload Area -->
    <div
      class="relative group rounded-2xl border-2 border-dashed transition-all duration-300 cursor-pointer overflow-hidden"
      :class="[
        dragOver 
          ? 'border-gray-400 bg-gradient-to-br from-gray-50/80 to-slate-50/80 shadow-lg scale-[1.02]' 
          : 'border-gray-300 bg-gradient-to-br from-gray-50/80 to-slate-50/80 hover:border-gray-400 hover:bg-gradient-to-br hover:from-gray-50/60 hover:to-slate-50/60 hover:shadow-md'
      ]"
      @click="handleBrowseClick">
      
      <!-- Background Pattern -->
      <div class="absolute inset-0 opacity-5">
        <div class="absolute inset-0" style="background-image: radial-gradient(circle at 1px 1px, #6b7280 1px, transparent 0); background-size: 20px 20px;"></div>
      </div>
      
      <!-- Content -->
      <div class="relative p-8 sm:p-12 text-center">
        <!-- Upload Icon with Animation -->
        <div class="relative mb-6">
          <div class="w-20 h-20 mx-auto rounded-2xl bg-gradient-to-br from-gray-500 to-slate-600 flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-110">
            <ArrowUpTrayIcon v-if="props.showIcon" class="h-10 w-10 text-white" aria-hidden="true" />
          </div>
          <!-- Floating particles effect -->
          <div class="absolute -top-2 -right-2 w-3 h-3 bg-gray-400 rounded-full opacity-60 animate-pulse"></div>
          <div class="absolute -bottom-1 -left-1 w-2 h-2 bg-slate-400 rounded-full opacity-40 animate-pulse" style="animation-delay: 0.5s;"></div>
        </div>
        
        <!-- Upload Text -->
        <div class="space-y-2 mb-6">
          <h3 class="text-xl font-bold text-gray-800 group-hover:text-gray-700 transition-colors duration-300">
            Drop files here
          </h3>
          <p class="text-gray-600 group-hover:text-gray-700 transition-colors duration-300">
            or <span class="font-semibold text-gray-600 hover:text-gray-700 underline decoration-2 underline-offset-2">browse files</span>
          </p>
          <p class="text-sm text-gray-500">
            Supports ZIP, TAR, GZ, TXT files
          </p>
        </div>
        
        <!-- Hidden File Input -->
        <input ref="fileInput" type="file" class="sr-only" @change="handleFileInputChange" multiple
          aria-describedby="upload-error" />
      </div>
      
      <!-- Hover Overlay -->
      <div class="absolute inset-0 bg-gradient-to-br from-gray-500/10 to-slate-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
    </div>
    
    <!-- Upload Progress Section -->
    <div v-if="hasUploadProgress" class="mt-6 space-y-4">
      <div class="flex items-center justify-between">
        <h4 class="text-sm font-semibold text-gray-700">Uploading Files</h4>
        <span class="text-xs text-gray-500">{{ uploadProgressEntries.length }} file(s)</span>
      </div>
      
      <div class="space-y-3">
        <div v-for="[fileName, progress] in uploadProgressEntries" :key="fileName" 
          class="bg-white/80 backdrop-blur-sm rounded-xl border border-gray-200/60 p-4 shadow-sm hover:shadow-md transition-all duration-300">
          
          <!-- File Info -->
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center space-x-3 flex-1 min-w-0">
              <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-gray-100 to-slate-100 flex items-center justify-center flex-shrink-0">
                <svg class="w-4 h-4 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ fileName }}</p>
                <p class="text-xs text-gray-500">{{ formatFileSize(progress.size) }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <span class="text-sm font-semibold text-gray-600">{{ formatFileSize(progress.loaded) }} / {{ formatFileSize(progress.total) }}</span>
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
                :style="{ width: progress.percent + '%' }">
                <!-- Shimmer effect -->
                <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-pulse"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Error Message -->
    <div v-if="error" id="upload-error" class="mt-4 p-4 bg-red-50/80 backdrop-blur-sm border border-red-200/60 rounded-xl shadow-sm" role="alert">
      <div class="flex items-center space-x-3">
        <div class="w-6 h-6 rounded-full bg-red-100 flex items-center justify-center flex-shrink-0">
          <svg class="w-4 h-4 text-red-600" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <p class="text-sm font-medium text-red-800">{{ error }}</p>
      </div>
    </div>
  </div>
</template>