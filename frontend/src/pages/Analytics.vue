<template>
  <div>
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-gray-900">Analytics & Reports</h1>
          <div class="flex gap-2">
            <select v-model="selectedPeriod" class="input-field">
              <option value="7">Last 7 Days</option>
              <option value="30">Last 30 Days</option>
              <option value="90">Last 90 Days</option>
              <option value="365">Last Year</option>
            </select>
            <button
              @click="exportReport"
              class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              Export Report
            </button>
          </div>
        </div>
      </div>
    </header>

    <main>
      <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="px-4 py-6 sm:px-0">
          <!-- KPI Cards -->
          <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="p-5">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <svg class="h-6 w-6 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1"></path>
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">Total Revenue</dt>
                      <dd class="flex items-baseline">
                        <div class="text-2xl font-semibold text-gray-900">
                          ₺{{ formatNumber(totalRevenue) }}
                        </div>
                        <div class="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                          +{{ revenueGrowth }}%
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="p-5">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <svg class="h-6 w-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">Orders Completed</dt>
                      <dd class="flex items-baseline">
                        <div class="text-2xl font-semibold text-gray-900">
                          {{ completedOrders }}
                        </div>
                        <div class="ml-2 flex items-baseline text-sm font-semibold text-blue-600">
                          +{{ ordersGrowth }}%
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="p-5">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <svg class="h-6 w-6 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">Production Efficiency</dt>
                      <dd class="flex items-baseline">
                        <div class="text-2xl font-semibold text-gray-900">
                          {{ productionEfficiency }}%
                        </div>
                        <div class="ml-2 flex items-baseline text-sm font-semibold text-purple-600">
                          +{{ efficiencyGrowth }}%
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div class="bg-white overflow-hidden shadow rounded-lg">
              <div class="p-5">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <svg class="h-6 w-6 text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"></path>
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">Inventory Value</dt>
                      <dd class="flex items-baseline">
                        <div class="text-2xl font-semibold text-gray-900">
                          ₺{{ formatNumber(inventoryValue) }}
                        </div>
                        <div class="ml-2 flex items-baseline text-sm font-semibold text-orange-600">
                          +{{ inventoryGrowth }}%
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Charts Section -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <!-- Revenue Chart -->
            <div class="bg-white shadow rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Revenue Trend</h3>
              <div class="h-64 flex items-end justify-between space-x-2">
                <div v-for="(value, index) in revenueData" :key="index" class="flex flex-col items-center">
                  <div
                    class="bg-primary-500 rounded-t"
                    :style="{ height: (value / Math.max(...revenueData)) * 200 + 'px', width: '20px' }"
                  ></div>
                  <span class="text-xs text-gray-500 mt-2">{{ formatNumber(value) }}</span>
                  <span class="text-xs text-gray-400">{{ getMonthName(index) }}</span>
                </div>
              </div>
            </div>

            <!-- Production Chart -->
            <div class="bg-white shadow rounded-lg p-6">
              <h3 class="text-lg font-medium text-gray-900 mb-4">Production Output</h3>
              <div class="h-64 flex items-end justify-between space-x-2">
                <div v-for="(value, index) in productionData" :key="index" class="flex flex-col items-center">
                  <div
                    class="bg-green-500 rounded-t"
                    :style="{ height: (value / Math.max(...productionData)) * 200 + 'px', width: '20px' }"
                  ></div>
                  <span class="text-xs text-gray-500 mt-2">{{ value }}kg</span>
                  <span class="text-xs text-gray-400">{{ getMonthName(index) }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Detailed Analytics Tabs -->
          <div class="bg-white shadow rounded-lg">
            <div class="border-b border-gray-200">
              <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                <button
                  v-for="tab in analyticsTabs"
                  :key="tab.id"
                  @click="activeTab = tab.id"
                  :class="[
                    'py-4 px-1 border-b-2 font-medium text-sm',
                    activeTab === tab.id
                      ? 'border-primary-500 text-primary-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  ]"
                >
                  {{ tab.name }}
                </button>
              </nav>
            </div>

            <div class="p-6">
              <!-- Production Analytics -->
              <div v-if="activeTab === 'production'" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Machine Utilization</h4>
                    <div class="space-y-2">
                      <div v-for="machine in machineUtilization" :key="machine.name" class="flex justify-between">
                        <span class="text-sm text-gray-600">{{ machine.name }}</span>
                        <span class="text-sm font-medium">{{ machine.utilization }}%</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Quality Metrics</h4>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Pass Rate</span>
                        <span class="text-sm font-medium text-green-600">{{ qualityMetrics.passRate }}%</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Defect Rate</span>
                        <span class="text-sm font-medium text-red-600">{{ qualityMetrics.defectRate }}%</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Rework Rate</span>
                        <span class="text-sm font-medium text-yellow-600">{{ qualityMetrics.reworkRate }}%</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Waste Management</h4>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Total Waste</span>
                        <span class="text-sm font-medium">{{ wasteMetrics.totalWaste }}kg</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Recycled</span>
                        <span class="text-sm font-medium text-green-600">{{ wasteMetrics.recycled }}kg</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Disposed</span>
                        <span class="text-sm font-medium text-red-600">{{ wasteMetrics.disposed }}kg</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Sales Analytics -->
              <div v-if="activeTab === 'sales'" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Top Products</h4>
                    <div class="space-y-2">
                      <div v-for="product in topProducts" :key="product.name" class="flex justify-between">
                        <span class="text-sm text-gray-600">{{ product.name }}</span>
                        <span class="text-sm font-medium">₺{{ formatNumber(product.revenue) }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Customer Analysis</h4>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Total Customers</span>
                        <span class="text-sm font-medium">{{ customerMetrics.totalCustomers }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">New Customers</span>
                        <span class="text-sm font-medium text-green-600">{{ customerMetrics.newCustomers }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Repeat Orders</span>
                        <span class="text-sm font-medium text-blue-600">{{ customerMetrics.repeatOrders }}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Inventory Analytics -->
              <div v-if="activeTab === 'inventory'" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Stock Levels</h4>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">In Stock</span>
                        <span class="text-sm font-medium text-green-600">{{ stockLevels.inStock }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Low Stock</span>
                        <span class="text-sm font-medium text-yellow-600">{{ stockLevels.lowStock }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Out of Stock</span>
                        <span class="text-sm font-medium text-red-600">{{ stockLevels.outOfStock }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Turnover Rate</h4>
                    <div class="space-y-2">
                      <div v-for="item in turnoverRates" :key="item.name" class="flex justify-between">
                        <span class="text-sm text-gray-600">{{ item.name }}</span>
                        <span class="text-sm font-medium">{{ item.rate }}x</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Warehouse Performance</h4>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Pick Accuracy</span>
                        <span class="text-sm font-medium text-green-600">{{ warehouseMetrics.pickAccuracy }}%</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Order Fulfillment</span>
                        <span class="text-sm font-medium text-blue-600">{{ warehouseMetrics.fulfillmentRate }}%</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Avg. Pick Time</span>
                        <span class="text-sm font-medium">{{ warehouseMetrics.avgPickTime }}min</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Financial Analytics -->
              <div v-if="activeTab === 'financial'" class="space-y-6">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Cost Analysis</h4>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Raw Materials</span>
                        <span class="text-sm font-medium">₺{{ formatNumber(costAnalysis.rawMaterials) }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Labor</span>
                        <span class="text-sm font-medium">₺{{ formatNumber(costAnalysis.labor) }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Overhead</span>
                        <span class="text-sm font-medium">₺{{ formatNumber(costAnalysis.overhead) }}</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Shipping</span>
                        <span class="text-sm font-medium">₺{{ formatNumber(costAnalysis.shipping) }}</span>
                      </div>
                    </div>
                  </div>
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-2">Profitability</h4>
                    <div class="space-y-2">
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Gross Margin</span>
                        <span class="text-sm font-medium text-green-600">{{ profitability.grossMargin }}%</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">Net Margin</span>
                        <span class="text-sm font-medium text-blue-600">{{ profitability.netMargin }}%</span>
                      </div>
                      <div class="flex justify-between">
                        <span class="text-sm text-gray-600">ROI</span>
                        <span class="text-sm font-medium text-purple-600">{{ profitability.roi }}%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// Data
const selectedPeriod = ref('30')
const activeTab = ref('production')

// KPI Data
const totalRevenue = ref(1250000)
const revenueGrowth = ref(12.5)
const completedOrders = ref(156)
const ordersGrowth = ref(8.3)
const productionEfficiency = ref(87.2)
const efficiencyGrowth = ref(5.1)
const inventoryValue = ref(450000)
const inventoryGrowth = ref(15.7)

// Chart Data
const revenueData = ref([85000, 92000, 88000, 105000, 98000, 112000, 125000])
const productionData = ref([1200, 1350, 1280, 1450, 1380, 1520, 1680])

// Analytics Tabs
const analyticsTabs = ref([
  { id: 'production', name: 'Production' },
  { id: 'sales', name: 'Sales' },
  { id: 'inventory', name: 'Inventory' },
  { id: 'financial', name: 'Financial' }
])

// Production Analytics
const machineUtilization = ref([
  { name: 'Extrusion Line 1', utilization: 85 },
  { name: 'Mixing Tank 1', utilization: 92 },
  { name: 'Packaging Line 1', utilization: 78 },
  { name: 'Quality Control', utilization: 88 }
])

const qualityMetrics = ref({
  passRate: 94.2,
  defectRate: 3.1,
  reworkRate: 2.7
})

const wasteMetrics = ref({
  totalWaste: 1250,
  recycled: 890,
  disposed: 360
})

// Sales Analytics
const topProducts = ref([
  { name: 'Market Poşeti 30x40', revenue: 450000 },
  { name: 'Bulaşık Deterjanı', revenue: 320000 },
  { name: 'Temizlik Malzemesi', revenue: 280000 },
  { name: 'Endüstriyel Temizlik', revenue: 200000 }
])

const customerMetrics = ref({
  totalCustomers: 45,
  newCustomers: 8,
  repeatOrders: 78
})

// Inventory Analytics
const stockLevels = ref({
  inStock: 156,
  lowStock: 12,
  outOfStock: 3
})

const turnoverRates = ref([
  { name: 'Raw Materials', rate: 4.2 },
  { name: 'Finished Goods', rate: 6.8 },
  { name: 'Packaging', rate: 8.1 }
])

const warehouseMetrics = ref({
  pickAccuracy: 98.5,
  fulfillmentRate: 96.2,
  avgPickTime: 12.3
})

// Financial Analytics
const costAnalysis = ref({
  rawMaterials: 450000,
  labor: 280000,
  overhead: 150000,
  shipping: 75000
})

const profitability = ref({
  grossMargin: 35.2,
  netMargin: 18.7,
  roi: 24.3
})

// Methods
function formatNumber (num) {
  return new Intl.NumberFormat('tr-TR').format(num)
}

function getMonthName (index) {
  const months = ['Oca', 'Şub', 'Mar', 'Nis', 'May', 'Haz', 'Tem', 'Ağu', 'Eyl', 'Eki', 'Kas', 'Ara']
  return months[index] || ''
}

function exportReport () {
  // TODO: Implement report export functionality
  console.log('Exporting analytics report...')
}

// Lifecycle
onMounted(() => {
  // Load analytics data
})
</script>
