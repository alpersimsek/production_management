<!--
GDPR Tool Files View - File Management Interface

This component provides the file management interface for the GDPR compliance tool.
It allows users to upload, process, and manage files with product-based processing workflow.

Key Features:
- File Upload: Drag-and-drop file upload with progress tracking
- Product-Based Processing: Select products before processing files
- File Management: View, download, and delete uploaded and processed files
- Processing Status: Real-time processing progress with time estimates
- Pagination: Efficient handling of large file lists
- Admin Features: Bulk delete operations for administrators
- Error Handling: Comprehensive error states and user feedback

File Management Features:
- Upload Files: Support for multiple file types with validation
- Process Files: Product selection modal for targeted processing
- Download Files: Download processed files with proper error handling
- Delete Files: Individual and bulk file deletion with confirmation
- File Status: Real-time processing status and progress tracking

Processing Workflow:
- Product Selection: Choose product before processing for targeted rules
- Progress Tracking: Real-time progress updates with time estimates
- Status Management: Handle processing states and error conditions
- File Organization: Separate views for uploaded and processed files

The component provides comprehensive file management functionality for
GDPR compliance tool users with proper workflow and error handling.
-->

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useFilesStore } from '../stores/files'
import { useAuthStore } from '../stores/auth'
import { useFormatters } from '../composables/useFormatters'
import { useErrorHandler } from '../composables/useErrorHandler'
import { useNotifications } from '../composables/useNotifications'
import ApiService from '../services/api'
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
  DocumentArrowUpIcon,
} from '@heroicons/vue/24/outline'

const filesStore = useFilesStore()
const authStore = useAuthStore()
const { formatFileSize, formatDate, formatTimeRemaining } = useFormatters()
const { handleError } = useErrorHandler()
const { showFileUploaded, showFileDeleted, showFileProcessingStarted, showFileProcessingComplete, showFileProcessingError } = useNotifications()
const showDeleteModal = ref(false)
const deleteFileId = ref(false)
const isLoading = ref(false)
const showDeleteAllModal = ref(false)
const showProductModal = ref(false)
const selectedFileForProcessing = ref(null)

// Pagination state for Processed Files
const currentPage = ref(1)
const itemsPerPage = 3

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
    for (const file of files) {
      await filesStore.uploadFile(file)
      showFileUploaded(file.name)
    }
  } catch (error) {
    console.error('Upload error:', error)
    handleError(error, { type: 'file' })
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
    handleError(error, { type: 'file' })
  }
}

const handleProductProcess = async (processOptions) => {
  try {
    const fileName = selectedFileForProcessing.value.filename
    showFileProcessingStarted(fileName)
    
    // Send product ID to backend for product-based processing
    await filesStore.processFileWithProduct(selectedFileForProcessing.value.id, processOptions.productId)
    await filesStore.fetchFiles()
    
    showFileProcessingComplete(fileName)
    showProductModal.value = false
    selectedFileForProcessing.value = null
  } catch (error) {
    console.error('Failed to process file:', error)
    showFileProcessingError(selectedFileForProcessing.value.filename, error.message)
    // Use global error handler for better error display
    handleError(error, { 
      type: 'file',
      retryAction: () => handleProductProcess(processOptions),
      cancelAction: () => cancelFileProcessing(selectedFileForProcessing.value.id)
    })
  }
}

const cancelFileProcessing = async (fileId) => {
  try {
    // Stop polling immediately
    filesStore.stopPolling(fileId)
    
    // Cancel processing on backend
    await ApiService.cancelFileProcessing(fileId)
    
    // Refresh files list
    await filesStore.fetchFiles()
    
    // Close modal
    showProductModal.value = false
    selectedFileForProcessing.value = null
  } catch (error) {
    console.error('Failed to cancel file processing:', error)
    handleError(error, { type: 'file' })
  }
}

const handleProductModalClose = () => {
  showProductModal.value = false
  selectedFileForProcessing.value = null
}

// Debug method to check polling status
const debugPollingStatus = () => {
  filesStore.getPollingStatus()
}

// Emergency stop all polling
const stopAllPolling = () => {
  filesStore.stopAllPolling()
  console.log('All polling stopped')
}

const handleDelete = (fileId) => {
  deleteFileId.value = fileId
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  try {
    const file = filesStore.uploads.find(f => f.id === deleteFileId.value) || 
                 filesStore.processed.find(f => f.id === deleteFileId.value)
    const fileName = file?.filename || 'Unknown file'
    
    await filesStore.deleteFile(deleteFileId.value)
    await filesStore.fetchFiles()
    
    showFileDeleted(fileName)
  } catch (error) {
    console.error('Failed to delete file:', error)
    handleError(error, { type: 'file' })
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
    const fileCount = filesStore.uploads.length + filesStore.processed.length
    await filesStore.deleteAllFiles()
    await filesStore.fetchFiles()
    
    showFileDeleted(`${fileCount} files`)
  } catch (error) {
    console.error('Failed to delete all files:', error)
    handleError(error, { type: 'file' })
  } finally {
    showDeleteAllModal.value = false
  }
}

const handleDownload = async (fileId) => {
  try {
    await filesStore.downloadFile(fileId)
  } catch (error) {
    console.error('Failed to download file:', error)
    handleError(error, { type: 'file' })
  }
}
</script>

<template>
  <MainLayout>
    <div class="min-h-screen bg-gray-50 px-4 sm:px-6 lg:px-8 py-1 sm:py-1">
      <!-- Header Section -->
      <div class="sm:flex sm:items-center mb-8">
        <div class="sm:flex-auto">
          <div class="flex items-center gap-3">
            <div class="w-12 h-12 bg-gray-500/80 backdrop-blur-sm rounded-2xl flex items-center justify-center">
              <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z" />
              </svg>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900 tracking-tight">File Manager</h1>
              <p class="mt-2 text-sm text-gray-600 font-medium">Upload, process, and manage your files with ease</p>
            </div>
          </div>
        </div>
        
        <!-- Delete All Button for Admins -->
        <div v-if="isAdmin" class="mt-6 sm:mt-0 sm:ml-16 sm:flex-none">
          <button
            @click="handleDeleteAll"
            class="inline-flex items-center justify-center rounded-2xl bg-red-600 px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-red-700 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200"
            title="Delete all files"
            aria-label="Delete all files"
          >
            <TrashIcon class="h-5 w-5 mr-2" aria-hidden="true" />
            Delete All Files
          </button>
        </div>
      </div>
        <!-- Loading State -->
        <div v-if="isLoading" class="flex items-center justify-center py-12" aria-live="polite">
          <div class="flex items-center space-x-3">
            <div class="animate-spin rounded-full h-6 w-6 border-2 border-gray-400/60 border-t-transparent"></div>
            <span class="text-sm font-medium text-slate-600">Loading files...</span>
          </div>
        </div>

        <!-- File Lists -->
        <div v-if="!isLoading" class="space-y-8">
          <!-- File Management Section -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- File Uploader Card -->
          <div class="group bg-gradient-to-br from-white/90 to-slate-50/90 backdrop-blur-sm rounded-2xl border border-slate-200/60 shadow-lg hover:shadow-xl transition-all duration-500 overflow-hidden">
            <!-- Header -->
            <div class="px-6 py-4 border-b border-slate-200/40">
              <div class="flex items-center space-x-4">
                <div class="w-12 h-12 bg-gradient-to-br from-gray-500 to-slate-600 rounded-xl flex items-center justify-center shadow-lg group-hover:shadow-xl transition-all duration-300 group-hover:scale-105">
                  <svg class="h-6 w-6 text-white rotate-90" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M12 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                  </svg>
                </div>
                <div>
                  <h3 class="text-xl font-bold text-slate-900 group-hover:text-gray-700 transition-colors duration-300">File Upload</h3>
                  <p class="text-sm text-slate-600 group-hover:text-gray-700 transition-colors duration-300">Upload your files for processing</p>
                </div>
              </div>
            </div>
            
            <!-- Upload Area -->
            <div class="p-6">
              <FileUploader :upload-progress="filesStore.uploadProgress" :error="null" :show-icon="true"
                @file-upload="handleFileUpload" class="w-full" />
            </div>
          </div>

          <!-- Uploads Card -->
          <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-200/60 shadow-sm hover:bg-white/90 transition-all duration-300">
            <div class="p-6">
              <!-- Custom Header -->
              <div class="flex items-center justify-between mb-4">
                <div class="flex items-center space-x-4">
                  <div class="w-12 h-12 bg-gradient-to-br from-gray-500 to-slate-600 rounded-2xl flex items-center justify-center shadow-lg">
                    <DocumentArrowUpIcon class="h-6 w-6 text-white" aria-hidden="true" />
                  </div>
                  <h3 class="text-lg font-semibold text-slate-900">Uploads</h3>
                </div>
              </div>
              
              <!-- File List -->
              <div v-if="paginatedUploads.length" :class="[
                'space-y-4',
                totalUploadPages > 1 ? 'min-h-[400px]' : ''
              ]">
                <div v-for="file in paginatedUploads" :key="file.id"
                  class="flex items-start justify-between p-5 bg-slate-50/60 backdrop-blur-sm rounded-2xl border border-slate-100/60 hover:bg-slate-100/80 transition-all duration-300">
                  <div class="flex items-start space-x-4 flex-1 min-w-0">
                    <div class="flex-shrink-0 mt-1">
                      <div class="w-14 h-14 bg-gray-100/80 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                        <svg class="w-7 h-7 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-sm font-semibold text-slate-900 truncate mb-2">{{ file.filename }}</p>
                      <p class="text-xs text-slate-500 mb-1">{{ file.formattedSize }}</p>
                      <p class="text-xs text-slate-500 mb-3">{{ file.formattedDate }}</p>
                      <ProcessingStatus v-if="isProcessing(file.id)" :percent="getProcessingStatus(file).percent"
                        :time-remaining="getProcessingStatus(file).timeRemaining"
                        :progress-width="getProcessingStatus(file).progressWidth" class="h-4 w-24 flex items-center"
                        aria-live="polite" />
                    </div>
                  </div>
                  <div class="flex items-center space-x-2 ml-6 flex-shrink-0">
                    <template v-if="!isProcessing(file.id)">
                      <button @click="handleProcess(file.id)"
                        class="inline-flex items-center px-3 py-2 text-xs font-medium text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 rounded-2xl hover:bg-gray-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
                        title="Process File" aria-label="Process File">
                        <PlayIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                        Process
                      </button>
                    </template>
                    <button @click="handleDelete(file.id)"
                      class="inline-flex items-center px-3 py-2 text-xs font-medium text-red-700 bg-red-100/80 backdrop-blur-sm border border-red-200/60 rounded-2xl hover:bg-red-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 transition-all duration-200"
                      title="Delete File" aria-label="Delete File">
                      <TrashIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                      Delete
                    </button>
                  </div>
                </div>
              </div>
              <div v-else :class="[
                'text-center py-8',
                totalUploadPages > 1 ? 'min-h-[400px]' : ''
              ]">
                <div class="w-20 h-20 mx-auto mb-4 bg-slate-100/60 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                  <DocumentArrowUpIcon class="h-10 w-10 text-slate-400" />
                </div>
                <p class="text-sm text-slate-500 font-medium">No uploads available</p>
              </div>
              
              <!-- Pagination Controls for Uploads -->
              <div v-if="totalUploadPages > 1" class="mt-4 flex justify-center items-center gap-2" role="navigation" aria-label="Uploads pagination">
                <button
                  @click="prevUploadPage"
                  :disabled="currentUploadPage === 1"
                  class="inline-flex items-center justify-center rounded-2xl px-3 py-1.5 text-sm font-semibold text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 shadow-sm hover:bg-gray-200/80 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Previous page"
                >
                  Previous
                </button>
                <button
                  v-for="page in totalUploadPages"
                  :key="page"
                  @click="goToUploadPage(page)"
                  :class="[
                    'inline-flex items-center justify-center rounded-2xl px-3 py-1.5 text-sm font-semibold',
                    currentUploadPage === page
                      ? 'bg-gray-600 text-white shadow-sm'
                      : 'bg-gray-100/80 backdrop-blur-sm text-gray-700 border border-gray-200/60 shadow-sm hover:bg-gray-200/80'
                  ]"
                  :aria-current="currentUploadPage === page ? 'page' : undefined"
                  :aria-label="`Go to page ${page}`"
                >
                  {{ page }}
                </button>
                <button
                  @click="nextUploadPage"
                  :disabled="currentUploadPage === totalUploadPages"
                  class="inline-flex items-center justify-center rounded-2xl px-3 py-1.5 text-sm font-semibold text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 shadow-sm hover:bg-gray-200/80 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Next page"
                >
                  Next
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Processed Files Card -->
        <div class="bg-white/80 backdrop-blur-sm rounded-2xl border border-slate-200/60 shadow-sm hover:bg-white/90 transition-all duration-300">
          <div class="p-6">
            <!-- Custom Header -->
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center space-x-4">
                <div class="w-12 h-12 bg-gradient-to-br from-gray-500 to-slate-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <DocumentCheckIcon class="h-6 w-6 text-white" aria-hidden="true" />
                </div>
                <h3 class="text-lg font-semibold text-slate-900">Processed Files</h3>
              </div>
            </div>
            
            <!-- File List -->
            <div v-if="paginatedProcessed.length" class="space-y-4">
              <div v-for="file in paginatedProcessed" :key="file.id"
                class="flex items-start justify-between p-5 bg-slate-50/60 backdrop-blur-sm rounded-2xl border border-slate-100/60 hover:bg-slate-100/80 transition-all duration-300">
                <div class="flex items-start space-x-4 flex-1 min-w-0">
                  <div class="flex-shrink-0 mt-1">
                    <div class="w-14 h-14 bg-gray-100/80 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                      <svg class="w-7 h-7 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                  </div>
                  <div class="flex-1 min-w-0">
                    <div class="flex items-center justify-between mb-2">
                      <p class="text-sm font-semibold text-slate-900 truncate">{{ file.filename }}</p>
                      <span class="text-xs text-slate-500 bg-slate-200/60 px-2 py-1 rounded-full">{{ file.formattedSize }}</span>
                    </div>
                    <p class="text-xs text-slate-500 mb-3">{{ file.formattedDate }}</p>
                  </div>
                </div>
                <div class="flex items-center space-x-2 ml-6 flex-shrink-0">
                  <button @click="handleDownload(file.id)"
                    class="inline-flex items-center px-3 py-2 text-xs font-medium text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 rounded-2xl hover:bg-gray-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
                    title="Download File" aria-label="Download File">
                    <ArrowDownTrayIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                    Download
                  </button>
                  <button @click="handleDelete(file.id)"
                    class="inline-flex items-center px-3 py-2 text-xs font-medium text-red-700 bg-red-100/80 backdrop-blur-sm border border-red-200/60 rounded-2xl hover:bg-red-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 transition-all duration-200"
                    title="Delete File" aria-label="Delete File">
                    <TrashIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                    Delete
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="text-center py-8">
              <div class="w-20 h-20 mx-auto mb-4 bg-slate-100/60 backdrop-blur-sm rounded-2xl flex items-center justify-center">
                <DocumentCheckIcon class="h-10 w-10 text-slate-400" />
              </div>
              <p class="text-sm text-slate-500 font-medium">No processed files available</p>
            </div>
            
            <!-- Pagination Controls for Processed Files -->
            <div v-if="totalPages > 1" class="mt-4 flex justify-center items-center gap-2" role="navigation" aria-label="Processed files pagination">
              <button
                @click="prevPage"
                :disabled="currentPage === 1"
                class="inline-flex items-center justify-center rounded-2xl px-3 py-1.5 text-sm font-semibold text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 shadow-sm hover:bg-gray-200/80 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Previous page"
              >
                Previous
              </button>
              <button
                v-for="page in totalPages"
                :key="page"
                @click="goToPage(page)"
                :class="[
                  'inline-flex items-center justify-center rounded-2xl px-3 py-1.5 text-sm font-semibold',
                  currentPage === page
                    ? 'bg-gray-600 text-white shadow-sm'
                    : 'bg-gray-100/80 backdrop-blur-sm text-gray-700 border border-gray-200/60 shadow-sm hover:bg-gray-200/80'
                ]"
                :aria-current="currentPage === page ? 'page' : undefined"
                :aria-label="`Go to page ${page}`"
              >
                {{ page }}
              </button>
              <button
                @click="nextPage"
                :disabled="currentPage === totalPages"
                class="inline-flex items-center justify-center rounded-2xl px-3 py-1.5 text-sm font-semibold text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 shadow-sm hover:bg-gray-200/80 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Next page"
              >
                Next
              </button>
            </div>
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
        v-if="selectedFileForProcessing"
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