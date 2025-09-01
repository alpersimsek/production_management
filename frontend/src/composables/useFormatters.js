/**
 * Composable providing utility formatting functions for the GDPR tool frontend
 * 
 * This composable provides reusable formatting utilities that can be imported
 * and used across Vue components. It includes functions for formatting file sizes,
 * dates, and time durations in a user-friendly manner.
 * 
 * Key Features:
 * - File size formatting (bytes to human-readable format like KB, MB, GB)
 * - Date formatting (ISO strings to locale-specific format)
 * - Time remaining formatting (seconds to minutes and seconds)
 * 
 * Usage:
 * ```javascript
 * import { useFormatters } from '@/composables/useFormatters'
 * 
 * const { formatFileSize, formatDate, formatTimeRemaining } = useFormatters()
 * ```
 * 
 * Functions:
 * - formatFileSize(bytes): Converts bytes to human-readable format (B, KB, MB, GB)
 * - formatDate(dateString): Converts ISO date string to locale string
 * - formatTimeRemaining(seconds): Formats seconds as "Xm Ys" or "Xs"
 */
export function useFormatters() {
  /**
   * Format file size in bytes to human-readable format
   * @param {number} bytes - File size in bytes
   * @returns {string} Formatted file size
   */
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`
  }

  /**
   * Format date string to locale string
   * @param {string} dateString - ISO date string
   * @returns {string} Formatted date
   */
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString()
  }

  /**
   * Format seconds to minutes and seconds
   * @param {number} seconds - Time in seconds
   * @returns {string} Formatted time
   */
  const formatTimeRemaining = (seconds) => {
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  return {
    formatFileSize,
    formatDate,
    formatTimeRemaining
  }
}
