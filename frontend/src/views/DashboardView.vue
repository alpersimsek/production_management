<script setup>
import { onMounted } from 'vue'
import { useFilesStore } from '../stores/files'
import { useAuthStore } from '../stores/auth'
import MainLayout from '../components/MainLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import ExpandableCard from '../components/ExpandableCard.vue'
import ActionCard from '../components/ActionCard.vue'
import {
  DocumentIcon,
  DocumentCheckIcon,
  UserGroupIcon,
} from '@heroicons/vue/24/outline'

const filesStore = useFilesStore()
const authStore = useAuthStore()

onMounted(async () => {
  await filesStore.fetchFiles()
})

// Utility functions that would normally be in a composable
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
  <MainLayout>
    <div class="px-4 sm:px-6 lg:px-8">
      <PageHeader :title="`Welcome back, ${authStore.user?.username.charAt(0).toUpperCase() + authStore.user?.username.slice(1) || ''}`" />

      <div class="mt-8">
        <div class="grid grid-cols-1 gap-5 sm:grid-cols-2">
          <!-- Uploads Card -->
          <ExpandableCard
            title="Uploads"
            :icon="DocumentIcon"
            :count="filesStore.uploads.length"
          >
            <template #content>
              <div class="space-y-4">
                <div
                  v-for="file in filesStore.uploads"
                  :key="file.id"
                  class="flex items-center justify-between"
                >
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ file.filename }}</p>
                    <p class="text-sm text-gray-500">{{ formatDate(file.create_date) }}</p>
                  </div>
                  <span class="text-sm text-gray-500">{{ formatFileSize(file.file_size) }}</span>
                </div>
              </div>
            </template>
          </ExpandableCard>

          <!-- Processed Files Card -->
          <ExpandableCard
            title="Processed Files"
            :icon="DocumentCheckIcon"
            :count="filesStore.processed.length"
          >
            <template #content>
              <div class="space-y-4">
                <div
                  v-for="file in filesStore.processed"
                  :key="file.id"
                  class="flex items-center justify-between"
                >
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ file.filename }}</p>
                    <p class="text-sm text-gray-500">{{ formatDate(file.create_date) }}</p>
                  </div>
                  <span class="text-sm text-gray-500">{{ formatFileSize(file.file_size) }}</span>
                </div>
              </div>
            </template>
          </ExpandableCard>
        </div>
      </div>

      <div class="mt-8 grid grid-cols-1 gap-5 sm:grid-cols-2">
        <!-- User Management Card (Admin Only) -->
        <ActionCard
          v-if="authStore.isAdmin"
          title="User Management"
          description="Manage system users and their permissions"
          :icon="UserGroupIcon"
          link-to="/users"
          link-text="View all users"
        />

        <!-- File Management Card -->
        <ActionCard
          title="File Management"
          description="Upload and process files for GDPR compliance"
          :icon="DocumentIcon"
          link-to="/files"
          link-text="Manage files"
          :custom-class="!authStore.isAdmin ? 'sm:col-span-2' : ''"
        />
      </div>
    </div>
  </MainLayout>
</template>
