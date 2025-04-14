<script setup>
import { onMounted } from 'vue'
import { useAuthStore } from './stores/auth'

const authStore = useAuthStore()

onMounted(() => {
  authStore.setAuth()
})
</script>

<template>
  <RouterView />
</template>

<style></style>
