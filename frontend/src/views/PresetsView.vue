<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../components/MainLayout.vue'
import PresetsList from '../components/PresetsList.vue'
import PresetForm from '../components/PresetForm.vue'
import PresetRuleForm from '../components/PresetRuleForm.vue'
import RuleManagement from '../components/RuleManagement.vue'
import ConfirmDeleteDialog from '../components/ConfirmDeleteDialog.vue'
import { XMarkIcon, PlusIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'

const router = useRouter()
const presets = ref([])
const products = ref([])
const rules = ref([])
const loading = ref(false)
const error = ref('')

// State for modals
const showPresetModal = ref(false)
const showRuleModal = ref(false)
const showDeleteModal = ref(false)
const showRuleListModal = ref(false)
const editingPreset = ref(null)
const editingRule = ref(null)
const deleteTarget = ref(null)
const deleteType = ref('') // 'preset', 'rule', or 'customRule'

// Role check
const isAdmin = computed(() => {
  try {
    const userData = JSON.parse(sessionStorage.getItem('user'))
    return userData && userData.role === 'admin'
  } catch {
    return false
  }
})

// Check if user is admin, otherwise redirect
onMounted(async () => {
  if (!isAdmin.value) {
    router.push('/') // Redirect non-admin users
    return
  }

  try {
    loading.value = true
    // Load initial data
    await Promise.all([
      loadPresets(),
      loadProducts(),
      loadRules()
    ])
  } catch (err) {
    error.value = 'Failed to load data: ' + (err.message || 'Unknown error')
  } finally {
    loading.value = false
  }
})

// Data loading functions
const loadPresets = async () => {
  try {
    const response = await ApiService.getPresets()
    presets.value = response || []
    return response
  } catch (err) {
    console.error('Failed to load presets:', err)
    throw err
  }
}

const loadProducts = async () => {
  try {
    const response = await ApiService.getProducts()
    products.value = response || []
    return response
  } catch (err) {
    console.error('Failed to load products:', err)
    throw err
  }
}

const loadRules = async () => {
  try {
    const response = await ApiService.getRules()
    rules.value = response || []
    return response
  } catch (err) {
    console.error('Failed to load rules:', err)
    throw err
  }
}

const loadPresetRules = async (presetId) => {
  try {
    const response = await ApiService.getPresetRules(presetId)
    // Update the preset with its rules
    const presetIndex = presets.value.findIndex(p => p.id === presetId)
    if (presetIndex !== -1) {
      presets.value[presetIndex].rules = response || []
    }
    return response
  } catch (err) {
    console.error(`Failed to load rules for preset ${presetId}:`, err)
    throw err
  }
}

// CRUD operations for presets
const openPresetModal = (preset = null, productId = null) => {
  editingPreset.value = preset
  // Store the product ID if it's provided (for creating new presets)
  if (productId && !preset) {
    // This is for creating a new preset with a specific product
    console.log('Opening preset modal for product:', productId)
  }
  showPresetModal.value = true
}

const handlePresetSaved = async () => {
  try {
    await loadPresets()
    showPresetModal.value = false
  } catch (err) {
    error.value = `Failed to refresh preset list: ${err.message || 'Unknown error'}`
  }
}

const handlePresetError = (err) => {
  error.value = `Failed to save preset: ${err.message || 'Unknown error'}`
}

// CRUD operations for rules
const openRuleModal = (presetId, rule = null) => {
  editingRule.value = rule
  showRuleModal.value = true
}

const handleRuleSaved = async (presetId) => {
  try {
    await loadPresetRules(presetId)
    showRuleModal.value = false
  } catch (err) {
    error.value = `Failed to refresh rules list: ${err.message || 'Unknown error'}`
  }
}

const handleRuleError = (err) => {
  error.value = `Failed to save rule: ${err.message || 'Unknown error'}`
}

// Delete operations
const confirmDelete = (type, item) => {
  deleteType.value = type
  deleteTarget.value = item
  showDeleteModal.value = true
}

const handleDelete = async () => {
  try {
    loading.value = true

    if (deleteType.value === 'preset') {
      await ApiService.deletePreset(deleteTarget.value.id)
      await loadPresets()
    } else if (deleteType.value === 'rule') {
      await ApiService.deletePresetRule(deleteTarget.value.preset_id, deleteTarget.value.rule_id)
      await loadPresetRules(deleteTarget.value.preset_id)
    } else if (deleteType.value === 'customRule') {
      await ApiService.deleteRule(deleteTarget.value.id)
      await loadRules()
    }

    showDeleteModal.value = false
    deleteTarget.value = null
    deleteType.value = ''
  } catch (err) {
    error.value = `Failed to delete ${deleteType.value}: ` + (err.message || 'Unknown error')
  } finally {
    loading.value = false
  }
}

// Rule management
const openRuleListModal = () => {
  showRuleListModal.value = true
}

const handleRuleListSaved = async () => {
  try {
    await loadRules()
  } catch (err) {
    error.value = `Failed to refresh rules list: ${err.message || 'Unknown error'}`
  }
}

// Handlers for the PresetsList component
const handleAddPreset = (productId = null) => {
  openPresetModal(null, productId)
}

const handleEditPreset = (preset) => {
  openPresetModal(preset)
}

const handleDeletePreset = (preset) => {
  confirmDelete('preset', preset)
}

const handleAddRuleToPreset = (presetId) => {
  openRuleModal(presetId)
}

const handleEditPresetRule = ({ presetId, rule }) => {
  openRuleModal(presetId, rule)
}

const handleDeletePresetRule = (data) => {
  confirmDelete('rule', data)
}
</script>

<template>
  <MainLayout>
    <div class="px-4 sm:px-6 lg:px-8">
      <div class="sm:flex sm:items-center">
        <div class="sm:flex-auto">
          <div class="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              class="h-6 w-6 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
              />
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
            </svg>
            <h1 class="text-xl font-semibold text-gray-900">Preset Management</h1>
          </div>
          <p class="mt-2 text-sm text-gray-700">
            Manage product presets and their associated rules
          </p>
        </div>
        <div class="mt-4 sm:mt-0 sm:ml-16 sm:flex-none flex space-x-4">
          <button
            type="button"
            @click="openRuleListModal()"
            class="inline-flex items-center justify-center rounded-md border border-indigo-300 bg-white px-4 py-2 text-sm font-medium text-indigo-700 shadow-sm hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
            </svg>
            Manage Rules
          </button>
          <button
            type="button"
            @click="openPresetModal()"
            class="inline-flex items-center justify-center rounded-md border border-transparent bg-indigo-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 sm:w-auto"
          >
            <PlusIcon class="h-5 w-5 mr-2" />
            Add Preset
          </button>
        </div>
      </div>

      <!-- Error message -->
      <div v-if="error" class="mt-4 rounded-md bg-red-50 p-4">
        <div class="flex">
          <div class="flex-shrink-0">
            <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
            </svg>
          </div>
          <div class="ml-3">
            <p class="text-sm font-medium text-red-800">{{ error }}</p>
          </div>
          <div class="ml-auto pl-3">
            <div class="-mx-1.5 -my-1.5">
              <button
                type="button"
                @click="error = ''"
                class="inline-flex rounded-md bg-red-50 p-1.5 text-red-500 hover:bg-red-100 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                <XMarkIcon class="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Main content - presets list -->
      <PresetsList
        :presets="presets"
        :products="products"
        :rules="rules"
        :loading="loading"
        @add-preset="handleAddPreset"
        @edit-preset="handleEditPreset"
        @delete-preset="handleDeletePreset"
        @add-rule-to-preset="handleAddRuleToPreset"
        @edit-preset-rule="handleEditPresetRule"
        @delete-preset-rule="handleDeletePresetRule"
        @load-preset-rules="loadPresetRules"
      />

      <!-- Preset modal -->
      <PresetForm
        :open="showPresetModal"
        :products="products"
        :edit-preset="editingPreset"
        @close="showPresetModal = false"
        @saved="handlePresetSaved"
        @error="handlePresetError"
      />

      <!-- Rule modal -->
      <PresetRuleForm
        v-if="showRuleModal"
        :open="showRuleModal"
        :preset-id="editingRule ? editingRule.preset_id : $route.params.presetId"
        :rules="rules"
        :preset-rules="presets.find(p => p.id === (editingRule ? editingRule.preset_id : $route.params.presetId))?.rules || []"
        :edit-rule="editingRule"
        @close="showRuleModal = false"
        @saved="handleRuleSaved(editingRule ? editingRule.preset_id : $route.params.presetId)"
        @error="handleRuleError"
      />

      <!-- Delete confirmation dialog -->
      <ConfirmDeleteDialog
        :open="showDeleteModal"
        :item-type="deleteType"
        @close="showDeleteModal = false"
        @confirm="handleDelete"
      />

      <!-- Rule management modal -->
      <RuleManagement
        :open="showRuleListModal"
        :rules="rules"
        @close="showRuleListModal = false"
        @saved="handleRuleListSaved"
        @delete="confirmDelete('customRule', $event)"
      />
    </div>
  </MainLayout>
</template>
