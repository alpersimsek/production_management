<template>
  <div class="relative overflow-hidden rounded-lg bg-white shadow">
    <div class="px-4 pb-5 pt-5 sm:px-6 sm:pt-6">
      <button @click="toggleExpanded" class="w-full text-left">
        <div class="relative">
          <div v-if="icon" class="absolute rounded-md bg-primary p-3">
            <component :is="icon" class="h-6 w-6 text-white" aria-hidden="true" />
          </div>
          <div class="flex items-center justify-between" :class="{ 'ml-16': icon }">
            <div>
              <h3 class="text-lg font-medium text-gray-900">{{ title }}</h3>
              <p v-if="subtitle" class="text-sm text-gray-500">{{ subtitle }}</p>
            </div>
            <component
              :is="expanded ? ChevronUpIcon : ChevronDownIcon"
              class="h-5 w-5 text-gray-400"
              v-if="expandable"
            />
          </div>
          <div v-if="count !== undefined" :class="{ 'ml-16': icon }" class="flex items-baseline pb-4">
            <p class="text-2xl font-semibold text-gray-900">
              {{ count }}
            </p>
          </div>
        </div>
      </button>

      <div v-if="!expandable || expanded" :class="{ 'mt-4 border-t pt-4': expandable }">
        <slot name="content"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ChevronUpIcon, ChevronDownIcon } from '@heroicons/vue/24/outline'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: Object,
    default: null
  },
  count: {
    type: Number,
    default: undefined
  },
  expandable: {
    type: Boolean,
    default: true
  },
  initialExpanded: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['expanded', 'collapsed'])
const expanded = ref(props.initialExpanded)

watch(() => props.initialExpanded, (value) => {
  expanded.value = value
})

const toggleExpanded = () => {
  if (!props.expandable) return

  expanded.value = !expanded.value
  emit(expanded.value ? 'expanded' : 'collapsed')
}
</script>
