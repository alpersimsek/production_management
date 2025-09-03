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
import MainLayout from '../components/MainLayout.vue'
import ExpandableCard from '../components/ExpandableCard.vue'
import ActionCard from '../components/ActionCard.vue'
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
const isLoading = ref(false)
const showDeleteModal = ref(false)
const deleteFileId = ref(null)
const uploadError = ref('')

// Global admin check boolean: checks if role contains "admin" (case-insensitive)
const adminCheck = computed(() => {
  return authStore.user?.role ? authStore.user.role.toLowerCase().includes('admin') : false
})

onMounted(async () => {
  isLoading.value = true
  if (!authStore.user) {
    await authStore.fetchUser() // Implement this in authStore if missing
  }
  await filesStore.fetchFiles()
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

const handleProcess = async (fileId) => {
  try {
    uploadError.value = ''
    await filesStore.processFile(fileId)
    await filesStore.fetchFiles()
  } catch (error) {
    console.error('Failed to process file:', error)
    uploadError.value = `Failed to process file: ${error.message || 'Unknown error'}`
  }
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

const handleDownload = async (fileId) => {
  try {
    uploadError.value = ''
    await filesStore.downloadFile(fileId)
  } catch (error) {
    console.error('Failed to download file:', error)
    uploadError.value = `Download failed: ${error.message || 'The file may no longer exist or you may not have permission to access it.'}`
  }
}

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
</script>

<template>
  <MainLayout>
    <div class="min-h-screen bg-gray-50 px-4 sm:px-6 lg:px-8 py-1 sm:py-1">
      <!-- Header -->
      <div class="sm:flex sm:items-center mb-8">
        <div class="sm:flex-auto">
          <div class="flex items-center gap-3">
            <svg class="h-8 w-8 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" aria-hidden="true">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.25 12l8.954-8.955c.44-.439 1.152-.439 1.591 0L21.75 12M4.5 9.75v10.125c0 .621.504 1.125 1.125 1.125H9.75v-4.875c0-.621.504-1.125 1.125-1.125h2.25c.621 0 1.125.504 1.125 1.125V21h4.125c.621 0 1.125-.504 1.125-1.125V9.75M8.25 21h8.25" />
            </svg>
            <h1 class="text-2xl font-bold text-gray-900 tracking-tight">
              Welcome back, {{ authStore.user?.username.charAt(0).toUpperCase() + authStore.user?.username.slice(1) ||
                'User' }}
            </h1>
          </div>
          <p class="mt-2 text-sm text-gray-600 font-medium">
            Manage your files and system settings from your dashboard
          </p>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="py-8 flex justify-center items-center" aria-live="polite">
        <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600"></div>
        <p class="ml-4 text-sm font-medium text-gray-600">Loading dashboard...</p>
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

      <!-- Main Content -->
      <div v-if="!isLoading" class="space-y-8">
        <!-- Uploads and Processed Files (Expandable Cards) -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-fade-in">
          <!-- Uploads Card -->
          <ExpandableCard title="Uploads" :count="filesStore.uploads.length" :icon="UploadIcon" expandable
            class="bg-white rounded-xl shadow-sm border border-gray-100">
            <template #icon>
              <UploadIcon class="h-8 w-8 text-gray-600" aria-hidden="true" />
            </template>
            <template #content>
              <div class="px-4 sm:px-6 pb-5">

                <div v-if="filesStore.uploads.length" class="space-y-3">
                  <div v-for="file in filesStore.uploads" :key="file.id"
                    class="grid grid-cols-[2fr,1fr] items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200">
                    <div class="min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">{{ file.filename }}</p>
                      <p class="text-xs text-gray-500">{{ formatDate(file.create_date) }}</p>
                      <ProcessingStatus v-if="filesStore.getProcessingStatus(file.id)" :percent="getPercent(file.id)"
                        :time-remaining="formatTimeRemaining(filesStore.getProcessingStatus(file.id).timeRemaining)"
                        :progress-width="getProgressWidth(file.id)" class="h-5 w-20 sm:w-24 flex items-center mt-2"
                        aria-live="polite" />
                    </div>
                    <div class="flex items-center gap-2 justify-end">
                      <span class="text-xs text-gray-500">{{ formatFileSize(file.file_size) }}</span>
                      <button v-if="!filesStore.getProcessingStatus(file.id)" @click="handleProcess(file.id)"
                        class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                        title="Process File" aria-label="Process File">
                        <PlayIcon class="h-5 w-5" aria-hidden="true" />
                      </button>
                      <button @click="handleDownload(file.id)"
                        class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                        title="Download File" aria-label="Download File">
                        <DownloadIcon class="h-5 w-5" aria-hidden="true" />
                      </button>
                      <button @click="handleDelete(file.id)"
                        class="inline-flex items-center justify-center rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                        title="Delete File" aria-label="Delete File">
                        <TrashIcon class="h-5 w-5 text-gray-600 hover:text-red-600" aria-hidden="true" />
                      </button>
                    </div>
                  </div>
                </div>
                <p v-else class="text-sm text-gray-600 font-medium text-center py-4">
                  No uploads available.
                </p>
              </div>
            </template>
          </ExpandableCard>

          <!-- Processed Files Card -->
          <ExpandableCard title="Processed Files" :count="filesStore.processed.length" :icon="Docs" expandable
            class="bg-white rounded-xl shadow-sm border border-gray-100">
            <template #icon>
              <Docs class="h-8 w-8 text-gray-600" aria-hidden="true" />
            </template>
            <template #content>
              <div class="px-4 sm:px-6 pb-5">
                <div v-if="filesStore.processed.length" class="space-y-3">
                  <div v-for="file in filesStore.processed" :key="file.id"
                    class="grid grid-cols-[2fr,1fr] items-center gap-4 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200">
                    <div class="min-w-0">
                      <p class="text-sm font-medium text-gray-900 truncate">{{ file.filename }}</p>
                      <p class="text-xs text-gray-500">{{ formatDate(file.create_date) }}</p>
                    </div>
                    <div class="flex items-center gap-2 justify-end">
                      <span class="text-xs text-gray-500">{{ formatFileSize(file.file_size) }}</span>
                      <button @click="handleDownload(file.id)"
                        class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-2.5 py-1.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                        title="Download File" aria-label="Download File">
                        <DownloadIcon class="h-5 w-5" aria-hidden="true" />
                      </button>
                      <button @click="handleDelete(file.id)"
                        class="inline-flex items-center justify-center rounded-lg border border-gray-200 bg-white px-2.5 py-1.5 text-sm font-semibold text-gray-700 shadow-sm hover:bg-gray-50 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                        title="Delete File" aria-label="Delete File">
                        <TrashIcon class="h-5 w-5 text-gray-600 hover:text-red-600" aria-hidden="true" />
                      </button>
                    </div>
                  </div>
                </div>
                <p v-else class="text-sm text-gray-600 font-medium text-center py-4">
                  No processed files available.
                </p>
              </div>
            </template>
          </ExpandableCard>
        </div>

        <!-- Action Cards -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 animate-fade-in">
          <!-- User Management Card (Admin Only) -->
          <ActionCard v-if="adminCheck" title="User Management" description="Manage system users and their permissions"
            link-to="/users" link-text="View All Users"
            class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6 hover:shadow-md transition-all duration-200 min-h-[150px]">
            <template #icon>
              <Users class="h-8 w-8 text-gray-600 flex-shrink-0" />
            </template>
          </ActionCard>

          <!-- File Management Card -->
          <ActionCard title="File Management" description="Upload and process files for GDPR compliance"
            link-to="/files" link-text="Manage Files" :custom-class="!adminCheck ? 'lg:col-span-2' : ''"
            class="bg-white rounded-xl shadow-sm border border-gray-100 p-4 sm:p-6 hover:shadow-md transition-all duration-200 min-h-[150px]">
            <template #icon>
              <FilesIcon class="h-8 w-8 text-gray-600 flex-shrink-0" />
            </template>
          </ActionCard>
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
</style>