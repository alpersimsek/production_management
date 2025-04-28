<script setup>
import AppNavbar from './NavBar.vue'
</script>

<template>
  <div class="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
    <div class="shadow-sm">
      <AppNavbar />
    </div>
    <div class="py-8 sm:py-12">
      <main>
        <div class="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <slot></slot>
        </div>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* Smooth gradient transition */
.bg-gradient-to-b {
  transition: background-color 0.5s ease-in-out;
}
</style>