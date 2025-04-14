<template>
  <div class="overflow-hidden rounded-lg bg-white shadow" :class="customClass">
    <div class="p-6">
      <div class="flex items-center">
        <div class="flex-shrink-0">
          <component :is="icon" class="h-6 w-6 text-gray-400" aria-hidden="true" />
        </div>
        <div class="ml-3 w-0 flex-1">
          <h3 class="text-base font-semibold text-gray-900">{{ title }}</h3>
          <p class="mt-1 text-sm text-gray-500">{{ description }}</p>
        </div>
      </div>
      <div class="mt-6">
        <router-link
          :to="linkTo"
          class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-primary shadow-sm ring-1 ring-inset ring-primary hover:bg-gray-50"
        >
          {{ linkText }}
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  icon: {
    type: Object,
    required: true
  },
  linkTo: {
    type: String,
    required: true
  },
  linkText: {
    type: String,
    required: true
  },
  customClass: {
    type: String,
    default: ''
  }
})
</script>
