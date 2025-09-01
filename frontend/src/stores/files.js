/**
 * Files management store for the GDPR tool frontend using Pinia
 * 
 * This store manages file-related state and operations, including file uploads,
 * processing status tracking, and file management operations. It handles real-time
 * progress updates, polling for processing status, and maintains separate collections
 * for uploaded and processed files.
 * 
 * Key Features:
 * - File upload with progress tracking and event handling
 * - Real-time processing status monitoring with polling
 * - Separate state management for uploads and processed files
 * - Progress tracking for both upload and processing operations
 * - File operations (delete, download, bulk delete)
 * - Product-based file processing with enhanced workflow
 * 
 * State:
 * - uploads: Array of files in 'created' or 'in-progress' status
 * - processed: Array of files in 'done' status
 * - processingFiles: Map tracking processing progress by file ID
 * - uploadProgress: Map tracking upload progress by file name
 * 
 * Actions:
 * - fetchFiles(): Retrieves all files and categorizes by status
 * - uploadFile(file): Handles file upload with progress tracking
 * - processFile(fileId): Initiates file processing with status polling
 * - processFileWithProduct(fileId, productId): Enhanced processing with product selection
 * - deleteFile(fileId): Removes file from both uploads and processed arrays
 * - deleteAllFiles(): Clears all files and progress tracking
 * - downloadFile(fileId): Initiates file download
 * 
 * Getters:
 * - getUploads: Returns array of uploaded files
 * - getProcessed: Returns array of processed files
 * - getProcessingStatus(fileId): Returns processing status for specific file
 * 
 * Progress Tracking:
 * - Upload progress: Tracks bytes uploaded vs total file size
 * - Processing progress: Tracks completed size vs total size with time remaining
 * - Real-time updates: Uses polling and custom events for live updates
 * 
 * Usage:
 * ```javascript
 * import { useFilesStore } from '@/stores/files'
 * 
 * const filesStore = useFilesStore()
 * 
 * // Upload file
 * await filesStore.uploadFile(file)
 * 
 * // Process file
 * await filesStore.processFile(fileId)
 * 
 * // Get processing status
 * const status = filesStore.getProcessingStatus(fileId)
 * ```
 */

import { defineStore } from 'pinia'
import ApiService from '@/services/api'

export const useFilesStore = defineStore('files', {
  state: () => ({
    uploads: [],
    processed: [],
    processingFiles: new Map(), // Tracks files being processed: { id: { completedSize, totalSize, timeRemaining } }
    uploadProgress: new Map(), // Tracks upload progress: { fileName: { loaded, total, percent } }
  }),

  getters: {
    getUploads: (state) => state.uploads,
    getProcessed: (state) => state.processed,
    getProcessingStatus: (state) => (fileId) => state.processingFiles.get(fileId),
  },

  actions: {
    async fetchFiles() {
      try {
        const files = await ApiService.getFiles()
        this.uploads = files.filter((file) => file.status === 'created' || file.status === 'in-progress')
        this.processed = files.filter((file) => file.status === 'done')

        // Track files in progress
        const inProgress = files.filter((file) => file.status === 'in-progress')
        inProgress.forEach((file) => {
          if (!this.processingFiles.has(file.id)) {
            // Use extracted_size for progress calculation when available (for archives)

            this.processingFiles.set(file.id, {
              completedSize: file.completed_size || 0,
              totalSize: file.extracted_size || file.file_size,
              timeRemaining: file.time_remaining || 0,
            })
          }
        })
      } catch (error) {
        console.error('Failed to fetch files:', error)
        throw error
      }
    },

    async uploadFile(file) {
      try {
        // Initialize upload progress
        this.uploadProgress.set(file.name, {
          loaded: 0,
          total: file.size,
          percent: 0,
        })

        // Setup progress event listener
        const handleProgress = (event) => {
          const { fileId, progress } = event.detail
          if (fileId === file.name) {
            this.uploadProgress.set(fileId, progress)
          }
        }

        // Add event listener
        window.addEventListener('file-upload-progress', handleProgress)

        try {
          const uploadedFile = await ApiService.uploadFile(file)
          this.uploads.push(uploadedFile)
          return uploadedFile
        } finally {
          // Clean up
          window.removeEventListener('file-upload-progress', handleProgress)
          this.uploadProgress.delete(file.name)
        }
      } catch (error) {
        console.error('Failed to upload file:', error)
        this.uploadProgress.delete(file.name)
        throw error
      }
    },

    async processFile(fileId) {
      try {
        const file = this.uploads.find((f) => f.id === fileId)
        if (!file) {
          console.log(`File ${fileId} not found in uploads`)
          return
        }

        console.log(`Starting process for file:`, file)

        // Initialize processing status
        this.processingFiles.set(fileId, {
          completedSize: 0,
          totalSize: file.extracted_size || file.file_size,
          timeRemaining: 0,
        })
        // console.log(`Initialized processing status for ${fileId}`)

        // Start processing in background
        ApiService.processFile(fileId).catch((error) => {
          console.error('Process request failed:', error)
        })

        // console.log('Started processing, beginning polling')

        // Start polling for progress immediately
        const pollInterval = setInterval(async () => {
          try {
            console.log(`Polling for file ${fileId} status...`)
            const files = await ApiService.getFiles()
            // console.log('All files:', files)

            const processingFile = files.find((f) => f.id === fileId)
            // console.log(`Found processing file:`, processingFile)

            if (!processingFile) {
              console.log(`File ${fileId} not found in poll response`)
              clearInterval(pollInterval)
              this.processingFiles.delete(fileId)
              return
            }

            // console.log(`File status: ${processingFile.status}`)
            // console.log(`Completed size: ${processingFile.completed_size}`)
            // console.log(`Time remaining: ${processingFile.time_remaining}`)

            if (processingFile.status === 'in-progress') {
              const progress = {
                completedSize: processingFile.completed_size || 0,
                totalSize: processingFile.extracted_size || processingFile.file_size,
                timeRemaining: processingFile.time_remaining || 0,
              }
              console.log(`Setting progress for ${fileId}:`, progress)
              this.processingFiles.set(fileId, progress)
            } else if (processingFile.status === 'done') {
              console.log(`Processing complete for ${fileId}`)
              clearInterval(pollInterval)
              this.processingFiles.delete(fileId)
              await this.fetchFiles()
              return
            }
          } catch (error) {
            console.error('Failed to get processing status:', error)
            clearInterval(pollInterval)
            this.processingFiles.delete(fileId)
          }
        }, 1000) // Poll every 2000ms for smoother updates
      } catch (error) {
        console.error('Failed to process file:', error)
        this.processingFiles.delete(fileId)
        throw error
      }
    },

    async processFileWithProduct(fileId, productId) {
      try {
        const file = this.uploads.find((f) => f.id === fileId)
        if (!file) {
          console.log(`File ${fileId} not found in uploads`)
          return
        }

        console.log(`Starting process for file with product:`, file, productId)

        // Initialize processing status
        this.processingFiles.set(fileId, {
          completedSize: 0,
          totalSize: file.extracted_size || file.file_size,
          timeRemaining: 0,
        })

        // Start processing in background with product ID
        ApiService.processFileWithProduct(fileId, productId).catch((error) => {
          console.error('Process request failed:', error)
        })

        // Start polling for progress immediately
        const pollInterval = setInterval(async () => {
          try {
            console.log(`Polling for file ${fileId} status...`)
            const files = await ApiService.getFiles()
            // console.log('All files:', files)

            const processingFile = files.find((f) => f.id === fileId)
            // console.log(`Found processing file:`, processingFile)

            if (!processingFile) {
              console.log(`File ${fileId} not found in poll response`)
              clearInterval(pollInterval)
              this.processingFiles.delete(fileId)
              return
            }

            // console.log(`File status: ${processingFile.status}`)
            // console.log(`Completed size: ${processingFile.completed_size}`)
            // console.log(`Time remaining: ${processingFile.time_remaining}`)

            if (processingFile.status === 'in-progress') {
              const progress = {
                completedSize: processingFile.completed_size || 0,
                totalSize: processingFile.extracted_size || processingFile.file_size,
                timeRemaining: processingFile.time_remaining || 0,
              }
              console.log(`Setting progress for ${fileId}:`, progress)
              this.processingFiles.set(fileId, progress)
            } else if (processingFile.status === 'done') {
              console.log(`Processing complete for ${fileId}`)
              clearInterval(pollInterval)
              this.processingFiles.delete(fileId)
              await this.fetchFiles()
              return
            }
          } catch (error) {
            console.error('Failed to get processing status:', error)
            clearInterval(pollInterval)
            this.processingFiles.delete(fileId)
          }
        }, 1000) // Poll every 1000ms for smoother updates
      } catch (error) {
        console.error('Failed to process file with product:', error)
        this.processingFiles.delete(fileId)
        throw error
      }
    },

    async deleteFile(fileId) {
      try {
        await ApiService.deleteFile(fileId)
        // Remove file from both uploads and processed arrays
        this.uploads = this.uploads.filter((f) => f.id !== fileId)
        this.processed = this.processed.filter((f) => f.id !== fileId)
      } catch (error) {
        console.error('Failed to delete file:', error)
        throw error
      }
    },

    async deleteAllFiles() {
      try {
        await ApiService.deleteAllFiles()
        this.uploads = []
        this.processed = []
        this.processingFiles.clear()
        this.uploadProgress.clear()
      } catch (error) {
        throw error
      }
    },

    async downloadFile(fileId) {
      try {
        return await ApiService.downloadFile(fileId)
      } catch (error) {
        console.error('Failed to download file:', error)
        throw error
      }
    },
  },
})
