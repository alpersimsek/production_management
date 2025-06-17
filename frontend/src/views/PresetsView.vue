<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import MainLayout from '../components/MainLayout.vue'
import PresetsList from '../components/PresetsList.vue'
import PresetForm from '../components/PresetForm.vue'
import PresetRuleForm from '../components/PresetRuleForm.vue'
import RuleManagement from '../components/RuleManagement.vue'
import CustomRuleForm from '../components/CustomRuleForm.vue'
import ConfirmDeleteDialog from '../components/ConfirmDeleteDialog.vue'
import { XMarkIcon, PlusIcon, ExclamationCircleIcon } from '@heroicons/vue/24/outline'
import ApiService from '../services/api'

const router = useRouter()
const presets = ref([])
const products = ref([])
const rules = ref([])
const loading = ref(false)
const error = ref('')
const showPresetModal = ref(false)
const showRuleModal = ref(false)
const showDeleteModal = ref(false)
const showRuleListModal = ref(false)
const showCustomRuleForm = ref(false)
const editingPreset = ref(null)
const editingRule = ref(null)
const selectedRule = ref(null)
const deleteTarget = ref(null)
const deleteType = ref('')
const currentPresetId = ref(null)
const defaultProductId = ref(null)

const isAdmin = computed(() => {
  try {
    const userData = JSON.parse(sessionStorage.getItem('user'))
    return userData && userData.role === 'admin'
  } catch {
    return false
  }
})

// Debug modal state changes
watch(showRuleListModal, (newVal) => {
  console.log(`showRuleListModal changed to: ${newVal}`)
})
watch(showCustomRuleForm, (newVal) => {
  console.log(`showCustomRuleForm changed to: ${newVal}`)
})

onMounted(async () => {
  if (!isAdmin.value) {
    router.push('/')
    return
  }
  try {
    loading.value = true
    await Promise.all([loadPresets(), loadProducts(), loadRules()])
  } catch (err) {
    error.value = `Failed to load data: ${err.message || err.data?.detail || 'Unknown error'}`
  } finally {
    loading.value = false
  }
})

const loadPresets = async () => {
  try {
    const response = await ApiService.getPresets()
    presets.value = response || []
    return response
  } catch (err) {
    throw err
  }
}

const loadProducts = async () => {
  try {
    const response = await ApiService.getProducts()
    products.value = response || []
    return response
  } catch (err) {
    throw err
  }
}

const loadRules = async () => {
  try {
    const response = await ApiService.getRules()
    rules.value = response.data || []
    return response
  } catch (err) {
    throw err
  }
}

const loadPresetRules = async (presetId) => {
  try {
    const response = await ApiService.getPresetRules(presetId)
    const presetIndex = presets.value.findIndex(p => p.id === presetId)
    if (presetIndex !== -1) {
      presets.value[presetIndex].rules = response || []
    }
    return response
  } catch (err) {
    throw err
  }
}

const openPresetModal = (preset = null, productId = null) => {
  editingPreset.value = null // Reset to avoid stale state
  defaultProductId.value = null
  if (preset && typeof preset === 'object') {
    editingPreset.value = { ...preset } // Deep copy to ensure reactivity
  }
  defaultProductId.value = productId
  showPresetModal.value = true
  console.log('Opening preset modal with preset:', editingPreset.value)
}

const handleAddPreset = (productId) => {
  openPresetModal(null, productId)
}

const handleEditPreset = (eventOrPreset) => {
  const preset = eventOrPreset && typeof eventOrPreset === 'object' && !('target' in eventOrPreset) ? eventOrPreset : null
  if (preset) {
    openPresetModal(preset, null)
  } else {
    console.warn('Invalid preset object received in handleEditPreset:', eventOrPreset)
  }
}

const handleDeletePreset = (preset) => {
  confirmDelete('preset', preset)
}

const handleAddRuleToPreset = (presetId) => {
  openRuleModal(presetId)
}

const handleEditPresetRule = (rule) => {
  openRuleModal(rule.presetId, rule)
}

const handleDeletePresetRule = (rule) => {
  confirmDelete('rule', rule)
}

const handlePresetSaved = async () => {
  try {
    await loadPresets()
    showPresetModal.value = false
  } catch (err) {
    error.value = `Failed to refresh preset list: ${err.message || err.data?.detail || 'Unknown error'}`
  }
}

const handlePresetError = (err) => {
  error.value = `Failed to save preset: ${typeof err === 'string' ? err : (err.message || err.data?.detail || 'Unknown error')}`
}

const openRuleModal = (presetId, rule = null) => {
  currentPresetId.value = presetId
  editingRule.value = rule ? { ...rule, preset_id: presetId } : null
  showRuleModal.value = true
}

const handleRuleSaved = async (presetId) => {
  try {
    await loadPresetRules(presetId)
    showRuleModal.value = false
    currentPresetId.value = null
  } catch (err) {
    error.value = `Failed to refresh rules list: ${err.message || err.data?.detail || 'Unknown error'}`
  }
}

const handleRuleError = (err) => {
  let message = 'Failed to save rule'
  if (typeof err === 'string') {
    message = err
  } else if (err.data?.detail) {
    message = Array.isArray(err.data.detail) ? err.data.detail.map(e => e.msg).join('; ') : err.data.detail
  } else if (err.message) {
    message = err.message
  }
  error.value = message
}

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
    error.value = `Failed to delete ${deleteType.value}: ${err.message || err.data?.detail || 'Unknown error'}`
  } finally {
    loading.value = false
  }
}

const openRuleListModal = () => {
  showRuleListModal.value = true
  console.log('Opened RuleManagement modal')
}

const handleRuleListSaved = async () => {
  try {
    await loadRules()
    showCustomRuleForm.value = false
    selectedRule.value = null
    // Ensure RuleManagement modal stays open
    if (!showRuleListModal.value) {
      console.warn('RuleManagement modal was unexpectedly closed')
      showRuleListModal.value = true
    }
  } catch (err) {
    error.value = `Failed to refresh rules list: ${err.message || err.data?.detail || 'Unknown error'}`
  }
}

const openCustomRuleForm = (rule = null) => {
  selectedRule.value = rule
  showCustomRuleForm.value = true
  console.log('Opened CustomRuleForm modal')
}

const closeCustomRuleForm = () => {
  showCustomRuleForm.value = false
  selectedRule.value = null
  // Ensure RuleManagement modal stays open
  if (!showRuleListModal.value) {
    console.warn('RuleManagement modal was unexpectedly closed')
    showRuleListModal.value = true
  }
  console.log('Closed CustomRuleForm modal')
}
</script>

<template>
  <MainLayout>
    <div class="min-h-screen bg-gray-50 px-4 sm:px-6 lg:px-8 py-8">
      <div class="sm:flex sm:items-center mb-8">
        <div class="sm:flex-auto">
          <div class="flex items-center gap-3">
            <svg xmlns="http://www.w3.org/2000/svg"
              class="h-8 w-8 text-indigo-600 transition-transform duration-300 hover:scale-110" fill="none"
              viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <h1 class="text-3xl font-bold text-gray-900 tracking-tight">Preset Management</h1>
          </div>
          <p class="mt-2 text-sm text-gray-600 font-medium">Seamlessly manage product presets and their associated rules</p>
        </div>
        <div class="mt-6 sm:mt-0 sm:ml-16 sm:flex-none flex space-x-4">
          <button type="button" @click="openRuleListModal"
            class="inline-flex items-center justify-center rounded-md bg-gradient-to-r from-indigo-600 to-indigo-700 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
            aria-label="Manage rules">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7" />
            </svg>
            Manage Rules
          </button>
          <button type="button" @click="openPresetModal"
            class="inline-flex items-center justify-center rounded-md bg-gradient-to-r from-indigo-600 to-indigo-700 px-5 py-2.5 text-sm font-semibold text-white shadow-sm hover:from-indigo-700 hover:to-indigo-800 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200"
            aria-label="Add preset">
            <PlusIcon class="h-5 w-5 mr-2" />
            Add Preset
          </button>
        </div>
      </div>
      <div v-if="error" class="mt-6 rounded-xl bg-red-50 p-4 shadow-sm animate-fade-in">
        <div class="flex items-center">
          <ExclamationCircleIcon class="h-5 w-5 text-red-400" />
          <p class="ml-3 text-sm font-medium text-red-800">{{ error }}</p>
          <button type="button" @click="error = ''"
            class="ml-auto text-red-500 hover:text-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 transition-colors duration-200"
            aria-label="Dismiss error">
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>
      </div>
      <div v-if="loading" class="mt-8 flex justify-center items-center">
        <div class="animate-spin rounded-full h-12 w-12 border-t-4 border-indigo-600"></div>
        <p class="ml-4 text-sm font-medium text-gray-600">Loading presets...</p>
      </div>
      <div v-else class="mt-8 bg-white rounded-xl shadow-md p-6">
        <PresetsList :presets="presets" :products="products" :rules="rules" :loading="loading"
          @add-preset="handleAddPreset" @edit-preset="handleEditPreset" @delete-preset="handleDeletePreset"
          @add-rule-to-preset="handleAddRuleToPreset" @edit-preset-rule="handleEditPresetRule"
          @delete-preset-rule="handleDeletePresetRule" @load-preset-rules="loadPresetRules" class="animate-fade-in" />
      </div>
      <PresetForm v-if="showPresetModal" :open="showPresetModal" :products="products" :edit-preset="editingPreset"
        :defaultProductId="defaultProductId" @close="showPresetModal = false" @saved="handlePresetSaved"
        @error="handlePresetError" />
      <transition name="modal">
        <PresetRuleForm v-if="showRuleModal" :open="showRuleModal" :preset-id="currentPresetId" :rules="rules"
          :preset-rules="presets.find(p => p.id === currentPresetId)?.rules || []" :edit-rule="editingRule"
          @close="showRuleModal = false" @saved="handleRuleSaved(currentPresetId)" @error="handleRuleError" />
      </transition>
      <transition name="modal">
        <ConfirmDeleteDialog v-if="showDeleteModal" :open="showDeleteModal" :item-type="deleteType"
          :item-name="deleteTarget?.name" @close="showDeleteModal = false" @confirm="handleDelete" />
      </transition>
      <!-- Note: RuleManagement and CustomRuleForm are nested modals. Ensure z-index and focus management are correct -->
      <RuleManagement v-if="showRuleListModal" :open="showRuleListModal"
        @close="showRuleListModal = false" @saved="handleRuleListSaved" @open-rule-form="openCustomRuleForm"
        @delete="confirmDelete('customRule', $event)" />
      <CustomRuleForm v-if="showCustomRuleForm" :open="showCustomRuleForm" :rule="selectedRule"
        @close="closeCustomRuleForm" @saved="handleRuleListSaved" @error="error = $event" />
    </div>
  </MainLayout>
</template>

<style scoped>
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in { animation: fadeIn 0.3s ease-out; }
.modal-enter-active, .modal-leave-active { transition: all 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: translateY(-20px); }
</style>