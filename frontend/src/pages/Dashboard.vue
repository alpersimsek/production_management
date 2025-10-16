<template>
  <div>
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
                <h1 class="text-3xl font-bold text-gray-900">{{ $t('dashboard.title') }}</h1>
      </div>
    </header>

    <main>
      <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="px-4 py-6 sm:px-0">
          <div class="border-4 border-dashed border-gray-200 rounded-lg h-96 p-4">
                    <h2 class="text-2xl font-semibold text-gray-800 mb-4">{{ $t('dashboard.welcome') }}, {{ authStore.user?.full_name || authStore.user?.email }}!</h2>

            <!-- Metrics Cards -->
            <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
              <div class="bg-white overflow-hidden shadow rounded-lg">
                <div class="p-5">
                  <div class="flex items-center">
                    <div class="flex-shrink-0">
                      <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path></svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                      <dl>
                                <dt class="text-sm font-medium text-gray-500 truncate">{{ $t('dashboard.metrics.orders') }}</dt>
                        <dd class="flex items-baseline">
                          <div class="text-2xl font-semibold text-gray-900">
                            24
                          </div>
                          <div class="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                            +10%
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
                      <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                      <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">{{ $t('dashboard.metrics.production_jobs') }}</dt>
                        <dd class="flex items-baseline">
                          <div class="text-2xl font-semibold text-gray-900">
                            12
                          </div>
                          <div class="ml-2 flex items-baseline text-sm font-semibold text-red-600">
                            -5%
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
                      <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4"></path></svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                      <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">{{ $t('dashboard.metrics.inventory_items') }}</dt>
                        <dd class="flex items-baseline">
                          <div class="text-2xl font-semibold text-gray-900">
                            156
                          </div>
                          <div class="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                            +20%
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
                      <svg class="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 4H6a2 2 0 00-2 2v12a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-2m-4-1v8m0-8H8m-4 0h.01M16 4v8m0-8h-2m-4 6h4m-4 4h4m-6 0h.01"></path></svg>
                    </div>
                    <div class="ml-5 w-0 flex-1">
                      <dl>
                        <dt class="text-sm font-medium text-gray-500 truncate">{{ $t('dashboard.metrics.shipments') }}</dt>
                        <dd class="flex items-baseline">
                          <div class="text-2xl font-semibold text-gray-900">
                            8
                          </div>
                          <div class="ml-2 flex items-baseline text-sm font-semibold text-green-600">
                            +15%
                          </div>
                        </dd>
                      </dl>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quick Actions -->
            <div class="mb-8">
                    <h3 class="text-xl font-semibold text-gray-800 mb-3">{{ $t('dashboard.quick_actions') }}</h3>
              <div class="flex flex-wrap gap-4">
                <router-link to="/orders" class="bg-primary-500 hover:bg-primary-600 text-white font-bold py-2 px-4 rounded-lg shadow-md">
                  {{ $t('dashboard.new_order') }}
                </router-link>
                <router-link to="/production-jobs" class="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg shadow-md">
                  {{ $t('dashboard.start_production') }}
                </router-link>
                <router-link to="/warehouses" class="bg-yellow-500 hover:bg-yellow-600 text-white font-bold py-2 px-4 rounded-lg shadow-md">
                  {{ $t('dashboard.manage_inventory') }}
                </router-link>
                <router-link to="/shipments" class="bg-indigo-500 hover:bg-indigo-600 text-white font-bold py-2 px-4 rounded-lg shadow-md">
                  {{ $t('dashboard.track_shipment') }}
                </router-link>
              </div>
            </div>

            <!-- Recent Activity -->
            <div class="mb-8">
              <h3 class="text-xl font-semibold text-gray-800 mb-3">{{ $t('dashboard.recent_activity') }}</h3>
              <div class="bg-white rounded-lg shadow p-4">
                <div class="space-y-3">
                  <div class="flex items-center space-x-3">
                    <div class="w-2 h-2 bg-green-400 rounded-full"></div>
                    <span class="text-sm text-gray-600">{{ $t('dashboard.activity.order_created', { orderNumber: '#ORD-20241201-0001' }) }}</span>
                    <span class="text-xs text-gray-400">{{ $t('dashboard.time.hours_ago', { hours: 2 }) }}</span>
                  </div>
                  <div class="flex items-center space-x-3">
                    <div class="w-2 h-2 bg-blue-400 rounded-full"></div>
                    <span class="text-sm text-gray-600">{{ $t('dashboard.activity.production_started', { jobNumber: '#PJ-001' }) }}</span>
                    <span class="text-xs text-gray-400">{{ $t('dashboard.time.hours_ago', { hours: 4 }) }}</span>
                  </div>
                  <div class="flex items-center space-x-3">
                    <div class="w-2 h-2 bg-yellow-400 rounded-full"></div>
                    <span class="text-sm text-gray-600">{{ $t('dashboard.activity.receipt_approved', { receiptNumber: '#WR-001' }) }}</span>
                    <span class="text-xs text-gray-400">{{ $t('dashboard.time.hours_ago', { hours: 6 }) }}</span>
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
import { useAuthStore } from '@/store/auth'

const authStore = useAuthStore()
</script>
