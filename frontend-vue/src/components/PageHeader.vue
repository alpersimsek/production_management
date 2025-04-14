<template>
  <div class="sm:flex sm:items-center mb-8">
    <div class="sm:flex-auto">
      <h1 class="text-2xl font-semibold text-gray-900">{{ title }}</h1>
      <p v-if="description" class="mt-2 text-sm text-gray-700">
        {{ description }}
      </p>
      <slot name="description"></slot>
    </div>
    <div v-if="$slots.actions" class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none">
      <slot name="actions"></slot>
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
    default: ''
  }
})
</script>
