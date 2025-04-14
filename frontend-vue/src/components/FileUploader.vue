<template>
  <div
    class="mx-auto max-w-3xl"
    @drop="handleDrop"
    @dragover="handleDragOver"
    @dragleave="handleDragLeave"
  >
    <div
      class="flex justify-center rounded-lg border border-dashed border-gray-900/25 px-6 py-10 cursor-pointer"
      :class="dropzoneClasses"
      @click="handleBrowseClick"
    >
      <div class="text-center">
        <DocumentIcon class="mx-auto h-12 w-12 text-gray-300" aria-hidden="true" />
        <div class="mt-4 flex text-sm leading-6 text-gray-600">
          <span class="font-semibold text-primary">Upload a file</span>
          <input
            ref="fileInput"
            type="file"
            class="sr-only"
            @change="handleFileInputChange"
            multiple
          />
          <p class="pl-1">or drag and drop</p>
        </div>
        <p class="text-xs leading-5 text-gray-600">Supported files: ZIP, TAR, GZ, TXT</p>
        <template v-if="hasUploadProgress">
          <div
            v-for="[fileName, progress] in uploadProgressEntries"
            :key="fileName"
            class="mt-4"
          >
            <div class="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span class="truncate">{{ fileName }}</span>
              <span>{{ progress.percent }}%</span>
            </div>
            <div class="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
              <div
                class="h-full bg-indigo-600 transition-all duration-200"
                :style="{ width: progress.percent + '%' }"
              ></div>
            </div>
          </div>
        </template>
        <p v-if="error" class="mt-2 text-sm text-red-600">
          {{ error }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { DocumentIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  uploadProgress: {
    type: Map,
    default: () => new Map()
  },
  error: {
    type: String,
    default: ''
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
