<!--
GDPR Tool Dashboard View - Main Dashboard Interface

This component provides the main dashboard interface for the GDPR compliance tool.
It displays file management overview, processing status, and quick access to key features.

Key Features:
- File Overview: Display uploaded and processed files with counts
- Processing Status: Real-time processing progress and time estimates
- Quick Actions: Direct access to file management and user management
- Role-Based Access: Admin features shown only to administrators
- File Operations: Process, download, and delete files directly from dashboard
- Responsive Design: Mobile-first responsive layout with expandable cards

Dashboard Features:
- File Statistics: Overview of uploaded and processed files
- Processing Progress: Real-time status updates for file processing
- Quick File Operations: Process, download, and delete files
- Navigation Cards: Quick access to main application features
- User Welcome: Personalized greeting with username

Admin Features:
- User Management Access: Quick link to user management (admin only)
- Enhanced File Operations: Additional administrative capabilities
- Role-Based UI: Interface adapts based on user role

The component provides a comprehensive dashboard overview for GDPR compliance
tool users with role-based functionality and efficient file management.
-->

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useFilesStore } from '../stores/files'
import { useAuthStore } from '../stores/auth'
import { useErrorHandler } from '../composables/useErrorHandler'
import ApiService from '../services/api'
import MainLayout from '../components/MainLayout.vue'
import ProcessingStatus from '../components/ProcessingStatus.vue'
import ConfirmDeleteDialog from '../components/ConfirmDeleteDialog.vue'
import {
  ClipboardDocumentListIcon as Docs,
  FolderIcon as FilesIcon,
  UsersIcon as Users,
  PlayIcon,
  ArrowDownTrayIcon as DownloadIcon,
  ArrowUpTrayIcon as UploadIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const filesStore = useFilesStore()
const authStore = useAuthStore()
const { handleError } = useErrorHandler()
const isLoading = ref(false)
const showDeleteModal = ref(false)
const deleteFileId = ref(null)
const uploadsExpanded = ref(false)
const processedExpanded = ref(false)
const totalUsers = ref(0)

// Pagination state
const itemsPerPage = 3
const currentUploadsPage = ref(1)
const currentProcessedPage = ref(1)

// Global admin check boolean: checks if role contains "admin" (case-insensitive)
const adminCheck = computed(() => {
  return authStore.user?.role ? authStore.user.role.toLowerCase().includes('admin') : false
})

// Paginated uploads
const paginatedUploads = computed(() => {
  const start = (currentUploadsPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filesStore.uploads.slice(start, end)
})

// Paginated processed files
const paginatedProcessed = computed(() => {
  const start = (currentProcessedPage.value - 1) * itemsPerPage
  const end = start + itemsPerPage
  return filesStore.processed.slice(start, end)
})

// Total pages for uploads
const totalUploadsPages = computed(() => Math.ceil(filesStore.uploads.length / itemsPerPage))

// Total pages for processed files
const totalProcessedPages = computed(() => Math.ceil(filesStore.processed.length / itemsPerPage))

onMounted(async () => {
  isLoading.value = true
  if (!authStore.user) {
    await authStore.fetchUser() // Implement this in authStore if missing
  }
  await filesStore.fetchFiles()
  
  // Fetch user count if admin
  if (adminCheck.value) {
    try {
      const users = await ApiService.getUsers()
      totalUsers.value = users.length + 1 // +1 for admin user
    } catch (error) {
      console.error('Failed to fetch users:', error)
      totalUsers.value = 1 // Fallback to just admin
    }
  }
  
  isLoading.value = false
})

// Utility functions
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString()
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
}

const formatTimeRemaining = (seconds) => {
  if (!seconds || seconds <= 0) return '0s'
  if (seconds < 60) return `${Math.round(seconds)}s`
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`
  return `${Math.round(seconds / 3600)}h`
}

const getProgressWidth = (fileId) => {
  const status = filesStore.getProcessingStatus(fileId)
  if (!status) return '0%'
  return `${Math.round((status.completedSize / status.totalSize) * 100)}%`
}

const getPercent = (fileId) => {
  const status = filesStore.getProcessingStatus(fileId)
  if (!status) return '0'
  return Math.round((status.completedSize / status.totalSize) * 100).toFixed(1)
}

// Toggle functions for expandable cards
const toggleUploadsExpanded = () => {
  uploadsExpanded.value = !uploadsExpanded.value
}

const toggleProcessedExpanded = () => {
  processedExpanded.value = !processedExpanded.value
}

const handleProcess = async (fileId) => {
  try {
    await filesStore.processFile(fileId)
    await filesStore.fetchFiles()
  } catch (error) {
    console.error('Failed to process file:', error)
    handleError(error, { type: 'file' })
  }
}

const handleDelete = (fileId) => {
  deleteFileId.value = fileId
  showDeleteModal.value = true
}

const confirmDelete = async () => {
  try {
    await filesStore.deleteFile(deleteFileId.value)
    await filesStore.fetchFiles()
  } catch (error) {
    console.error('Failed to delete file:', error)
    handleError(error, { type: 'file' })
  } finally {
    showDeleteModal.value = false
    deleteFileId.value = null
  }
}

// Pagination navigation functions for uploads
const goToUploadsPage = (page) => {
  currentUploadsPage.value = page
}

const prevUploadsPage = () => {
  if (currentUploadsPage.value > 1) {
    currentUploadsPage.value--
  }
}

const nextUploadsPage = () => {
  if (currentUploadsPage.value < totalUploadsPages.value) {
    currentUploadsPage.value++
  }
}

// Pagination navigation functions for processed files
const goToProcessedPage = (page) => {
  currentProcessedPage.value = page
}

const prevProcessedPage = () => {
  if (currentProcessedPage.value > 1) {
    currentProcessedPage.value--
  }
}

const nextProcessedPage = () => {
  if (currentProcessedPage.value < totalProcessedPages.value) {
    currentProcessedPage.value++
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

const handleFileUpload = async (files) => {
  try {
    for (const file of files) {
      await filesStore.uploadFile(file)
    }
  } catch (error) {
    console.error('Upload error:', error)
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
            <div class="w-12 h-12 bg-gray-500/80 backdrop-blur-sm rounded-lg flex items-center justify-center">
              <svg class="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
              </svg>
            </div>
            <div>
              <h1 class="text-2xl font-bold text-gray-900 tracking-tight">
                Welcome back, {{ authStore.user?.username?.charAt(0).toUpperCase() + authStore.user?.username?.slice(1) || 'User' }}
              </h1>
              <p class="mt-2 text-sm text-gray-600 font-medium">GDPR Compliance Dashboard</p>
            </div>
          </div>
        </div>
        
        <!-- Quick Stats -->
        <div class="mt-6 sm:mt-0 sm:ml-16 sm:flex-none flex space-x-4">
          <div class="text-center mb-2">
            <p class="text-xs text-slate-500 mb-4">Quick Stats - Click to navigate</p>
          </div>
          <router-link v-if="adminCheck" to="/users" class="w-12 h-12 bg-gray-100/80 backdrop-blur-sm rounded-lg flex flex-col items-center justify-center hover:scale-105 transition-all duration-200 hover:bg-slate-100/60 p-2">
            <div class="text-lg font-bold text-slate-900">{{ totalUsers }}</div>
            <div class="text-xs text-slate-500 uppercase tracking-wide">Users</div>
          </router-link>
          <div v-else class="w-12 h-12 bg-gray-100/80 backdrop-blur-sm rounded-lg flex flex-col items-center justify-center p-2">
            <div class="text-lg font-bold text-slate-900">1</div>
            <div class="text-xs text-slate-500 uppercase tracking-wide">Users</div>
          </div>
          <router-link to="/files" class="w-12 h-12 bg-gray-100/80 backdrop-blur-sm rounded-lg flex flex-col items-center justify-center hover:scale-105 transition-all duration-200 hover:bg-slate-100/60 p-2">
            <div class="text-lg font-bold text-slate-900">{{ filesStore.uploads.length }}</div>
            <div class="text-xs text-slate-500 uppercase tracking-wide">Uploads</div>
          </router-link>
          <router-link to="/files" class="w-12 h-12 bg-gray-100/80 backdrop-blur-sm rounded-lg flex flex-col items-center justify-center hover:scale-105 transition-all duration-200 hover:bg-slate-100/60 p-2">
            <div class="text-lg font-bold text-slate-900">{{ filesStore.processed.length }}</div>
            <div class="text-xs text-slate-500 uppercase tracking-wide">Processed</div>
          </router-link>
        </div>
      </div>
      <!-- Loading State -->
      <div v-if="isLoading" class="flex items-center justify-center py-12" aria-live="polite">
        <div class="flex items-center space-x-3">
          <div class="animate-spin rounded-full h-6 w-6 border-2 border-gray-400/60 border-t-transparent"></div>
          <span class="text-sm font-medium text-slate-600">Loading dashboard...</span>
        </div>
      </div>

      <div v-if="!isLoading" class="space-y-8">
          <!-- File Management Section -->
          <div class="space-y-12">
            <!-- Uploads Card -->
            <div class="bg-white/80 backdrop-blur-sm rounded-lg border border-slate-200/60 shadow-sm hover:bg-white/90 transition-all duration-300">
              <div class="p-6">
                <!-- Custom Header -->
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center space-x-4">
                    <div class="w-14 h-14 bg-gray-100/80 backdrop-blur-sm rounded-lg flex items-center justify-center">
                      <UploadIcon class="h-7 w-7 text-gray-600" aria-hidden="true" />
                    </div>
                    <div>
                      <h3 class="text-lg font-semibold text-slate-900">Uploads</h3>
                      <p class="text-sm text-slate-500">Files ready for processing - click expand to view and process</p>
                    </div>
                  </div>
                  <button @click="toggleUploadsExpanded" class="p-2 hover:bg-slate-100/60 hover:scale-105 rounded-lg transition-all duration-200 hover:shadow-md">
                    <svg class="w-7 h-7 text-slate-500" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
                
                <!-- Expandable Content -->
                <div v-if="uploadsExpanded" class="border-t border-slate-200/60 pt-4">
                  <div v-if="paginatedUploads.length" :class="[
                    'space-y-4',
                    totalUploadsPages > 1 ? 'min-h-[400px]' : ''
                  ]">
                      <div v-for="file in paginatedUploads" :key="file.id"
                        class="flex items-start justify-between p-5 bg-slate-50/60 backdrop-blur-sm rounded-lg border border-slate-100/60 hover:bg-slate-100/80 transition-all duration-300">
                        <div class="flex items-start space-x-4 flex-1 min-w-0">
                          <div class="flex-shrink-0 mt-1">
                            <div class="w-14 h-14 bg-gray-100/80 backdrop-blur-sm rounded-lg flex items-center justify-center">
                              <svg class="w-7 h-7 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                              </svg>
                            </div>
                          </div>
                          <div class="flex-1 min-w-0">
                            <div class="flex items-center justify-between mb-2">
                              <p class="text-sm font-semibold text-slate-900 truncate">{{ file.filename }}</p>
                              <span class="text-xs text-slate-500 bg-slate-200/60 px-2 py-1 rounded-full">{{ formatFileSize(file.file_size) }}</span>
                            </div>
                            <p class="text-xs text-slate-500 mb-3">{{ formatDate(file.create_date) }}</p>
                            <ProcessingStatus v-if="filesStore.getProcessingStatus(file.id)" :percent="getPercent(file.id)"
                              :time-remaining="formatTimeRemaining(filesStore.getProcessingStatus(file.id).timeRemaining)"
                              :progress-width="getProgressWidth(file.id)" class="h-4 w-24 flex items-center"
                              aria-live="polite" />
                          </div>
                        </div>
                        <div class="flex items-center space-x-2 ml-6 flex-shrink-0">
                          <button v-if="!filesStore.getProcessingStatus(file.id)" @click="handleProcess(file.id)"
                            class="inline-flex items-center px-3 py-2 text-xs font-medium text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 rounded-md hover:bg-gray-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200"
                            title="Process File" aria-label="Process File">
                            <PlayIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                            Process
                          </button>
                          <button @click="handleDownload(file.id)"
                            class="inline-flex items-center px-3 py-2 text-xs font-medium text-slate-700 bg-slate-100/80 backdrop-blur-sm border border-slate-200/60 rounded-md hover:bg-slate-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 transition-all duration-200"
                            title="Download File" aria-label="Download File">
                            <DownloadIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                            Download
                          </button>
                          <button @click="handleDelete(file.id)"
                            class="inline-flex items-center px-3 py-2 text-xs font-medium text-red-700 bg-red-100/80 backdrop-blur-sm border border-red-200/60 rounded-md hover:bg-red-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 transition-all duration-200"
                            title="Delete File" aria-label="Delete File">
                            <TrashIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                    <div v-else :class="[
                      'text-center py-8',
                      totalUploadsPages > 1 ? 'min-h-[400px]' : ''
                    ]">
                      <div class="w-20 h-20 mx-auto mb-4 bg-slate-100/60 backdrop-blur-sm rounded-lg flex items-center justify-center">
                        <UploadIcon class="h-10 w-10 text-slate-400" />
                      </div>
                      <p class="text-sm text-slate-500 font-medium">No uploads available</p>
                    </div>
                  </div>
                </div>
                
                <!-- Pagination Controls for Uploads -->
                <div v-if="uploadsExpanded && totalUploadsPages > 1" class="mt-4 flex justify-center items-center gap-2" role="navigation" aria-label="Uploads pagination">
                    <button
                      @click="prevUploadsPage"
                      :disabled="currentUploadsPage === 1"
                      class="inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 shadow-sm hover:bg-gray-200/80 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      aria-label="Previous page"
                    >
                      Previous
                    </button>
                    <button
                      v-for="page in totalUploadsPages"
                      :key="page"
                      @click="goToUploadsPage(page)"
                      :class="[
                        'inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold',
                        currentUploadsPage === page
                          ? 'bg-gray-600 text-white shadow-sm'
                          : 'bg-gray-100/80 backdrop-blur-sm text-gray-700 border border-gray-200/60 shadow-sm hover:bg-gray-200/80'
                      ]"
                      :aria-current="currentUploadsPage === page ? 'page' : undefined"
                      :aria-label="`Go to page ${page}`"
                    >
                      {{ page }}
                    </button>
                    <button
                      @click="nextUploadsPage"
                      :disabled="currentUploadsPage === totalUploadsPages"
                      class="inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 shadow-sm hover:bg-gray-200/80 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      aria-label="Next page"
                    >
                      Next
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- Processed Files Card -->
            <div class="bg-white/80 backdrop-blur-sm rounded-lg border border-slate-200/60 shadow-sm hover:bg-white/90 transition-all duration-300 mt-8">
              <div class="p-6">
                <!-- Custom Header -->
                <div class="flex items-center justify-between mb-4">
                  <div class="flex items-center space-x-4">
                    <div class="w-14 h-14 bg-gray-100/80 backdrop-blur-sm rounded-lg flex items-center justify-center">
                      <Docs class="h-7 w-7 text-gray-600" aria-hidden="true" />
                    </div>
                    <div>
                      <h3 class="text-lg font-semibold text-slate-900">Processed Files</h3>
                      <p class="text-sm text-slate-500">Files with sensitive data masked - ready for download and use</p>
                    </div>
                  </div>
                  <button @click="toggleProcessedExpanded" class="p-2 hover:bg-slate-100/60 hover:scale-105 rounded-lg transition-all duration-200 hover:shadow-md">
                    <svg class="w-7 h-7 text-slate-500" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
                
                <!-- Expandable Content -->
                <div v-if="processedExpanded" class="border-t border-slate-200/60 pt-4">
                  <div v-if="paginatedProcessed.length" :class="[
                    'space-y-4',
                    totalProcessedPages > 1 ? 'min-h-[400px]' : ''
                  ]">
                      <div v-for="file in paginatedProcessed" :key="file.id"
                        class="flex items-start justify-between p-5 bg-slate-50/60 backdrop-blur-sm rounded-lg border border-slate-100/60 hover:bg-slate-100/80 transition-all duration-300">
                        <div class="flex items-start space-x-4 flex-1 min-w-0">
                          <div class="flex-shrink-0 mt-1">
                            <div class="w-14 h-14 bg-gray-100/80 backdrop-blur-sm rounded-lg flex items-center justify-center">
                              <svg class="w-7 h-7 text-gray-600" fill="none" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                            </div>
                          </div>
                          <div class="flex-1 min-w-0">
                            <div class="flex items-center justify-between mb-2">
                              <p class="text-sm font-semibold text-slate-900 truncate">{{ file.filename }}</p>
                              <span class="text-xs text-slate-500 bg-slate-200/60 px-2 py-1 rounded-full">{{ formatFileSize(file.file_size) }}</span>
                            </div>
                            <p class="text-xs text-slate-500">{{ formatDate(file.create_date) }}</p>
                          </div>
                        </div>
                        <div class="flex items-center space-x-2 ml-6 flex-shrink-0">
                          <button @click="handleDownload(file.id)"
                            class="inline-flex items-center px-3 py-2 text-xs font-medium text-slate-700 bg-slate-100/80 backdrop-blur-sm border border-slate-200/60 rounded-md hover:bg-slate-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2 transition-all duration-200"
                            title="Download File" aria-label="Download File">
                            <DownloadIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                            Download
                          </button>
                          <button @click="handleDelete(file.id)"
                            class="inline-flex items-center px-3 py-2 text-xs font-medium text-red-700 bg-red-100/80 backdrop-blur-sm border border-red-200/60 rounded-md hover:bg-red-200/80 hover:scale-105 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-red-400 focus:ring-offset-2 transition-all duration-200"
                            title="Delete File" aria-label="Delete File">
                            <TrashIcon class="h-6 w-6 mr-1.5" aria-hidden="true" />
                            Delete
                          </button>
                        </div>
                      </div>
                    </div>
                    <div v-else :class="[
                      'text-center py-8',
                      totalProcessedPages > 1 ? 'min-h-[400px]' : ''
                    ]">
                      <div class="w-20 h-20 mx-auto mb-4 bg-slate-100/60 backdrop-blur-sm rounded-lg flex items-center justify-center">
                        <Docs class="h-10 w-10 text-slate-400" />
                      </div>
                      <p class="text-sm text-slate-500 font-medium">No processed files available</p>
                    </div>
                  </div>
                </div>
                
                <!-- Pagination Controls for Processed Files -->
                <div v-if="processedExpanded && totalProcessedPages > 1" class="mt-4 flex justify-center items-center gap-2" role="navigation" aria-label="Processed files pagination">
                    <button
                      @click="prevProcessedPage"
                      :disabled="currentProcessedPage === 1"
                      class="inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 shadow-sm hover:bg-gray-200/80 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      aria-label="Previous page"
                    >
                      Previous
                    </button>
                    <button
                      v-for="page in totalProcessedPages"
                      :key="page"
                      @click="goToProcessedPage(page)"
                      :class="[
                        'inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold',
                        currentProcessedPage === page
                          ? 'bg-gray-600 text-white shadow-sm'
                          : 'bg-gray-100/80 backdrop-blur-sm text-gray-700 border border-gray-200/60 shadow-sm hover:bg-gray-200/80'
                      ]"
                      :aria-current="currentProcessedPage === page ? 'page' : undefined"
                      :aria-label="`Go to page ${page}`"
                    >
                      {{ page }}
                    </button>
                    <button
                      @click="nextProcessedPage"
                      :disabled="currentProcessedPage === totalProcessedPages"
                      class="inline-flex items-center justify-center rounded-lg px-3 py-1.5 text-sm font-semibold text-gray-700 bg-gray-100/80 backdrop-blur-sm border border-gray-200/60 shadow-sm hover:bg-gray-200/80 focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                      aria-label="Next page"
                    >
                      Next
                    </button>
                  </div>
                </div>

          <!-- Management Actions -->
          <div class="w-full mt-8">
            <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <!-- User Management Card (Admin Only) -->
            <div v-if="adminCheck" class="bg-white/80 backdrop-blur-sm rounded-lg border border-slate-200/60 shadow-sm hover:bg-white/90 hover:shadow-md transition-all duration-300">
              <div class="p-6">
                <div class="flex items-center space-x-4 mb-4">
                  <div class="w-16 h-16 bg-gray-100/80 backdrop-blur-sm rounded-lg flex items-center justify-center">
                    <Users class="h-8 w-8 text-gray-600" />
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-slate-900">User Management</h3>
                    <p class="text-sm text-slate-600">Admin only - Create, edit, and manage user accounts</p>
                  </div>
                </div>
                <router-link to="/users"
                  class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-gray-600/80 backdrop-blur-sm border border-transparent rounded-md hover:bg-gray-700/80 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200">
                  View All Users
                  <svg class="ml-2 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </router-link>
              </div>
            </div>

            <!-- File Management Card -->
            <div class="bg-white/80 backdrop-blur-sm rounded-lg border border-slate-200/60 shadow-sm hover:bg-white/90 hover:shadow-md transition-all duration-300">
              <div class="p-6">
                <div class="flex items-center space-x-4 mb-4">
                  <div class="w-16 h-16 bg-gray-100/80 backdrop-blur-sm rounded-lg flex items-center justify-center">
                    <FilesIcon class="h-8 w-8 text-gray-600" />
                  </div>
                  <div>
                    <h3 class="text-lg font-semibold text-slate-900">File Management</h3>
                    <p class="text-sm text-slate-600">Upload new files and manage all your files in one place</p>
                  </div>
                </div>
                <router-link to="/files"
                  class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-gray-600/80 backdrop-blur-sm border border-transparent rounded-md hover:bg-gray-700/80 hover:scale-105 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2 transition-all duration-200">
                  Manage Files
                  <svg class="ml-2 w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
                  </svg>
                </router-link>
              </div>
            </div>
          </div>

      </div>

    <!-- Footer -->
    <footer class="mt-12 text-center text-sm text-gray-500 px-4 sm:px-16">
      © {{ new Date().getFullYear() }} GDPR Processor. All rights reserved.
      <a href="/privacy" class="text-indigo-600 hover:text-indigo-700 ml-2 transition-colors duration-200">Privacy Policy</a>
    </footer>
    </div>

    <!-- Delete Confirmation Dialog -->
    <ConfirmDeleteDialog v-if="showDeleteModal" :open="showDeleteModal" item-type="file"
      @close="showDeleteModal = false" @confirm="confirmDelete" />
  </MainLayout>
</template>

<style scoped>
/* Enterprise Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fadeIn 0.4s ease-out;
}

/* Enterprise Focus States */
.focus\:ring-2:focus {
  box-shadow: 0 0 0 2px rgba(107, 114, 128, 0.5);
}

/* Smooth transitions */
* {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke, opacity, box-shadow, transform, backdrop-filter;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* Enterprise hover effects */
.hover\:shadow-md:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

/* Transparency effects */
.backdrop-blur-sm {
  backdrop-filter: blur(4px);
}

/* Gray color variations */
.bg-gray-500\/80 {
  background-color: rgba(107, 114, 128, 0.8);
}

.bg-gray-100\/80 {
  background-color: rgba(243, 244, 246, 0.8);
}

.bg-gray-200\/80 {
  background-color: rgba(229, 231, 235, 0.8);
}

.bg-gray-600\/80 {
  background-color: rgba(75, 85, 99, 0.8);
}

.bg-gray-700\/80 {
  background-color: rgba(55, 65, 81, 0.8);
}

/* Custom scrollbar for enterprise feel */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>