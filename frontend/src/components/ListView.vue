<!--
GDPR Tool List View - Generic List Container Component

This component provides a generic list container for the GDPR compliance tool.
It displays lists of items with customizable rendering and empty states.

Key Features:
- Generic List Display: Shows lists of any type of items
- Customizable Rendering: Function-based item rendering configuration
- Empty State: Displays placeholder message when no items are present
- Slot Support: Flexible slot system for custom content
- Action Support: Slot for item-specific actions
- Responsive Grid: Grid layout for list items

Props:
- title: List title (string, optional)
- items: Array of items to display (array, required)
- itemKey: Key field for item identification (string, default: 'id')
- emptyMessage: Message when no items (string, default: 'No items')
- emptyIcon: Icon for empty state (object, optional)
- getItemTitle: Function to get item title (function, default: item => item.name || item.title || '')
- getItemSubtitle: Function to get item subtitle (function, default: () => '')
- getItemMetadata: Function to get item metadata (function, default: () => '')
- getItemIcon: Function to get item icon (function, default: () => null)
- getItemIconClass: Function to get item icon class (function, default: () => 'text-gray-400')
- getItemClass: Function to get item CSS class (function, default: () => '')

Slots:
- default: Custom item rendering slot (overrides default rendering)
- empty: Custom empty state slot (overrides default empty state)
- itemActions: Item-specific actions slot

Features:
- Item Rendering: Configurable item rendering with function props
- Empty State: Customizable empty state with icon and message
- Action Support: Slot for item-specific actions
- Responsive Layout: Grid layout that adapts to screen size
- Flexible Content: Slot-based content system for customization

The component provides a flexible list interface for various data types
in the GDPR compliance tool with proper rendering and empty state handling.
-->

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
