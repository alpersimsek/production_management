/**
 * Notification Manager Composable
 * 
 * This composable provides a centralized notification system for the GDPR tool frontend.
 * It manages toast notifications with different types, positions, and auto-dismiss functionality.
 * 
 * Key Features:
 * - Multiple Toast Support: Stack multiple notifications simultaneously
 * - Type Management: Success, info, warning, and error notifications
 * - Position Control: Top/bottom, left/right positioning
 * - Auto Dismiss: Configurable auto-dismiss duration
 * - Manual Control: Programmatic show/hide/dismiss functionality
 * - Queue Management: Automatic queue management for multiple notifications
 * 
 * Notification Types:
 * - success: Success messages (green)
 * - info: Information messages (blue)
 * - warning: Warning messages (yellow)
 * - error: Error messages (red)
 * 
 * Usage:
 * ```javascript
 * import { useNotifications } from '@/composables/useNotifications'
 * 
 * const { showSuccess, showError, showWarning, showInfo, notifications, dismiss } = useNotifications()
 * 
 * // Show a success message
 * showSuccess('File uploaded successfully!')
 * 
 * // Show an error with custom duration
 * showError('Upload failed', { duration: 10000 })
 * 
 * // Show info with title
 * showInfo('Processing started', { title: 'File Processing' })
 * ```
 */

import { ref, reactive } from 'vue'

// Global notification state
const notifications = ref([])
let nextId = 1

export function useNotifications() {
  const showNotification = (type, message, options = {}) => {
    const {
      title = '',
      duration = type === 'error' ? 8000 : 5000, // Errors stay longer
      position = 'top-right',
      persistent = false
    } = options

    const notification = {
      id: nextId++,
      type,
      title,
      message,
      duration: persistent ? 0 : duration,
      position,
      open: true,
      timestamp: Date.now()
    }

    notifications.value.push(notification)

    // Auto-remove after duration (if not persistent)
    if (!persistent && duration > 0) {
      setTimeout(() => {
        dismiss(notification.id)
      }, duration)
    }

    return notification.id
  }

  const showSuccess = (message, options = {}) => {
    return showNotification('success', message, { ...options, title: options.title || 'Success' })
  }

  const showInfo = (message, options = {}) => {
    return showNotification('info', message, { ...options, title: options.title || 'Information' })
  }

  const showWarning = (message, options = {}) => {
    return showNotification('warning', message, { ...options, title: options.title || 'Warning' })
  }

  const showError = (message, options = {}) => {
    return showNotification('error', message, { ...options, title: options.title || 'Error' })
  }

  const dismiss = (id) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const dismissAll = () => {
    notifications.value = []
  }

  const dismissByType = (type) => {
    notifications.value = notifications.value.filter(n => n.type !== type)
  }

  const getNotificationsByPosition = (position) => {
    return notifications.value.filter(n => n.position === position)
  }

  const getNotificationsByType = (type) => {
    return notifications.value.filter(n => n.type === type)
  }

  const hasNotifications = () => {
    return notifications.value.length > 0
  }

  const hasNotificationsByType = (type) => {
    return notifications.value.some(n => n.type === type)
  }

  const hasNotificationsByPosition = (position) => {
    return notifications.value.some(n => n.position === position)
  }

  // Convenience methods for common scenarios
  const showLoginExpired = () => {
    return showError('Your session has expired. Please log in again.', {
      title: 'Session Expired',
      duration: 0, // Persistent until manually dismissed
      position: 'top-center'
    })
  }

  const showFileUploaded = (filename) => {
    return showSuccess(`File "${filename}" uploaded successfully!`, {
      title: 'Upload Complete'
    })
  }

  const showFileDeleted = (filename) => {
    return showSuccess(`File "${filename}" deleted successfully!`, {
      title: 'File Deleted'
    })
  }

  const showFileProcessingStarted = (filename) => {
    return showInfo(`Processing "${filename}"...`, {
      title: 'Processing Started'
    })
  }

  const showFileProcessingComplete = (filename) => {
    return showSuccess(`File "${filename}" processed successfully!`, {
      title: 'Processing Complete'
    })
  }

  const showFileProcessingError = (filename, error) => {
    return showError(`Failed to process "${filename}": ${error}`, {
      title: 'Processing Failed',
      duration: 10000
    })
  }

  const showUserCreated = (username) => {
    return showSuccess(`User "${username}" created successfully!`, {
      title: 'User Created'
    })
  }

  const showUserDeleted = (username) => {
    return showSuccess(`User "${username}" deleted successfully!`, {
      title: 'User Deleted'
    })
  }

  const showPresetCreated = (presetName) => {
    return showSuccess(`Preset "${presetName}" created successfully!`, {
      title: 'Preset Created'
    })
  }

  const showPresetDeleted = (presetName) => {
    return showSuccess(`Preset "${presetName}" deleted successfully!`, {
      title: 'Preset Deleted'
    })
  }

  const showNetworkError = () => {
    return showError('Network connection failed. Please check your internet connection and try again.', {
      title: 'Connection Error',
      duration: 10000
    })
  }

  const showServerError = (message = 'Server error occurred. Please try again later.') => {
    return showError(message, {
      title: 'Server Error',
      duration: 10000
    })
  }

  const showValidationError = (message) => {
    return showWarning(message, {
      title: 'Validation Error',
      duration: 7000
    })
  }

  return {
    // State
    notifications,
    
    // Core methods
    showNotification,
    showSuccess,
    showInfo,
    showWarning,
    showError,
    dismiss,
    dismissAll,
    dismissByType,
    
    // Query methods
    getNotificationsByPosition,
    getNotificationsByType,
    hasNotifications,
    hasNotificationsByType,
    hasNotificationsByPosition,
    
    // Convenience methods
    showLoginExpired,
    showFileUploaded,
    showFileDeleted,
    showFileProcessingStarted,
    showFileProcessingComplete,
    showFileProcessingError,
    showUserCreated,
    showUserDeleted,
    showPresetCreated,
    showPresetDeleted,
    showNetworkError,
    showServerError,
    showValidationError
  }
}

// Global notification manager instance
export const globalNotifications = useNotifications()
