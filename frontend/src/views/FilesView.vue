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
    <div class="min-h-screen bg-gray-50 px-4 sm:px-6 lg:px-8 py-1 sm:py-1">

      <!-- Header -->
      <div class="sm:flex sm:items-center mb-8">
        <div class="sm:flex-auto">
          <div class="flex items-center gap-3">
            <h1 class="text-2xl font-bold text-gray-900 tracking-tight">File Manager</h1>
          </div>
          <p class="mt-2 text-sm text-gray-600 font-medium">
            Upload, process, and manage your files with ease
          </p>
        </div>
      </div>

      <!-- File Lists -->
      <div v-if="isLoading" class="py-8 flex justify-center items-center" aria-live="polite">
        <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600"></div>
        <p class="ml-4 text-sm font-medium text-gray-600">Loading files...</p>
      </div>
      <div v-else class="space-y-8">
        <!-- File Uploader and Uploads Section -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 sm:mb-8">
          <!-- File Uploader -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6 animate-fade-in">
            <FileUploader :upload-progress="filesStore.uploadProgress" :error="uploadError" :show-icon="true"
              @file-upload="handleFileUpload" class="w-full max-w-md" />
            <p v-if="uploadError" class="mt-2 text-sm text-red-500 text-center bg-red-50 p-2 rounded-md animate-fade-in"
              role="alert">
              {{ uploadError }}
            </p>
          </div>
          <!-- Uploads List -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6 animate-fade-in">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Uploads</h2>
            <ListView title="" :items="formattedUploads" :empty-message="'No files uploaded yet'"
              :empty-icon="DocumentIcon" :get-item-title="item => item.filename"
              :get-item-subtitle="item => item.formattedSize" :get-item-metadata="item => item.formattedDate"
              :get-item-icon="() => DocumentIcon">
              <template #itemActions="{ item }">
                <div class="flex items-center gap-2">
                  <template v-if="!isProcessing(item.id)">
                    <button @click="handleProcess(item.id)"
                      class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                      title="Process file" aria-label="Process file">
                      <PlayIcon class="h-5 w-5" aria-hidden="true" />
                    </button>
                  </template>
                  <ProcessingStatus v-else :percent="getProcessingStatus(item).percent"
                    :time-remaining="getProcessingStatus(item).timeRemaining"
                    :progress-width="getProcessingStatus(item).progressWidth" class="h-5 w-20 sm:w-24 flex items-center"
                    aria-live="polite" />
                  <button @click="handleDelete(item.id)"
                    class="inline-flex items-center justify-center rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                    title="Delete file" aria-label="Delete file">
                    <TrashIcon class="h-5 w-5 text-gray-400 hover:text-red-600" aria-hidden="true" />
                  </button>
                </div>
              </template>
            </ListView>
          </div>
        </div>

        <!-- Processed Files -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6 animate-fade-in">
          <ListView title="Processed Files" :items="formattedProcessed" :empty-message="'No processed files yet'"
            :empty-icon="DocumentCheckIcon" :get-item-title="item => item.filename"
            :get-item-subtitle="item => item.formattedSize" :get-item-metadata="item => item.formattedDate"
            :get-item-icon="() => DocumentCheckIcon">
            <template #itemActions="{ item }">
              <div class="flex items-center gap-2">
                <button @click="handleDownload(item.id)"
                  class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                  title="Download file" aria-label="Download file">
                  <ArrowDownTrayIcon class="h-5 w-5" aria-hidden="true" />
                </button>
                <button @click="handleDelete(item.id)"
                  class="inline-flex items-center justify-center rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                  title="Delete file" aria-label="Delete file">
                  <TrashIcon class="h-5 w-5 text-gray-400 hover:text-red-600" aria-hidden="true" />
                </button>
              </div>
            </template>
          </ListView>
        </div>
      </div>

      <!-- Delete Confirmation Dialog -->
      <ConfirmDeleteDialog v-if="showDeleteModal" :open="showDeleteModal" item-type="file"
        @close="showDeleteModal = false" @confirm="confirmDelete" />

      <!-- Footer Branding -->
      <footer class="mt-12 text-center text-sm text-gray-500 px-4 sm:px-16">
        © {{ new Date().getFullYear() }} GDPR Processor. All rights reserved.
        <a href="/privacy" class="text-indigo-600 hover:text-indigo-700 ml-2 transition-colors duration-200">Privacy
          Policy</a>
      </footer>
    </div>
  </MainLayout>
</template>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.3s ease-out;
}

/* Dialog transition */
.dialog-enter-active,
.dialog-leave-active {
  transition: all 0.3s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>