<template>
  <div>
    <h2 v-if="title" class="text-lg font-medium text-gray-900">{{ title }}</h2>
    <ul role="list" class="mt-4 grid grid-cols-1 gap-4">
      <!-- Empty state -->
      <slot v-if="items.length === 0" name="empty">
        <ListItem :icon="emptyIcon" :icon-class="'text-gray-300'">
          <p class="text-sm text-gray-500 italic">{{ emptyMessage }}</p>
        </ListItem>
      </slot>

      <!-- List items -->
      <slot v-for="(item, index) in items" :key="itemKey ? item[itemKey] : index" :item="item" :index="index">
        <!-- Default rendering if no slot content is provided -->
        <ListItem :title="getItemTitle(item)" :subtitle="getItemSubtitle(item)" :metadata="getItemMetadata(item)"
          :icon="getItemIcon(item)" :icon-class="getItemIconClass(item)" :custom-class="getItemClass(item)">
          <template v-if="$slots.itemActions" #actions>
            <slot name="itemActions" :item="item" :index="index"></slot>
          </template>
        </ListItem>
      </slot>
    </ul>
  </div>
</template>

<script setup>
import ListItem from './ListItem.vue'

defineProps({
  title: {
    type: String,
    default: ''
  },
  items: {
    type: Array,
    required: true
  },
  itemKey: {
    type: String,
    default: 'id'
  },
  emptyMessage: {
    type: String,
    default: 'No items'
  },
  emptyIcon: {
    type: [Object, null],
    default: null
  },
  getItemTitle: {
    type: Function,
    default: item => item.name || item.title || ''
  },
  getItemSubtitle: {
    type: Function,
    default: () => ''
  },
  getItemMetadata: {
    type: Function,
    default: () => ''
  },
  getItemIcon: {
    type: Function,
    default: () => null
  },
  getItemIconClass: {
    type: Function,
    default: () => 'text-gray-400'
  },
  getItemClass: {
    type: Function,
    default: () => ''
  }
})
</script>
