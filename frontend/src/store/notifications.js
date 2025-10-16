import { defineStore } from 'pinia'
import api from '@/services/api'

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    notifications: [],
    unreadCount: 0,
    loading: false,
    error: null
  }),

  getters: {
    unreadNotifications: (state) => state.notifications.filter(n => !n.is_read),
    recentNotifications: (state) => state.notifications.slice(0, 5)
  },

  actions: {
    async fetchNotifications (unreadOnly = false) {
      this.loading = true
      this.error = null

      try {
        const params = unreadOnly ? { unread_only: true } : {}
        const response = await api.get('/notifications/', { params })
        this.notifications = response.data
      } catch (error) {
        this.error = error.response?.data?.detail || 'Failed to fetch notifications'
        console.error('Error fetching notifications:', error)
      } finally {
        this.loading = false
      }
    },

    async fetchUnreadCount () {
      try {
        const response = await api.get('/notifications/unread-count')
        this.unreadCount = response.data.unread_count
      } catch (error) {
        console.error('Error fetching unread count:', error)
      }
    },

    async markAsRead (notificationId) {
      try {
        await api.put(`/notifications/${notificationId}`, { is_read: true })

        // Update local state
        const notification = this.notifications.find(n => n.id === notificationId)
        if (notification) {
          notification.is_read = true
          notification.read_at = new Date().toISOString()
          this.unreadCount = Math.max(0, this.unreadCount - 1)
        }
      } catch (error) {
        console.error('Error marking notification as read:', error)
      }
    },

    async markAllAsRead () {
      try {
        await api.post('/notifications/mark-all-read')

        // Update local state
        this.notifications.forEach(notification => {
          if (!notification.is_read) {
            notification.is_read = true
            notification.read_at = new Date().toISOString()
          }
        })
        this.unreadCount = 0
      } catch (error) {
        console.error('Error marking all notifications as read:', error)
      }
    },

    async deleteNotification (notificationId) {
      try {
        await api.delete(`/notifications/${notificationId}`)

        // Update local state
        const notification = this.notifications.find(n => n.id === notificationId)
        if (notification && !notification.is_read) {
          this.unreadCount = Math.max(0, this.unreadCount - 1)
        }
        this.notifications = this.notifications.filter(n => n.id !== notificationId)
      } catch (error) {
        console.error('Error deleting notification:', error)
      }
    },

    async createNotification (notificationData) {
      try {
        const response = await api.post('/notifications/', notificationData)
        this.notifications.unshift(response.data)
        if (!response.data.is_read) {
          this.unreadCount++
        }
        return response.data
      } catch (error) {
        console.error('Error creating notification:', error)
        throw error
      }
    },

    // Real-time notification handling
    addNotification (notification) {
      this.notifications.unshift(notification)
      if (!notification.is_read) {
        this.unreadCount++
      }
    },

    // Initialize notifications
    async initialize () {
      await Promise.all([
        this.fetchNotifications(),
        this.fetchUnreadCount()
      ])
    }
  }
})
