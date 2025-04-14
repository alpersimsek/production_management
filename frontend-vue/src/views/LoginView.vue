<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import InputField from '../components/InputField.vue'
import AppButton from '../components/AppButton.vue'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const isLoading = ref(false)

const handleSubmit = async () => {
  try {
    error.value = ''
    isLoading.value = true
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50">
    <div class="w-full max-w-sm space-y-6">
      <h1 class="text-2xl font-bold text-center text-gray-900">Sign in to your account</h1>
      <form class="space-y-4" @submit.prevent="handleSubmit">
        <InputField
          id="username"
          v-model="username"
          label="Username"
          type="text"
          required
          :error="error ? '' : undefined"
        />

        <InputField
          id="password"
          v-model="password"
          label="Password"
          type="password"
          required
          :error="error ? '' : undefined"
        />

        <div v-if="error" class="text-red-600 text-sm text-center">
          {{ error }}
        </div>

        <AppButton
          type="submit"
          variant="primary"
          :loading="isLoading"
          class="w-full"
        >
          Sign in
        </AppButton>
      </form>
    </div>
  </div>
</template>
