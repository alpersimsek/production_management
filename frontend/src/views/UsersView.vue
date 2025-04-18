<script setup>
import { ref, onMounted, computed } from 'vue'
import MainLayout from '../components/MainLayout.vue'
import PageHeader from '../components/PageHeader.vue'
import ListView from '../components/ListView.vue'
import { Dialog, DialogPanel, DialogTitle } from '@headlessui/vue'
import AppButton from '../components/AppButton.vue'
import InputField from '../components/InputField.vue'
import SelectField from '../components/SelectField.vue'
import ApiService from '../services/api'
import {
  UserIcon,
  UserPlusIcon,
  PencilIcon,
  TrashIcon
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
    <div class="px-4 sm:px-6 lg:px-8">
      <PageHeader title="User Management" description="Manage user accounts and permissions">
        <template #actions>
          <AppButton
            type="button"
            variant="primary"
            @click="handleAddUser"
            class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
            :preserveOriginalStyle="true"
          >
            <UserPlusIcon class="h-5 w-5 mr-2" />
            Add User
          </AppButton>
        </template>
      </PageHeader>

      <!-- Loading state -->
      <div v-if="isLoading && !users.length" class="py-6 text-center text-gray-500">
        Loading users...
      </div>

      <!-- Error state -->
      <div v-if="error" class="p-4 bg-red-50 text-red-700 rounded-md mt-4">
        {{ error }}
        <AppButton
          variant="text"
          class="ml-2 text-red-700 underline"
          @click="loadUsers"
        >
          Retry
        </AppButton>
      </div>

      <!-- User list -->
      <ListView
        v-if="!isLoading || users.length"
        title="Users"
        :items="formattedUsers"
        :empty-message="'No users found'"
        :empty-icon="UserIcon"
        :get-item-title="item => item.username"
        :get-item-subtitle="() => ''"
        :get-item-metadata="item => item.formattedRole"
        :get-item-icon="() => UserIcon"
        :get-item-class="item => item.role === 'admin' ? 'border-indigo-200' : ''"
      >
        <template #itemActions="{ item }">
          <!-- Edit button -->
          <AppButton
            @click="handleEditUser(item)"
            variant="text"
            class="text-gray-400 hover:text-indigo-600 transition-colors"
            :preserveOriginalStyle="true"
            title="Edit user"
          >
            <PencilIcon class="h-5 w-5" />
          </AppButton>

          <!-- Delete button (don't allow deleting own account) -->
          <AppButton
            v-if="item.id !== 1"
            @click="handleDeleteUser(item.id)"
            variant="text"
            class="text-gray-400 hover:text-red-600 transition-colors"
            :preserveOriginalStyle="true"
            title="Delete user"
          >
            <TrashIcon class="h-5 w-5" />
          </AppButton>
        </template>
      </ListView>

      <!-- User form dialog -->
      <Dialog v-if="showAddUserForm" @close="showAddUserForm = false" :open="showAddUserForm">
        <div class="fixed inset-0 bg-black/30" aria-hidden="true" @mousedown.stop />
        <div class="fixed inset-0 flex items-center justify-center p-4">
          <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-2xl bg-white p-6 text-left align-middle shadow-xl transition-all">
            <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
              {{ editUser ? 'Edit User' : 'Add New User' }}
            </DialogTitle>

            <div v-if="error" class="mt-2 p-2 bg-red-50 text-red-700 rounded-md text-sm">
              {{ error }}
            </div>

            <div class="mt-4 space-y-4">
              <InputField
                id="username"
                v-model="newUser.username"
                label="Username"
                type="text"
                required
              />

              <InputField
                id="password"
                v-model="newUser.password"
                label="Password"
                type="password"
                required
              />

              <SelectField
                id="role"
                v-model="newUser.role"
                label="Role"
              >
                <option value="user">User</option>
                <option value="admin">Admin</option>
              </SelectField>
            </div>

            <div class="mt-6 flex justify-end space-x-3">
              <AppButton
                variant="secondary"
                @click="showAddUserForm = false"
                class="border border-gray-300 bg-white text-gray-700 shadow-sm hover:bg-gray-50 px-4 py-2 rounded-md"
                :preserveOriginalStyle="true"
                :disabled="isLoading"
              >
                Cancel
              </AppButton>
              <AppButton
                variant="primary"
                @click="saveUser"
                class="border border-transparent bg-indigo-600 text-white shadow-sm hover:bg-indigo-700 px-4 py-2 rounded-md"
                :preserveOriginalStyle="true"
                :loading="isLoading"
              >
                {{ editUser ? 'Update' : 'Add' }}
              </AppButton>
            </div>
          </DialogPanel>
        </div>
      </Dialog>
    </div>
  </MainLayout>
</template>
