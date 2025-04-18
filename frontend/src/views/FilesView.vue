<script setup>
import { ref, onMounted, computed } from 'vue'
import { useFilesStore } from '../stores/files'
import { useFormatters } from '../composables/useFormatters'
import MainLayout from '../components/MainLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import ListView from '../components/ListView.vue'
import FileUploader from '../components/FileUploader.vue'
import ProcessingStatus from '../components/ProcessingStatus.vue'
import {
  DocumentIcon,
  DocumentCheckIcon,
  PlayIcon,
  TrashIcon,
  ArrowDownTrayIcon,
} from '@heroicons/vue/24/outline'

const filesStore = useFilesStore()
const { formatFileSize, formatDate, formatTimeRemaining } = useFormatters()
const uploadError = ref('')

// Computed properties for formatted data
const formattedUploads = computed(() => {
  return filesStore.uploads.map(file => ({
    ...file,
    formattedSize: formatFileSize(file.file_size),
    formattedDate: formatDate(file.create_date)
  }))
})

const formattedProcessed = computed(() => {
  return filesStore.processed.map(file => ({
    ...file,
    formattedSize: formatFileSize(file.file_size),
    formattedDate: formatDate(file.create_date)
  }))
})

// Helper functions
const isProcessing = (fileId) => {
  return !!filesStore.getProcessingStatus(fileId)
}

const getProcessingStatus = (file) => {
  const status = filesStore.getProcessingStatus(file.id)
  if (!status) return null

  const percent = ((status.completedSize / status.totalSize) * 100).toFixed(1)
  const timeRemaining = formatTimeRemaining(status.timeRemaining)

  return {
    percent,
    timeRemaining,
    progressWidth: `${percent}%`
  }
}

// Setup functions
onMounted(async () => {
  await filesStore.fetchFiles()
})

// Event handlers
const handleFileUpload = async (files) => {
  try {
    uploadError.value = ''
    for (const file of files) {
      await filesStore.uploadFile(file)
    }
  } catch (error) {
    console.error('Upload error:', error)
    uploadError.value = error.message || 'Failed to upload file(s). Please try again.'
  }
}

const handleProcess = async (fileId) => {
  try {
    await filesStore.processFile(fileId)
    await filesStore.fetchFiles()
  } catch (error) {
    console.error('Failed to process file:', error)
  }
}

const handleDelete = async (fileId) => {
  try {
    await filesStore.deleteFile(fileId)
    await filesStore.fetchFiles()
  } catch (error) {
    console.error('Failed to delete file:', error)
  }
}

const handleDownload = async (fileId) => {
  try {
    await filesStore.downloadFile(fileId)
  } catch (error) {
    console.error('Failed to download file:', error)
    if (typeof window.alert === 'function') {
      window.alert(`Download failed: ${error.message || 'The file may no longer exist or you may not have permission to access it.'}`)
    }
  }
}
</script>

<template>
  <MainLayout>
    <div class="px-4 sm:px-6 lg:px-8">
      <PageHeader
        title="File Manager"
        description="Upload and manage your files"
      />

      <div class="mt-8">
        <FileUploader
          :upload-progress="filesStore.uploadProgress"
          :error="uploadError"
          @file-upload="handleFileUpload"
        />
      </div>

      <div class="mt-8 space-y-8">
        <!-- Uploads -->
        <ListView
          title="Uploads"
          :items="formattedUploads"
          :empty-message="'No files uploaded yet'"
          :empty-icon="DocumentIcon"
          :get-item-title="item => item.filename"
          :get-item-subtitle="item => item.formattedSize"
          :get-item-metadata="item => item.formattedDate"
          :get-item-icon="() => DocumentIcon"
        >
          <template #itemActions="{ item }">
            <!-- Process button or processing status -->
            <template v-if="!isProcessing(item.id)">
              <button
                @click="handleProcess(item.id)"
                class="text-gray-400 hover:text-indigo-600 transition-colors"
                title="Process file"
              >
                <PlayIcon class="h-5 w-5" />
              </button>
            </template>
            <ProcessingStatus
              v-else
              :percent="getProcessingStatus(item).percent"
              :time-remaining="getProcessingStatus(item).timeRemaining"
              :progress-width="getProcessingStatus(item).progressWidth"
            />

            <!-- Delete button -->
            <button
              @click="handleDelete(item.id)"
              class="text-gray-400 hover:text-red-600 transition-colors"
              title="Delete file"
            >
              <TrashIcon class="h-5 w-5" />
            </button>
          </template>
        </ListView>

        <!-- Processed Files -->
        <ListView
          title="Processed Files"
          :items="formattedProcessed"
          :empty-message="'No processed files yet'"
          :empty-icon="DocumentCheckIcon"
          :get-item-title="item => item.filename"
          :get-item-subtitle="item => item.formattedSize"
          :get-item-metadata="item => item.formattedDate"
          :get-item-icon="() => DocumentCheckIcon"
        >
          <template #itemActions="{ item }">
            <!-- Download button -->
            <button
              @click="handleDownload(item.id)"
              class="text-gray-400 hover:text-indigo-600 transition-colors"
              title="Download file"
            >
              <ArrowDownTrayIcon class="h-5 w-5" />
            </button>

            <!-- Delete button -->
            <button
              @click="handleDelete(item.id)"
              class="text-gray-400 hover:text-red-600 transition-colors"
              title="Delete file"
            >
              <TrashIcon class="h-5 w-5" />
            </button>
          </template>
        </ListView>
      </div>
    </div>
  </MainLayout>
</template>
