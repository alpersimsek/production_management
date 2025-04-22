<template>
  <div class="overflow-hidden rounded-lg bg-white shadow" :class="customClass">
    <div class="p-6">
      <div class="flex items-center">
        <div v-if="$slots.icon || icon" class="flex-shrink-0">
          <slot name="icon">
            <component :is="icon" class="h-8 sm:h-10 w-8 sm:w-10 text-indigo-600 flex-shrink-0" aria-hidden="true" />
          </slot>
        </div>
        <div :class="{ 'ml-3': $slots.icon || icon }" class="w-0 flex-1">
          <h3 class="text-base font-semibold text-gray-900">{{ title }}</h3>
          <p v-if="description" class="mt-1 text-sm text-gray-500">{{ description }}</p>
          <slot name="description"></slot>
        </div>
      </div>
      <div class="mt-6">
        <slot name="actions">
          <router-link v-if="linkTo" :to="linkTo"
            class="inline-flex items-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-primary shadow-sm ring-1 ring-inset ring-primary hover:bg-gray-50">
            {{ linkText }}
          </router-link>
        </slot>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },
  description: {
    type: String,
    default: '',
  },
  icon: {
    type: [Object, Function, null], // Allow Object, Function, or null for Heroicons
    default: null,
  },
  linkTo: {
    type: String,
    default: '',
  },
  linkText: {
    type: String,
    default: 'View',
  },
  customClass: {
    type: String,
    default: '',
  },
})
</script>
