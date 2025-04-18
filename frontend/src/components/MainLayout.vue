<script setup>
import AppNavbar from './NavBar.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50">
    <AppNavbar />

    <div class="py-10">
      <main>
        <div class="mx-auto max-w-7xl sm:px-6 lg:px-8">
          <slot></slot>
        </div>
      </main>
    </div>
  </div>
</template>
