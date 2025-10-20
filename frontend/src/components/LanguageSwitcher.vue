<template>
  <div class="language-switcher">
    <!-- Mobile: Icon Only -->
    <select
      :value="currentLanguage"
      @change="changeLanguage"
      class="lg:hidden bg-transparent text-secondary-600 text-sm rounded px-1 py-1 border-0 focus:outline-none focus:ring-2 focus:ring-primary-300 w-8 h-8 flex items-center justify-center"
    >
      <option value="en">🇺🇸</option>
      <option value="tr">🇹🇷</option>
    </select>

    <!-- Desktop: Full Text -->
    <select
      :value="currentLanguage"
      @change="changeLanguage"
      class="hidden lg:block bg-primary-600 text-white text-sm rounded px-2 py-1 border-0 focus:outline-none focus:ring-2 focus:ring-primary-300"
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

/* Mobile icon-only style */
.language-switcher select.lg\:hidden {
  background-image: none;
  padding-right: 0.25rem;
  padding-left: 0.25rem;
  font-size: 1rem;
}
</style>
