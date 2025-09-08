/**
 * Global Error Handler Composable
 * 
 * This composable provides centralized error handling for the GDPR tool frontend.
 * It categorizes errors, formats them for display, and manages error state.
 * 
 * Key Features:
 * - Error Categorization: Automatically categorizes errors by type
 * - Error Formatting: Formats errors for user-friendly display
 * - Error State Management: Centralized error state management
 * - Retry Functionality: Built-in retry mechanism for failed operations
 * - Error Logging: Optional error logging for debugging
 * 
 * Error Types:
 * - network: Network connectivity issues
 * - server: Server-side errors (5xx)
 * - validation: Client-side validation errors (4xx)
 * - auth: Authentication/authorization errors (401, 403)
 * - file: File processing errors
 * - unknown: Generic errors
 * 
 * Usage:
 * ```javascript
 * import { useErrorHandler } from '@/composables/useErrorHandler'
 * 
 * const { handleError, clearError, error, showErrorModal } = useErrorHandler()
 * 
 * // Handle an error
 * handleError(new Error('Something went wrong'), { type: 'server' })
 * 
 * // Clear error
 * clearError()
 * ```
 */

import { ref, reactive } from 'vue'

const globalError = reactive({
  isVisible: false,
  type: 'unknown',
  message: '',
  details: null,
  status: null,
  timestamp: null,
  retryAction: null
})

export function useErrorHandler() {
  const showErrorModal = ref(false)

  const categorizeError = (error, context = {}) => {
    // Check for network errors
    if (!navigator.onLine) {
      return {
        type: 'network',
        message: 'No internet connection. Please check your network and try again.',
        details: 'Network connectivity issue detected'
      }
    }

    // Check for API errors
    if (error.response) {
      const status = error.response.status
      const data = error.response.data

      if (status >= 500) {
        return {
          type: 'server',
          message: data?.detail || data?.message || 'Server error occurred',
          details: data,
          status: status
        }
      }

      if (status === 401) {
        return {
          type: 'auth',
          message: 'Your session has expired. Please log in again.',
          details: data,
          status: status
        }
      }

      if (status === 403) {
        return {
          type: 'auth',
          message: 'You do not have permission to perform this action.',
          details: data,
          status: status
        }
      }

      if (status >= 400 && status < 500) {
        return {
          type: 'validation',
          message: data?.detail || data?.message || 'Invalid request',
          details: data,
          status: status
        }
      }
    }

    // Check for file processing errors
    if (context.type === 'file' || error.message?.includes('file') || error.message?.includes('upload')) {
      return {
        type: 'file',
        message: error.message || 'File processing error occurred',
        details: error.details || error.stack
      }
    }

    // Check for specific error patterns
    if (error.message?.includes('preset') || error.message?.includes('no assigned preset')) {
      return {
        type: 'file',
        message: 'File processing failed: No preset assigned to this file type.',
        details: error.message
      }
    }

    if (error.message?.includes('timeout')) {
      return {
        type: 'network',
        message: 'Request timed out. Please try again.',
        details: error.message
      }
    }

    // Default to unknown error
    return {
      type: 'unknown',
      message: error.message || 'An unexpected error occurred',
      details: error.stack || error.details
    }
  }

  const formatErrorMessage = (error, context = {}) => {
    const categorized = categorizeError(error, context)
    
    return {
      type: categorized.type,
      message: categorized.message,
      details: categorized.details,
      status: categorized.status,
      timestamp: new Date().toISOString()
    }
  }

  const handleError = (error, context = {}) => {
    console.error('Error handled:', error, context)
    
    const formattedError = formatErrorMessage(error, context)
    
    // Update global error state
    Object.assign(globalError, {
      isVisible: true,
      ...formattedError,
      retryAction: context.retryAction || null,
      cancelAction: context.cancelAction || null
    })
    
    showErrorModal.value = true
  }

  const clearError = () => {
    Object.assign(globalError, {
      isVisible: false,
      type: 'unknown',
      message: '',
      details: null,
      status: null,
      timestamp: null,
      retryAction: null,
      cancelAction: null
    })
    showErrorModal.value = false
  }

  const handleRetry = () => {
    if (globalError.retryAction) {
      globalError.retryAction()
    }
    clearError()
  }

  const handleDismiss = () => {
    clearError()
  }

  const handleCancel = () => {
    if (globalError.cancelAction) {
      globalError.cancelAction()
    }
    clearError()
  }

  return {
    error: globalError,
    showErrorModal,
    handleError,
    clearError,
    handleRetry,
    handleDismiss,
    handleCancel,
    categorizeError,
    formatErrorMessage
  }
}

// Global error handler instance
export const globalErrorHandler = useErrorHandler()
