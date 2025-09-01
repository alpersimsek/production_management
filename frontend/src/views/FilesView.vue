<script setup>
import { ref, onMounted, computed } from 'vue'
import { useFilesStore } from '../stores/files'
import { useAuthStore } from '../stores/auth'
import { useFormatters } from '../composables/useFormatters'
import MainLayout from '../components/MainLayout.vue'
import ListView from '../components/ListView.vue'
import FileUploader from '../components/FileUploader.vue'
import ProcessingStatus from '../components/ProcessingStatus.vue'
import ConfirmDeleteDialog from '../components/ConfirmDeleteDialog.vue'
import ProductSelectionForm from '../components/ProductSelectionForm.vue'
import {
  DocumentIcon,
  DocumentCheckIcon,
  PlayIcon,
  TrashIcon,
  ArrowDownTrayIcon,
} from '@heroicons/vue/24/outline'

const filesStore = useFilesStore()
const authStore = useAuthStore()
const { formatFileSize, formatDate, formatTimeRemaining } = useFormatters()
const uploadError = ref('')
const showDeleteModal = ref(false)
const deleteFileId = ref(false)
const isLoading = ref(false)
const showDeleteAllModal = ref(false)
const showProductModal = ref(false)
const selectedFileForProcessing = ref(null)

// Pagination state for Processed Files
const currentPage = ref(1)
const itemsPerPage = 5

// Pagination state for Uploads
const currentUploadPage = ref(1)

// Computed property to check if user is admin
const isAdmin = computed(() => authStore.user?.role === 'admin')

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

// Paginated uploads
const paginatedUploads = computed(() => {
  const start = (currentUploadPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return formattedUploads.value.slice(start, end)
})

// Total pages for uploads pagination
const totalUploadPages = computed(() => Math.ceil(formattedUploads.value.length / itemsPerPage))

// Pagination navigation methods for uploads
const goToUploadPage = (page) => {
  if (page >= 1 && page <= totalUploadPages.value) {
    currentUploadPage.value = page
  }
}

const prevUploadPage = () => {
  if (currentUploadPage.value > 1) {
    currentUploadPage.value--
  }
}

const nextUploadPage = () => {
  if (currentUploadPage.value < totalUploadPages.value) {
    currentUploadPage.value++
  }
}

// Paginated processed files
const paginatedProcessed = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return formattedProcessed.value.slice(start, end)
})

// Total pages for processed files pagination
const totalPages = computed(() => Math.ceil(formattedProcessed.value.length / itemsPerPage))

// Pagination navigation methods for processed files
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

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
  isLoading.value = true
  try {
    await filesStore.fetchFiles()
  } finally {
    isLoading.value = false
  }
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
    const file = filesStore.uploads.find(f => f.id === fileId)
    if (file) {
      selectedFileForProcessing.value = file
      showProductModal.value = true
    }
  } catch (error) {
    console.error('Failed to open product selection:', error)
    uploadError.value = `Failed to open product selection: ${error.message || 'Unknown error'}`
  }
}

const handleProductProcess = async (processOptions) => {
  try {
    uploadError.value = ''
    // Send product ID to backend for product-based processing
    await filesStore.processFileWithProduct(selectedFileForProcessing.value.id, processOptions.productId)
    await filesStore.fetchFiles()
    showProductModal.value = false
    selectedFileForProcessing.value = null
  } catch (error) {
    console.error('Failed to process file:', error)
    uploadError.value = `Failed to process file: ${error.message || 'Unknown error'}`
  }
}

const handleProductModalClose = () => {
  showProductModal.value = false
  selectedFileForProcessing.value = null
}

const handleDelete = (fileId) => {
  deleteFileId.value = fileId
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  try {
    uploadError.value = ''
    await filesStore.deleteFile(deleteFileId.value)
    await filesStore.fetchFiles()
  } catch (error) {
    console.error('Failed to delete file:', error)
    uploadError.value = `Failed to delete file: ${error.message || 'Unknown error'}`
  } finally {
    showDeleteModal.value = false
    deleteFileId.value = null
  }
}

const handleDeleteAll = () => {
  showDeleteAllModal.value = true
}

const confirmDeleteAll = async () => {
  try {
    uploadError.value = ''
    await filesStore.deleteAllFiles()
    await filesStore.fetchFiles()
  } catch (error) {
    console.error('Failed to delete all files:', error)
    uploadError.value = `Failed to delete all files: ${error.message || 'Unknown error'}`
  } finally {
    showDeleteAllModal.value = false
  }
}

const handleDownload = async (fileId) => {
  try {
    uploadError.value = ''
    await filesStore.downloadFile(fileId)
  } catch (error) {
    console.error('Failed to download file:', error)
    uploadError.value = `Download failed: ${error.message || 'The file may no longer exist or you may not have permission to access it.'}`
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
        <!-- Add Delete All Button for Admins -->
        <div v-if="isAdmin" class="mt-4 sm:mt-0 sm:ml-4">
          <button
            @click="handleDeleteAll"
            class="inline-flex items-center justify-center rounded-lg bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200"
            title="Delete all files"
            aria-label="Delete all files"
          >
            <TrashIcon class="h-5 w-5 mr-2" aria-hidden="true" />
            Delete All Files
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="py-8 flex justify-center items-center" aria-live="polite">
        <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600"></div>
        <p class="ml-4 text-sm font-medium text-gray-600">Loading files...</p>
      </div>

      <!-- Error State -->
      <div v-if="uploadError && !isLoading"
        class="mt-6 rounded-xl bg-red-50 p-4 shadow-sm animate-fade-in flex items-center justify-between" role="alert">
        <div class="flex items-center">
          <svg class="h-5 w-5 text-red-400 mr-2" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clip-rule="evenodd" />
          </svg>
          <span class="text-sm font-medium text-red-800">{{ uploadError }}</span>
        </div>
        <div class="ml-auto pl-3">
          <div class="-mx-1.5 -my-1.5">
            <button type="button" @click="uploadError = ''"
              class="inline-flex rounded-md bg-red-50 p-1.5 text-red-500 hover:bg-red-100 hover:text-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors duration-200"
              aria-label="Dismiss error">
              <TrashIcon class="h-5 w-5" aria-hidden="true" />
            </button>
          </div>
        </div>
      </div>

      <!-- File Lists -->
      <div v-if="!isLoading" class="space-y-8">
        <!-- File Uploader and Uploads Section -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 sm:mb-8">
          <!-- File Uploader -->
          <div
            class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6 animate-fade-in flex items-center justify-center hover:shadow-md hover:scale-105 transition-all duration-200">
            <div class="w-full max-w-md">
              <FileUploader :upload-progress="filesStore.uploadProgress" :error="uploadError" :show-icon="true"
                @file-upload="handleFileUpload" class="w-full" />
              <p v-if="uploadError"
                class="mt-2 text-sm text-red-500 text-center bg-red-50 p-2 rounded-md animate-fade-in" role="alert">
                {{ uploadError }}
              </p>
            </div>
          </div>
          <!-- Uploads List -->
          <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6 animate-fade-in">
            <h2 class="text-lg font-semibold text-gray-900 mb-4">Uploads</h2>
            <ListView title="" :items="paginatedUploads" empty-message="No files uploaded yet"
              :get-item-title="item => item.filename" :get-item-subtitle="item => item.formattedSize"
              :get-item-metadata="item => item.formattedDate" :get-item-icon="() => DocumentIcon">
              <template #empty>
                <div class="text-center py-4">
                  <DocumentIcon class="mx-auto h-12 w-12 text-gray-300" aria-hidden="true" />
                  <p class="mt-2 text-sm text-gray-500 italic">No files uploaded yet</p>
                </div>
              </template>
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
                    <TrashIcon class="h-5 w-5 text-gray-600 hover:text-red-600" aria-hidden="true" />
                  </button>
                </div>
              </template>
            </ListView>
            <!-- Pagination Controls for Uploads -->
            <div v-if="totalUploadPages > 1" class="mt-4 flex justify-center items-center gap-2" role="navigation" aria-label="Uploads pagination">
              <button
                @click="prevUploadPage"
                :disabled="currentUploadPage === 1"
                class="inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-700 bg-white border border-gray-200 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Previous page"
              >
                Previous
              </button>
              <button
                v-for="page in totalUploadPages"
                :key="page"
                @click="goToUploadPage(page)"
                :class="[
                  'inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold',
                  currentUploadPage === page
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'bg-white text-gray-700 border border-gray-200 shadow-sm hover:bg-gray-50'
                ]"
                :aria-current="currentUploadPage === page ? 'page' : undefined"
                :aria-label="`Go to page ${page}`"
              >
                {{ page }}
              </button>
              <button
                @click="nextUploadPage"
                :disabled="currentUploadPage === totalUploadPages"
                class="inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-700 bg-white border border-gray-200 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Next page"
              >
                Next
              </button>
            </div>
          </div>
        </div>

        <!-- Processed Files -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6 animate-fade-in">
          <ListView title="Processed Files" :items="paginatedProcessed" empty-message="No processed files yet"
            :get-item-title="item => item.filename" :get-item-subtitle="item => item.formattedSize"
            :get-item-metadata="item => item.formattedDate" :get-item-icon="() => DocumentCheckIcon">
            <template #empty>
              <div class="text-center py-4">
                <DocumentCheckIcon class="mx-auto h-12 w-12 text-gray-300" aria-hidden="true" />
                <p class="mt-2 text-sm text-gray-500 italic">No processed files yet</p>
              </div>
            </template>
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
                  <TrashIcon class="h-5 w-5 text-gray-600 hover:text-red-600" aria-hidden="true" />
                </button>
              </div>
            </template>
          </ListView>
          <!-- Pagination Controls for Processed Files -->
          <div v-if="totalPages > 1" class="mt-4 flex justify-center items-center gap-2" role="navigation" aria-label="Processed files pagination">
            <button
              @click="prevPage"
              :disabled="currentPage === 1"
              class="inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-700 bg-white border border-gray-200 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Previous page"
            >
              Previous
            </button>
            <button
              v-for="page in totalPages"
              :key="page"
              @click="goToPage(page)"
              :class="[
                'inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold',
                currentPage === page
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : 'bg-white text-gray-700 border border-gray-200 shadow-sm hover:bg-gray-50'
              ]"
              :aria-current="currentPage === page ? 'page' : undefined"
              :aria-label="`Go to page ${page}`"
            >
              {{ page }}
            </button>
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-700 bg-white border border-gray-200 shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Next page"
            >
              Next
            </button>
          </div>
        </div>
      </div>

      <!-- Delete Confirmation Dialog -->
      <ConfirmDeleteDialog v-if="showDeleteModal" :open="showDeleteModal" item-type="file"
        @close="showDeleteModal = false" @confirm="confirmDelete" />

      <!-- Delete All Confirmation Dialog -->
      <ConfirmDeleteDialog v-if="showDeleteAllModal" :open="showDeleteAllModal" item-type="all files"
        @close="showDeleteAllModal = false" @confirm="confirmDeleteAll" />

      <!-- Product Selection Modal -->
      <ProductSelectionForm
        :is-open="showProductModal"
        :file="selectedFileForProcessing"
        @close="handleProductModalClose"
        @process="handleProductProcess"
      />

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
</style>