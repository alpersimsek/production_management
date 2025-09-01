<!--
GDPR Tool Dashboard Expandable Card - Dashboard-Specific Card Component

This component provides a specialized expandable card component for the GDPR compliance tool dashboard.
It displays file lists with counts and allows expansion to show detailed file information.

Key Features:
- Dashboard Integration: Specialized for dashboard file display
- File List Display: Shows file items with metadata
- Expandable Content: Toggle between collapsed and expanded states
- File Information: Displays filename, date, and file size
- Icon Support: Required icon display for visual identification
- Count Display: Shows total count of items
- Utility Functions: Built-in date and file size formatting

Props:
- title: Card title (required)
- icon: Icon component (required)
- items: Array of file items to display (required)
- count: Total count of items (required)
- initialExpanded: Initial expansion state (default: false)

Features:
- File Metadata: Displays filename, creation date, and file size
- Responsive Design: Mobile-first responsive layout
- Smooth Animations: Expandable content with smooth transitions
- Utility Formatting: Built-in date and file size formatters

The component provides a specialized dashboard card interface for displaying
file lists with expandable content and proper formatting for the GDPR tool.
-->

<script setup>
import { ref } from 'vue'
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/vue/24/outline'

defineProps({
  title: {
    type: String,
    required: true
  },
  icon: {
    type: Object,
    required: true
  },
  items: {
    type: Array,
    required: true
  },
  count: {
    type: Number,
    required: true
  },
  initialExpanded: {
    type: Boolean,
    default: false
  }
})

const expanded = ref(false)

const toggleExpanded = () => {
  expanded.value = !expanded.value
}

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
</script>

<template>
  <div class="relative overflow-hidden rounded-lg bg-white shadow">
    <div class="px-4 pb-5 pt-5 sm:px-6 sm:pt-6">
      <button @click="toggleExpanded" class="w-full">
        <div class="relative">
          <div class="absolute rounded-md bg-primary p-3">
            <component :is="icon" class="h-6 w-6 text-white" aria-hidden="true" />
          </div>
          <div class="flex items-center justify-between">
            <p class="ml-16 truncate text-sm font-medium text-gray-500">{{ title }}</p>
            <component
              :is="expanded ? ChevronUpIcon : ChevronDownIcon"
              class="h-5 w-5 text-gray-400"
            />
          </div>
          <div class="ml-16 flex items-baseline pb-6 sm:pb-7">
            <p class="text-2xl font-semibold text-gray-900">
              {{ count }}
            </p>
          </div>
        </div>
      </button>
      <div v-if="expanded" class="mt-4 border-t pt-4">
        <div class="space-y-4">
          <div
            v-for="item in items"
            :key="item.id"
            class="flex items-center justify-between"
          >
            <div>
              <p class="text-sm font-medium text-gray-900">{{ item.filename }}</p>
              <p class="text-sm text-gray-500">{{ formatDate(item.create_date) }}</p>
            </div>
            <span class="text-sm text-gray-500">{{ formatFileSize(item.file_size) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
