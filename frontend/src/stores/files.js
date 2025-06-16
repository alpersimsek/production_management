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
