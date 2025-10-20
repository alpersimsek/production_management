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
          <!-- Desktop Grid -->
          <div class="hidden lg:grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
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

          <!-- Mobile KPI Carousel -->
          <div class="block lg:hidden mb-8">
            <div class="text-sm text-gray-500 mb-2 text-center">
              {{ $t('analytics.showing_kpi') }} {{ currentKpiIndex + 1 }} {{ $t('common.of') }} {{ kpiCards.length }} — {{ $t('orders.swipe_hint') }}
            </div>
            <div
              class="bg-white overflow-hidden shadow rounded-lg select-none"
              @touchstart.passive="handleKpiTouchStart"
              @touchmove.prevent="handleKpiTouchMove"
              @touchend="handleKpiTouchEnd"
              @mousedown.prevent="handleKpiMouseDown"
              @mousemove.prevent="handleKpiMouseMove"
              @mouseup.prevent="handleKpiMouseUp"
              @mouseleave.prevent="handleKpiMouseUp"
            >
              <div class="p-5" v-if="currentKpiCard">
                <div class="flex items-center">
                  <div class="flex-shrink-0">
                    <svg class="h-6 w-6" :class="currentKpiCard.iconColor" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" :d="currentKpiCard.iconPath"></path>
                    </svg>
                  </div>
                  <div class="ml-5 w-0 flex-1">
                    <dl>
                      <dt class="text-sm font-medium text-gray-500 truncate">{{ currentKpiCard.title }}</dt>
                      <dd class="flex items-baseline">
                        <div class="text-2xl font-semibold text-gray-900">
                          {{ currentKpiCard.value }}
                        </div>
                        <div class="ml-2 flex items-baseline text-sm font-semibold" :class="currentKpiCard.growthColor">
                          +{{ currentKpiCard.growth }}%
                        </div>
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex justify-between mt-3">
              <button @click="previousKpi" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.previous') }}</button>
              <button @click="nextKpi" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.next') }}</button>
            </div>
          </div>

          <!-- Charts Section -->
          <!-- Desktop Charts -->
          <div class="hidden lg:grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
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

          <!-- Mobile Charts Carousel -->
          <div class="block lg:hidden mb-8">
            <div class="text-sm text-gray-500 mb-2 text-center">
              {{ $t('analytics.showing_chart') }} {{ currentChartIndex + 1 }} {{ $t('common.of') }} {{ charts.length }} — {{ $t('orders.swipe_hint') }}
            </div>
            <div
              class="bg-white shadow rounded-lg select-none"
              @touchstart.passive="handleChartTouchStart"
              @touchmove.prevent="handleChartTouchMove"
              @touchend="handleChartTouchEnd"
              @mousedown.prevent="handleChartMouseDown"
              @mousemove.prevent="handleChartMouseMove"
              @mouseup.prevent="handleChartMouseUp"
              @mouseleave.prevent="handleChartMouseUp"
            >
              <div class="p-6" v-if="currentChart">
                <h3 class="text-lg font-medium text-gray-900 mb-4">{{ currentChart.title }}</h3>
                <div class="h-64 flex items-end justify-between space-x-2">
                  <div v-for="(value, index) in currentChart.data" :key="index" class="flex flex-col items-center">
                    <div
                      class="rounded-t"
                      :class="currentChart.barColor"
                      :style="{ height: (value / Math.max(...currentChart.data)) * 200 + 'px', width: '20px' }"
                    ></div>
                    <span class="text-xs text-gray-500 mt-2">{{ currentChart.formatValue(value) }}</span>
                    <span class="text-xs text-gray-400">{{ getMonthName(index) }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="flex justify-between mt-3">
              <button @click="previousChart" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.previous') }}</button>
              <button @click="nextChart" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.next') }}</button>
            </div>
          </div>

          <!-- Detailed Analytics Tabs -->
          <div class="bg-white shadow rounded-lg">
            <!-- Desktop Tabs -->
            <div class="hidden lg:block border-b border-gray-200">
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

            <!-- Mobile Tab Carousel -->
            <div class="block lg:hidden border-b border-gray-200">
              <div class="text-sm text-gray-500 mb-2 text-center px-6 pt-4">
                {{ $t('analytics.showing_tab') }} {{ currentTabIndex + 1 }} {{ $t('common.of') }} {{ analyticsTabs.length }} — {{ $t('orders.swipe_hint') }}
              </div>
              <div
                class="px-6 pb-4 select-none"
                @touchstart.passive="handleTabTouchStart"
                @touchmove.prevent="handleTabTouchMove"
                @touchend="handleTabTouchEnd"
                @mousedown.prevent="handleTabMouseDown"
                @mousemove.prevent="handleTabMouseMove"
                @mouseup.prevent="handleTabMouseUp"
                @mouseleave.prevent="handleTabMouseUp"
              >
                <div class="bg-primary-50 border border-primary-200 rounded-lg p-4" v-if="currentTab">
                  <h3 class="text-lg font-medium text-primary-900 mb-2">{{ currentTab.name }}</h3>
                  <p class="text-sm text-primary-700">{{ $t(`analytics.tab_descriptions.${currentTab.id}`) }}</p>
                </div>
              </div>
              <div class="flex justify-between px-6 pb-4">
                <button @click="previousTab" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.previous') }}</button>
                <button @click="nextTab" class="px-3 py-2 text-sm bg-gray-100 rounded">{{ $t('common.next') }}</button>
              </div>
            </div>

            <div class="p-6">
              <!-- Production Analytics -->
              <div v-if="activeTab === 'production'" class="space-y-6">
                <!-- Desktop Grid -->
                <div class="hidden lg:grid grid-cols-1 md:grid-cols-3 gap-6">
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

                <!-- Mobile Production Cards -->
                <div class="block lg:hidden space-y-4">
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
import { ref, onMounted, onUnmounted, computed } from 'vue'

// Data
const selectedPeriod = ref('30')
const activeTab = ref('production')

// Carousel indices
const currentKpiIndex = ref(0)
const currentChartIndex = ref(0)
const currentTabIndex = ref(0)

// Touch/Mouse handling
const kpiTouchStartX = ref(0)
const kpiTouchStartY = ref(0)
const kpiIsDragging = ref(false)
const chartTouchStartX = ref(0)
const chartTouchStartY = ref(0)
const chartIsDragging = ref(false)
const tabTouchStartX = ref(0)
const tabTouchStartY = ref(0)
const tabIsDragging = ref(false)

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

// Computed properties for carousels
const kpiCards = computed(() => [
  {
    title: 'Total Revenue',
    value: `₺${formatNumber(totalRevenue.value)}`,
    growth: revenueGrowth.value,
    growthColor: 'text-green-600',
    iconColor: 'text-green-400',
    iconPath: 'M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1'
  },
  {
    title: 'Orders Completed',
    value: completedOrders.value.toString(),
    growth: ordersGrowth.value,
    growthColor: 'text-blue-600',
    iconColor: 'text-blue-400',
    iconPath: 'M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01'
  },
  {
    title: 'Production Efficiency',
    value: `${productionEfficiency.value}%`,
    growth: efficiencyGrowth.value,
    growthColor: 'text-purple-600',
    iconColor: 'text-purple-400',
    iconPath: 'M13 7h8m0 0v8m0-8l-8 8-4-4-6 6'
  },
  {
    title: 'Inventory Value',
    value: `₺${formatNumber(inventoryValue.value)}`,
    growth: inventoryGrowth.value,
    growthColor: 'text-orange-600',
    iconColor: 'text-orange-400',
    iconPath: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4'
  }
])

const charts = computed(() => [
  {
    title: 'Revenue Trend',
    data: revenueData.value,
    barColor: 'bg-primary-500',
    formatValue: (value) => formatNumber(value)
  },
  {
    title: 'Production Output',
    data: productionData.value,
    barColor: 'bg-green-500',
    formatValue: (value) => `${value}kg`
  }
])

const currentKpiCard = computed(() => kpiCards.value[currentKpiIndex.value])
const currentChart = computed(() => charts.value[currentChartIndex.value])
const currentTab = computed(() => analyticsTabs.value[currentTabIndex.value])

// Carousel navigation
function nextKpi () {
  currentKpiIndex.value = (currentKpiIndex.value + 1) % kpiCards.value.length
}

function previousKpi () {
  currentKpiIndex.value = currentKpiIndex.value === 0 ? kpiCards.value.length - 1 : currentKpiIndex.value - 1
}

function nextChart () {
  currentChartIndex.value = (currentChartIndex.value + 1) % charts.value.length
}

function previousChart () {
  currentChartIndex.value = currentChartIndex.value === 0 ? charts.value.length - 1 : currentChartIndex.value - 1
}

function nextTab () {
  currentTabIndex.value = (currentTabIndex.value + 1) % analyticsTabs.value.length
}

function previousTab () {
  currentTabIndex.value = currentTabIndex.value === 0 ? analyticsTabs.value.length - 1 : currentTabIndex.value - 1
}

// Touch/Mouse handlers for KPI
function handleKpiTouchStart (e) {
  const touch = e.touches[0]
  kpiTouchStartX.value = touch.clientX
  kpiTouchStartY.value = touch.clientY
  kpiIsDragging.value = true
}

function handleKpiTouchMove (e) {
  // intentionally left blank (no-op)
}

function handleKpiTouchEnd (e) {
  if (!kpiIsDragging.value) return
  const touch = e.changedTouches[0]
  const dx = touch.clientX - kpiTouchStartX.value
  kpiIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextKpi()
  else if (dx > threshold) previousKpi()
}

function handleKpiMouseDown (e) {
  kpiTouchStartX.value = e.clientX
  kpiTouchStartY.value = e.clientY
  kpiIsDragging.value = true
}

function handleKpiMouseMove (e) {
  // intentionally left blank (no-op)
}

function handleKpiMouseUp (e) {
  if (!kpiIsDragging.value) return
  const dx = e.clientX - kpiTouchStartX.value
  kpiIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextKpi()
  else if (dx > threshold) previousKpi()
}

// Touch/Mouse handlers for Charts
function handleChartTouchStart (e) {
  const touch = e.touches[0]
  chartTouchStartX.value = touch.clientX
  chartTouchStartY.value = touch.clientY
  chartIsDragging.value = true
}

function handleChartTouchMove (e) {
  // intentionally left blank (no-op)
}

function handleChartTouchEnd (e) {
  if (!chartIsDragging.value) return
  const touch = e.changedTouches[0]
  const dx = touch.clientX - chartTouchStartX.value
  chartIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextChart()
  else if (dx > threshold) previousChart()
}

function handleChartMouseDown (e) {
  chartTouchStartX.value = e.clientX
  chartTouchStartY.value = e.clientY
  chartIsDragging.value = true
}

function handleChartMouseMove (e) {
  // intentionally left blank (no-op)
}

function handleChartMouseUp (e) {
  if (!chartIsDragging.value) return
  const dx = e.clientX - chartTouchStartX.value
  chartIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextChart()
  else if (dx > threshold) previousChart()
}

// Touch/Mouse handlers for Tabs
function handleTabTouchStart (e) {
  const touch = e.touches[0]
  tabTouchStartX.value = touch.clientX
  tabTouchStartY.value = touch.clientY
  tabIsDragging.value = true
}

function handleTabTouchMove (e) {
  // intentionally left blank (no-op)
}

function handleTabTouchEnd (e) {
  if (!tabIsDragging.value) return
  const touch = e.changedTouches[0]
  const dx = touch.clientX - tabTouchStartX.value
  tabIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextTab()
  else if (dx > threshold) previousTab()
}

function handleTabMouseDown (e) {
  tabTouchStartX.value = e.clientX
  tabTouchStartY.value = e.clientY
  tabIsDragging.value = true
}

function handleTabMouseMove (e) {
  // intentionally left blank (no-op)
}

function handleTabMouseUp (e) {
  if (!tabIsDragging.value) return
  const dx = e.clientX - tabTouchStartX.value
  tabIsDragging.value = false
  const threshold = 40
  if (dx < -threshold) nextTab()
  else if (dx > threshold) previousTab()
}

// ESC key handler
function handleKeydown (event) {
  if (event.key === 'Escape') {
    // Close any modals if they exist
    // For now, just prevent default behavior
    event.preventDefault()
  }
}

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
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>
