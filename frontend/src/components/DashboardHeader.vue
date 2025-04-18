<template>
  <div class="mb-8">
    <h1 class="text-2xl font-semibold text-gray-900">
      Welcome back, {{ capitalizedUsername }}
    </h1>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  username: {
    type: String,
    required: true
  }
})

const capitalizedUsername = computed(() => {
  if (!props.username) return ''
  return props.username.charAt(0).toUpperCase() + props.username.slice(1)
})
</script>
