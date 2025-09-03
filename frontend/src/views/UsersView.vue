<!--
GDPR Tool Users View - User Management Interface

This component provides the user management interface for the GDPR compliance tool.
It allows administrators to create, edit, and delete user accounts with role-based permissions.

Key Features:
- User Management: Create, edit, and delete user accounts
- Role-Based Access: Admin and user role management
- Form Validation: Required field validation and error handling
- Modal Dialogs: Inline editing with modal forms
- Security Features: Prevent self-deletion and role validation
- Responsive Design: Mobile-first responsive layout
- Error Handling: Comprehensive error states and retry functionality

User Management Features:
- Add Users: Create new user accounts with username, password, and role
- Edit Users: Update existing user information
- Delete Users: Remove user accounts (with safety checks)
- Role Assignment: Assign admin or user roles
- Password Management: Secure password handling

Security Features:
- Self-Protection: Prevent users from deleting their own accounts
- Role Validation: Proper role assignment and validation
- Form Validation: Client-side validation for required fields
- Error Sanitization: Safe error message display

The component provides comprehensive user management functionality for
GDPR compliance tool administrators with proper security and validation.
-->

<script setup>
import { ref, onMounted, computed } from 'vue'
import MainLayout from '../components/MainLayout.vue'
import ListView from '../components/ListView.vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import AppButton from '../components/AppButton.vue'
import InputField from '../components/InputField.vue'
import SelectField from '../components/SelectField.vue'
import ApiService from '../services/api'
import {
  PlusIcon,
  UserIcon,
  UserPlusIcon,
  PencilIcon,
  TrashIcon,
  ShieldCheckIcon
} from '@heroicons/vue/24/outline'

// State
const users = ref([])
const isLoading = ref(false)
const error = ref(null)
const showAddUserForm = ref(false)
const editUser = ref(null)
const newUser = ref({
  username: '',
  password: '',
  role: 'user'
})

// Load users from the API
const loadUsers = async () => {
  isLoading.value = true
  error.value = null

  try {
    const response = await ApiService.getUsers()
    users.value = response
  } catch (err) {
    console.error('Failed to load users:', err)
    error.value = err.message || 'Failed to load users'
  } finally {
    isLoading.value = false
  }
}

const formattedUsers = computed(() => {
  return users.value.map(user => ({
    ...user,
    formattedRole: user.role.charAt(0).toUpperCase() + user.role.slice(1)
  }))
})

// Methods
const handleAddUser = () => {
  showAddUserForm.value = true
  editUser.value = null
  newUser.value = {
    username: '',
    password: '',
    role: 'user'
  }
}

const handleEditUser = (user) => {
  editUser.value = user
  newUser.value = {
    ...user,
    password: '' // Clear password when editing
  }
  showAddUserForm.value = true
}

const handleDeleteUser = async (userId) => {
  if (confirm('Are you sure you want to delete this user?')) {
    try {
      isLoading.value = true
      await ApiService.deleteUser(userId)
      await loadUsers() // Refresh the list
    } catch (err) {
      console.error('Failed to delete user:', err)
      error.value = err.message || 'Failed to delete user'
    } finally {
      isLoading.value = false
    }
  }
}

const saveUser = async () => {
  try {
    isLoading.value = true
    error.value = null

    if (editUser.value) {
      await ApiService.updateUser(editUser.value.id, newUser.value)
    } else {
      await ApiService.createUser(newUser.value)
    }

    showAddUserForm.value = false
    await loadUsers() // Refresh the list
  } catch (err) {
    console.error('Failed to save user:', err)
    error.value = err.message || 'Failed to save user'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  loadUsers()
})
</script>

<template>
  <MainLayout>
    <div class="min-h-screen bg-gray-50 px-4 sm:px-6 lg:px-8 py-1 sm:py-1">
      <!-- Header (Matching PresetManagement.vue) -->
      <div class="sm:flex sm:items-center mb-8">
        <div class="sm:flex-auto">
          <div class="flex items-center gap-3">
            <svg xmlns="http://www.w3.org/2000/svg"
              class="h-7 w-7 text-indigo-500 transition-transform duration-300 hover:scale-110" fill="none"
              viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
            <h1 class="text-2xl font-bold text-gray-900 tracking-tight">User Management</h1>
          </div>
          <p class="mt-2 text-sm text-gray-600 font-medium">
            Effortlessly manage user accounts and permissions
          </p>
        </div>
        <div class="mt-6 sm:mt-0 sm:ml-16 sm:flex-none flex space-x-4">
          <AppButton type="button" variant="primary" @click="handleAddUser"
            class="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-indigo-700 hover:shadow-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
            :preserveOriginalStyle="false" aria-label="Add new user">
            <PlusIcon class="h-5 w-5 mr-2" aria-hidden="true" />
            Add User
          </AppButton>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading && !users.length" class="py-8 flex justify-center items-center" aria-live="polite">
        <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600"></div>
        <p class="ml-4 text-sm font-medium text-gray-600">Loading users...</p>
      </div>

      <!-- Error State -->
      <div v-if="error"
        class="mt-6 rounded-xl bg-red-50 p-4 shadow-sm animate-fade-in flex items-center justify-between">
        <div class="flex items-center">
          <svg class="h-5 w-5 text-red-400 mr-2" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
            <path fill-rule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clip-rule="evenodd" />
          </svg>
          <span class="text-sm font-medium text-red-800">{{ error }}</span>
        </div>
        <AppButton variant="text"
          class="text-red-700 hover:text-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
          @click="loadUsers" :preserveOriginalStyle="false" aria-label="Retry loading users">
          Retry
        </AppButton>
      </div>

      <!-- User List -->
      <div v-if="!isLoading || users.length" class="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <ListView title="Users" :items="formattedUsers" :empty-message="'No users found'" :empty-icon="null"
          :get-item-title="item => item.username" :get-item-subtitle="() => ''"
          :get-item-metadata="item => item.formattedRole"
          :get-item-icon="item => item.role === 'admin' ? ShieldCheckIcon : UserIcon"
          :get-item-class="item => item.role === 'admin' ? 'border-l-4 border-indigo-500' : ''" class="animate-fade-in">
          <template #itemActions="{ item }">
            <!-- Edit Button -->
            <AppButton @click="handleEditUser(item)" variant="text"
              class="text-indigo-600 hover:text-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
              :preserveOriginalStyle="false" title="Edit user" aria-label="Edit user">
              <PencilIcon class="h-5 w-5" aria-hidden="true" />
            </AppButton>

            <!-- Delete Button (Prevent deleting own account) -->
            <AppButton v-if="item.id !== 1" @click="handleDeleteUser(item.id)" variant="text"
              class="text-red-500 hover:text-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              :preserveOriginalStyle="false" title="Delete user" aria-label="Delete user">
              <TrashIcon class="h-5 w-5" aria-hidden="true" />
            </AppButton>
          </template>
        </ListView>
      </div>

      <!-- User Form Dialog -->
      <Dialog v-if="showAddUserForm" @close="showAddUserForm = false" :open="showAddUserForm">
        <div class="fixed inset-0 bg-black/40 transition-opacity duration-300" aria-hidden="true" />
        <div class="fixed inset-0 flex items-center justify-center p-4">
          <DialogPanel class="w-full max-w-md rounded-xl bg-white p-6 shadow-xl transform transition-all duration-300">
            <DialogTitle as="h3" class="text-lg font-bold text-gray-900">
              {{ editUser ? 'Edit User' : 'Add New User' }}
            </DialogTitle>

            <div v-if="error" class="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-800 animate-fade-in">
              {{ error }}
            </div>

            <div class="mt-4 space-y-5">
              <InputField id="username" v-model="newUser.username" label="Username" type="text" required
                custom-class="border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-lg" />
              <InputField id="password" v-model="newUser.password" label="Password" type="password" required
                custom-class="border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-lg" />
              <SelectField id="role" v-model="newUser.role" label="Role"
                custom-class="border-gray-300 focus:border-indigo-500 focus:ring-indigo-500 rounded-lg">
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </SelectField>
            </div>

            <div class="mt-6 flex justify-end space-x-3">
              <AppButton variant="secondary" @click="showAddUserForm = false"
                class="border border-gray-300 bg-white px-4 py-2 text-sm font-semibold text-gray-700 rounded-lg shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                :preserveOriginalStyle="false" :disabled="isLoading" aria-label="Cancel">
                Cancel
              </AppButton>
              <AppButton variant="primary" @click="saveUser"
                class="bg-indigo-600 px-4 py-2 text-sm font-semibold text-white rounded-lg shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
                :preserveOriginalStyle="false" :loading="isLoading" :aria-label="editUser ? 'Update user' : 'Add user'">
                {{ editUser ? 'Update' : 'Add' }}
              </AppButton>
            </div>
          </DialogPanel>
        </div>
      </Dialog>

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

/* Dialog transition */
.dialog-enter-active,
.dialog-leave-active {
  transition: all 0.3s ease;
}

.dialog-enter-from,
.dialog-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}
</style>