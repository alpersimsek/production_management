<template>
  <div class="language-switcher">
    <select
      :value="currentLanguage"
      @change="changeLanguage"
      class="bg-primary-600 text-white text-sm rounded px-2 py-1 border-0 focus:outline-none focus:ring-2 focus:ring-primary-300"
    >
      <option value="en">🇺🇸 English</option>
      <option value="tr">🇹🇷 Türkçe</option>
    </select>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const currentLanguage = computed(() => locale.value)

function changeLanguage (event) {
  const newLanguage = event.target.value
  locale.value = newLanguage
  localStorage.setItem('app-language', newLanguage)

  // Emit event to notify other components
  window.dispatchEvent(new CustomEvent('language-changed', {
    detail: { language: newLanguage }
  }))
}
</script>

<style scoped>
.language-switcher select {
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
  background-position: right 0.5rem center;
  background-repeat: no-repeat;
  background-size: 1.5em 1.5em;
  padding-right: 2.5rem;
}
</style>
