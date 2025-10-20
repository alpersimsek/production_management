<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 via-white to-secondary-50">
    <!-- Background Pattern -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-10 -right-10 w-16 h-16 sm:w-32 sm:h-32 lg:w-48 lg:h-48 bg-primary-100 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
      <div class="absolute -bottom-10 -left-10 w-16 h-16 sm:w-32 sm:h-32 lg:w-48 lg:h-48 bg-secondary-100 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
      <div class="absolute top-10 left-10 w-16 h-16 sm:w-32 sm:h-32 lg:w-48 lg:h-48 bg-success-100 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
    </div>

    <!-- Main Content -->
    <div class="relative z-10 p-2 sm:p-4 lg:p-6">
      <!-- Welcome Header -->
      <div class="mb-3 sm:mb-4 lg:mb-6">
        <div class="bg-white/90 backdrop-blur-sm rounded-lg sm:rounded-xl lg:rounded-2xl shadow-lg border border-white/30 p-3 sm:p-4 lg:p-6">
          <div class="text-center sm:text-left">
            <h1 class="text-base sm:text-lg lg:text-xl font-bold text-secondary-900 mb-1">
              {{ $t('dashboard.welcome_user', { name: authStore.user?.full_name || authStore.user?.email || 'User' }) }}
            </h1>
            <p class="text-xs sm:text-sm text-secondary-600">
              {{ currentDateTime }}
            </p>
          </div>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="grid grid-cols-2 gap-2 sm:gap-3 lg:gap-4 mb-3 sm:mb-4 lg:mb-6">
        <div
          v-for="(stat, index) in stats"
          :key="stat.name"
          class="group bg-white/90 backdrop-blur-sm rounded-lg sm:rounded-xl shadow-md border border-white/30 p-2 sm:p-3 lg:p-4 hover:shadow-lg transition-all duration-200"
          :style="{ animationDelay: `${index * 50}ms` }"
        >
          <div class="text-center">
            <div :class="stat.iconBg" class="w-8 h-8 sm:w-10 sm:h-10 lg:w-12 lg:h-12 rounded-lg sm:rounded-xl mx-auto mb-2 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
              <component :is="stat.icon" :class="stat.iconColor" class="w-4 h-4 sm:w-5 sm:h-5 lg:w-6 lg:h-6" />
            </div>
            <p class="text-xs sm:text-sm font-medium text-secondary-600 mb-1 truncate">{{ stat.name }}</p>
            <p class="text-lg sm:text-xl lg:text-2xl font-bold text-secondary-900 mb-1">{{ stat.value }}</p>
            <div :class="stat.changeColor" class="flex items-center justify-center text-xs font-medium">
              <svg class="w-3 h-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 11l5-5m0 0l5 5m-5-5v12" />
              </svg>
              {{ stat.change }}
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content -->
      <div class="space-y-3 sm:space-y-4 lg:space-y-6">
        <!-- Recent Orders -->
        <div class="bg-white/90 backdrop-blur-sm rounded-lg sm:rounded-xl lg:rounded-2xl shadow-lg border border-white/30 overflow-hidden">
          <div class="p-3 sm:p-4 lg:p-6 border-b border-secondary-200/50">
            <div class="flex items-center justify-between mb-2">
              <div>
                <h3 class="text-sm sm:text-base lg:text-lg font-bold text-secondary-900">{{ $t('dashboard.recent_orders') }}</h3>
                <p class="text-xs sm:text-sm text-secondary-600">{{ $t('dashboard.latest_customer_orders') }}</p>
              </div>
              <BaseButton
                variant="ghost"
                size="sm"
                class="text-xs"
                @click="router.push('/orders')"
              >
                {{ $t('common.view_all') }}
              </BaseButton>
            </div>
          </div>
          <div class="p-3 sm:p-4 lg:p-6">
            <!-- Mobile Card Layout -->
            <div class="space-y-2 sm:space-y-3">
              <div
                v-for="(order, index) in recentOrders.slice(0, 3)"
                :key="order.id"
                class="bg-gradient-to-r from-secondary-50/50 to-secondary-100/50 rounded-lg p-3 border border-secondary-200/50"
                :style="{ animationDelay: `${index * 50}ms` }"
              >
                <div class="flex justify-between items-start mb-2">
                  <div class="flex-1">
                    <p class="text-sm font-semibold text-secondary-900">#{{ order.id }}</p>
                    <p class="text-xs text-secondary-600 truncate">{{ order.customer }}</p>
                  </div>
                  <span :class="getStatusClasses(order.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full ml-2">
                    {{ order.status }}
                  </span>
                </div>
                <div class="flex justify-between items-center">
                  <p class="text-sm font-semibold text-secondary-900">₺{{ order.amount.toLocaleString() }}</p>
                  <p class="text-xs text-secondary-600">{{ formatDate(order.date) }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white/90 backdrop-blur-sm rounded-lg sm:rounded-xl lg:rounded-2xl shadow-lg border border-white/30 overflow-hidden">
          <div class="p-3 sm:p-4 lg:p-6 border-b border-secondary-200/50">
            <h3 class="text-sm sm:text-base lg:text-lg font-bold text-secondary-900">{{ $t('dashboard.quick_actions') }}</h3>
            <p class="text-xs sm:text-sm text-secondary-600">{{ $t('dashboard.common_tasks') }}</p>
          </div>
          <div class="p-3 sm:p-4 lg:p-6">
            <div class="grid grid-cols-2 gap-2 sm:gap-3">
              <BaseButton
                v-for="(action, index) in quickActions.slice(0, 4)"
                :key="action.name"
                :variant="action.variant"
                :icon="action.icon"
                full-width
                size="sm"
                class="group hover:scale-105 transition-transform duration-200 text-xs sm:text-sm py-2"
                :style="{ animationDelay: `${index * 50}ms` }"
                @click="action.action"
              >
                {{ action.name }}
              </BaseButton>
            </div>
          </div>
        </div>

        <!-- Production Status -->
        <div class="bg-white/90 backdrop-blur-sm rounded-lg sm:rounded-xl lg:rounded-2xl shadow-lg border border-white/30 overflow-hidden">
          <div class="p-3 sm:p-4 lg:p-6 border-b border-secondary-200/50">
            <h3 class="text-sm sm:text-base lg:text-lg font-bold text-secondary-900">{{ $t('dashboard.production_status') }}</h3>
            <p class="text-xs sm:text-sm text-secondary-600">{{ $t('dashboard.current_operations') }}</p>
          </div>
          <div class="p-3 sm:p-4 lg:p-6">
            <div class="space-y-3">
              <div
                v-for="(job, index) in productionJobs"
                :key="job.id"
                class="bg-gradient-to-r from-secondary-50/50 to-secondary-100/50 rounded-lg p-3 border border-secondary-200/50"
                :style="{ animationDelay: `${index * 50}ms` }"
              >
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center flex-1">
                    <div class="w-2 h-2 sm:w-3 sm:h-3 rounded-full bg-success-500 mr-2 animate-pulse"></div>
                    <div class="flex-1">
                      <p class="text-xs sm:text-sm font-semibold text-secondary-900 truncate">{{ job.name }}</p>
                      <p class="text-xs text-secondary-600">{{ job.progress }}% {{ $t('dashboard.complete') }}</p>
                    </div>
                  </div>
                  <div class="text-right ml-2">
                    <p class="text-xs sm:text-sm font-bold text-secondary-900">{{ job.quantity }}</p>
                    <p class="text-xs text-secondary-600">{{ $t('dashboard.units') }}</p>
                  </div>
                </div>
                <div class="w-full bg-secondary-200 rounded-full h-1.5 sm:h-2">
                  <div
                    class="bg-gradient-to-r from-success-500 to-success-600 h-1.5 sm:h-2 rounded-full transition-all duration-1000"
                    :style="{ width: `${job.progress}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Charts Section -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-4 lg:gap-6">
          <div class="bg-white/90 backdrop-blur-sm rounded-lg sm:rounded-xl lg:rounded-2xl shadow-lg border border-white/30 overflow-hidden">
            <div class="p-3 sm:p-4 lg:p-6 border-b border-secondary-200/50">
              <h3 class="text-sm sm:text-base lg:text-lg font-bold text-secondary-900">{{ $t('dashboard.sales_overview') }}</h3>
              <p class="text-xs sm:text-sm text-secondary-600">{{ $t('dashboard.monthly_sales_performance') }}</p>
            </div>
            <div class="p-3 sm:p-4 lg:p-6">
              <div class="h-24 sm:h-32 lg:h-40 xl:h-48 flex items-center justify-center bg-gradient-to-br from-primary-50/50 to-primary-100/50 rounded-lg border border-primary-200/50">
                <div class="text-center">
                  <svg class="w-6 h-6 sm:w-8 sm:h-8 lg:w-12 lg:h-12 text-primary-400 mx-auto mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  <p class="text-xs sm:text-sm text-secondary-500">{{ $t('dashboard.chart_placeholder_sales') }}</p>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white/90 backdrop-blur-sm rounded-lg sm:rounded-xl lg:rounded-2xl shadow-lg border border-white/30 overflow-hidden">
            <div class="p-3 sm:p-4 lg:p-6 border-b border-secondary-200/50">
              <h3 class="text-sm sm:text-base lg:text-lg font-bold text-secondary-900">{{ $t('dashboard.production_efficiency') }}</h3>
              <p class="text-xs sm:text-sm text-secondary-600">{{ $t('dashboard.manufacturing_performance') }}</p>
            </div>
            <div class="p-3 sm:p-4 lg:p-6">
              <div class="h-24 sm:h-32 lg:h-40 xl:h-48 flex items-center justify-center bg-gradient-to-br from-success-50/50 to-success-100/50 rounded-lg border border-success-200/50">
                <div class="text-center">
                  <svg class="w-6 h-6 sm:w-8 sm:h-8 lg:w-12 lg:h-12 text-success-400 mx-auto mb-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  <p class="text-xs sm:text-sm text-secondary-500">{{ $t('dashboard.chart_placeholder_production') }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '@/store/auth'
import BaseButton from '@/components/ui/BaseButton.vue'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

// Current date and time
const currentDateTime = computed(() => {
  return new Intl.DateTimeFormat('tr-TR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date())
})

// Stats data
const stats = ref([
  {
    name: t('dashboard.total_orders'),
    value: '1,234',
    change: '+12%',
    changeColor: 'text-success-600',
    period: t('dashboard.this_month'),
    icon: 'DocumentTextIcon',
    iconBg: 'bg-primary-100',
    iconColor: 'text-primary-600'
  },
  {
    name: t('dashboard.active_production'),
    value: '8',
    change: '+2%',
    changeColor: 'text-success-600',
    period: t('dashboard.this_week'),
    icon: 'CogIcon',
    iconBg: 'bg-success-100',
    iconColor: 'text-success-600'
  },
  {
    name: t('dashboard.pending_shipments'),
    value: '23',
    change: '-5%',
    changeColor: 'text-error-600',
    period: t('dashboard.this_week'),
    icon: 'TruckIcon',
    iconBg: 'bg-warning-100',
    iconColor: 'text-warning-600'
  },
  {
    name: t('dashboard.revenue'),
    value: '₺2.4M',
    change: '+18%',
    changeColor: 'text-success-600',
    period: t('dashboard.this_month'),
    icon: 'CurrencyDollarIcon',
    iconBg: 'bg-secondary-100',
    iconColor: 'text-secondary-600'
  }
])

// Recent orders data
const recentOrders = ref([
  {
    id: 'ORD-001',
    customer: 'ABC Kimya Ltd.',
    status: 'Processing',
    amount: 45000,
    date: new Date('2024-01-15')
  },
  {
    id: 'ORD-002',
    customer: 'XYZ Deterjan A.Ş.',
    status: 'Shipped',
    amount: 32000,
    date: new Date('2024-01-14')
  },
  {
    id: 'ORD-003',
    customer: 'DEF Temizlik Ürünleri',
    status: 'Delivered',
    amount: 28000,
    date: new Date('2024-01-13')
  },
  {
    id: 'ORD-004',
    customer: 'GHI Kimya San.',
    status: 'Pending',
    amount: 55000,
    date: new Date('2024-01-12')
  }
])

// Quick actions
const quickActions = ref([
  {
    name: t('dashboard.new_order'),
    variant: 'primary',
    icon: 'PlusIcon',
    action: () => router.push('/orders')
  },
  {
    name: t('dashboard.add_customer'),
    variant: 'secondary',
    icon: 'UserPlusIcon',
    action: () => router.push('/customers')
  },
  {
    name: t('dashboard.start_production'),
    variant: 'success',
    icon: 'PlayIcon',
    action: () => router.push('/production-jobs')
  },
  {
    name: t('dashboard.view_analytics'),
    variant: 'ghost',
    icon: 'ChartBarIcon',
    action: () => router.push('/analytics')
  }
])

// Production jobs
const productionJobs = ref([
  {
    id: 1,
    name: 'Poşet Deterjan',
    progress: 75,
    quantity: 500
  },
  {
    id: 2,
    name: 'Sıvı Deterjan',
    progress: 45,
    quantity: 300
  },
  {
    id: 3,
    name: 'Çamaşır Suyu',
    progress: 90,
    quantity: 200
  }
])

const getStatusClasses = (status) => {
  const classes = {
    Pending: 'bg-warning-100 text-warning-800',
    Processing: 'bg-primary-100 text-primary-800',
    Shipped: 'bg-secondary-100 text-secondary-800',
    Delivered: 'bg-success-100 text-success-800'
  }
  return classes[status] || 'bg-secondary-100 text-secondary-800'
}

const formatDate = (date) => {
  return new Intl.DateTimeFormat('tr-TR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  }).format(date)
}

onMounted(() => {
  // Load dashboard data
  console.log('Dashboard loaded')
})
</script>
