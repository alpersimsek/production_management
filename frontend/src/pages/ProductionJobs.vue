<template>
  <div>
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-gray-900">{{ $t('production.title') }}</h1>
          <button
            @click="showAddModal = true"
            class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            {{ $t('production.new_job') }}
          </button>
        </div>
      </div>
    </header>

    <main>
      <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="px-4 py-6 sm:px-0">
          <!-- Search and Filters -->
          <div class="mb-6">
            <div class="flex flex-col sm:flex-row gap-4">
              <div class="flex-1">
                <input
                  v-model="searchQuery"
                  type="text"
                  :placeholder="$t('production.search_placeholder')"
                  class="input-field"
                />
              </div>
              <div class="flex gap-2">
                <select v-model="statusFilter" class="input-field">
                  <option value="">{{ $t('production.all_status') }}</option>
                  <option value="pending">{{ $t('production.status.pending') }}</option>
                  <option value="scheduled">{{ $t('production.status.scheduled') }}</option>
                  <option value="in_progress">{{ $t('production.status.in_progress') }}</option>
                  <option value="paused">{{ $t('production.status.paused') }}</option>
                  <option value="completed">{{ $t('production.status.completed') }}</option>
                  <option value="cancelled">{{ $t('production.status.cancelled') }}</option>
                </select>
                <select v-model="productFilter" class="input-field">
                  <option value="">{{ $t('production.all_products') }}</option>
                  <option v-for="product in products" :key="product.id" :value="product.id">
                    {{ product.name }}
                  </option>
                </select>
                <select v-model="priorityFilter" class="input-field">
                  <option value="">{{ $t('production.all_priorities') }}</option>
                  <option value="low">{{ $t('production.priority.low') }}</option>
                  <option value="medium">{{ $t('production.priority.medium') }}</option>
                  <option value="high">{{ $t('production.priority.high') }}</option>
                  <option value="urgent">{{ $t('production.priority.urgent') }}</option>
                </select>
                <button
                  @click="loadProductionJobs"
                  class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  {{ $t('common.refresh') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Production Jobs Table / Cards -->
          <div class="bg-white shadow overflow-hidden sm:rounded-md">
            <div v-if="loading" class="p-6 text-center">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p class="mt-2 text-gray-600">{{ $t('production.loading') }}</p>
            </div>

            <div v-else-if="productionJobs.length === 0" class="p-6 text-center text-gray-500">
              {{ $t('production.no_jobs_found') }}
            </div>

            <!-- Desktop Table -->
            <div v-if="productionJobs.length > 0" class="hidden lg:block overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('production.job_number') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('production.product') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('production.order') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.quantity') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.status') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('production.priority_label') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('production.start_date') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('production.progress') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('production.operator') }}
                    </th>
                    <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.actions') }}
                    </th>
                  </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                  <tr v-for="job in filteredJobs" :key="job.id" class="hover:bg-gray-50">
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {{ job.job_number }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {{ job.product_name }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ job.order_number }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ job.quantity }} {{ job.unit }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="getStatusColor(job.status)"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      >
                        {{ $t(`production.status.${job.status}`) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="getPriorityColor(job.priority)"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      >
                        {{ $t(`production.priority.${job.priority}`) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ formatDate(job.start_date) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <div class="flex items-center">
                        <div class="w-full bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            :class="getProgressColor(job.progress)"
                            class="h-2 rounded-full transition-all duration-300"
                            :style="{ width: job.progress + '%' }"
                          ></div>
                        </div>
                        <span class="text-sm text-gray-600">{{ job.progress }}%</span>
                      </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ job.operator_name || '-' }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        @click="viewJob(job)"
                        class="text-blue-600 hover:text-blue-900 mr-3"
                      >
                        {{ $t('common.view') }}
                      </button>
                      <button
                        @click="editJob(job)"
                        class="text-primary-600 hover:text-primary-900 mr-3"
                      >
                        {{ $t('common.edit') }}
                      </button>
                      <button
                        v-if="job.status === 'pending' || job.status === 'scheduled'"
                        @click="startJob(job)"
                        class="text-green-600 hover:text-green-900 mr-3"
                      >
                        {{ $t('production.start') }}
                      </button>
                      <button
                        v-if="job.status === 'in_progress'"
                        @click="pauseJob(job)"
                        class="text-yellow-600 hover:text-yellow-900 mr-3"
                      >
                        {{ $t('production.pause') }}
                      </button>
                      <button
                        v-if="job.status === 'paused'"
                        @click="resumeJob(job)"
                        class="text-green-600 hover:text-green-900 mr-3"
                      >
                        {{ $t('production.resume') }}
                      </button>
                      <button
                        v-if="job.status === 'in_progress' || job.status === 'paused'"
                        @click="completeJob(job)"
                        class="text-green-600 hover:text-green-900 mr-3"
                      >
                        {{ $t('production.complete') }}
                      </button>
                      <button
                        @click="deleteJob(job)"
                        class="text-red-600 hover:text-red-900"
                      >
                        {{ $t('common.delete') }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Mobile Cards - Carousel -->
            <div v-if="productionJobs.length > 0" class="block lg:hidden p-4">
              <div v-if="filteredJobs.length > 0" class="space-y-3">
                <!-- Header with counter and nav -->
                <div class="flex items-center justify-between">
                  <div class="text-sm text-gray-500">
                    {{ $t('production.showing_job') }} {{ currentJobIndex + 1 }} {{ $t('common.of') }} {{ filteredJobs.length }}
                  </div>
                  <div class="flex space-x-2">
                    <button @click="previousJob" :disabled="currentJobIndex === 0" class="p-2 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
                      </svg>
                    </button>
                    <button @click="nextJob" :disabled="currentJobIndex >= filteredJobs.length - 1" class="p-2 rounded-full bg-gray-100 hover:bg-gray-200 disabled:opacity-50">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                      </svg>
                    </button>
                  </div>
                </div>

                <!-- Swipe hint -->
                <div class="text-center text-xs text-gray-400">{{ $t('production.swipe_hint') }}</div>

                <!-- Card -->
                <div
                  v-if="currentJob"
                  @touchstart.stop="handleJobTouchStart"
                  @touchmove.prevent.stop="handleJobTouchMove"
                  @touchend.stop="handleJobTouchEnd"
                  @mousedown="handleJobMouseDown"
                  @mousemove="handleJobMouseMove"
                  @mouseup="handleJobMouseUp"
                  @mouseleave="handleJobMouseUp"
                  class="bg-white rounded-lg border border-gray-200 shadow-sm p-4 select-none cursor-grab active:cursor-grabbing"
                >
                  <div class="flex items-center justify-between mb-2">
                    <h3 class="text-base font-semibold text-gray-900">#{{ currentJob.job_number }}</h3>
                    <span :class="getStatusColor(currentJob.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">{{ $t('production.status.' + currentJob.status) }}</span>
                  </div>
                  <div class="grid grid-cols-1 gap-2 text-sm">
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('production.product') }}:</span><span class="text-gray-900">{{ currentJob.product_name }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('production.order') }}:</span><span class="text-gray-900">{{ currentJob.order_number }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('common.quantity') }}:</span><span class="text-gray-900">{{ currentJob.quantity }} {{ currentJob.unit }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('production.priority_label') }}:</span><span :class="getPriorityColor(currentJob.priority)" class="px-2 py-0.5 rounded text-xs font-medium">{{ $t('production.priority.' + currentJob.priority) }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('common.start_date') }}:</span><span class="text-gray-900">{{ currentJob.start_date }}</span></div>
                    <div class="flex justify-between"><span class="text-gray-500">{{ $t('production.expected_end_date') }}:</span><span class="text-gray-900">{{ currentJob.expected_end_date }}</span></div>
                  </div>
                  <div class="flex justify-end space-x-2 mt-3 pt-3 border-t border-gray-100">
                    <button @click="viewJob(currentJob)" class="px-3 py-1 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700">{{ $t('common.view') }}</button>
                    <button @click="editJob(currentJob)" class="px-3 py-1 text-sm bg-primary-600 text-white rounded-md hover:bg-primary-700">{{ $t('common.edit') }}</button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Pagination -->
          <div class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4">
            <div class="flex-1 flex justify-between sm:hidden">
              <button
                @click="previousPage"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                {{ $t('common.previous') }}
              </button>
              <button
                @click="nextPage"
                :disabled="currentPage === totalPages"
                class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                {{ $t('common.next') }}
              </button>
            </div>
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p class="text-sm text-gray-700">
                  {{ $t('common.showing') }}
                  <span class="font-medium">{{ (currentPage - 1) * itemsPerPage + 1 }}</span>
                  {{ $t('common.to') }}
                  <span class="font-medium">{{ Math.min(currentPage * itemsPerPage, totalJobs) }}</span>
                  {{ $t('common.of') }}
                  <span class="font-medium">{{ totalJobs }}</span>
                  {{ $t('common.results') }}
                </p>
              </div>
              <div>
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    @click="previousPage"
                    :disabled="currentPage === 1"
                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    {{ $t('common.previous') }}
                  </button>
                  <button
                    v-for="page in visiblePages"
                    :key="page"
                    @click="goToPage(page)"
                    :class="[
                      'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                      page === currentPage
                        ? 'z-10 bg-primary-50 border-primary-500 text-primary-600'
                        : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                    ]"
                  >
                    {{ page }}
                  </button>
                  <button
                    @click="nextPage"
                    :disabled="currentPage === totalPages"
                    class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    {{ $t('common.next') }}
                  </button>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add/Edit Production Job Modal -->
    <div v-if="showAddModal || showEditModal" @click="closeModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div @click.stop class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ showAddModal ? $t('production.new_job') : $t('production.edit_job') }}
            </h3>
            <button
              @click="closeModal"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <form @submit.prevent="saveJob" class="space-y-6">
            <!-- Job Basic Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('production.order') }} *</label>
                <select v-model="jobForm.order_id" required class="input-field mt-1">
                  <option value="">{{ $t('production.select_order') }}</option>
                  <option v-for="order in orders" :key="order.id" :value="order.id">
                    {{ order.order_number }} - {{ order.customer_name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('production.product') }} *</label>
                <select v-model="jobForm.product_id" required class="input-field mt-1">
                  <option value="">{{ $t('production.select_product') }}</option>
                  <option v-for="product in products" :key="product.id" :value="product.id">
                    {{ product.name }} ({{ product.code }})
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('common.quantity') }} *</label>
                <input
                  v-model.number="jobForm.quantity"
                  type="number"
                  min="1"
                  step="0.01"
                  required
                  class="input-field mt-1"
                  placeholder="0"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('production.unit') }}</label>
                <input
                  v-model="jobForm.unit"
                  type="text"
                  readonly
                  class="input-field mt-1 bg-gray-50"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('production.priority_label') }} *</label>
                <select v-model="jobForm.priority" required class="input-field mt-1">
                  <option value="">{{ $t('production.select_priority') }}</option>
                  <option value="low">{{ $t('production.priority.low') }}</option>
                  <option value="medium">{{ $t('production.priority.medium') }}</option>
                  <option value="high">{{ $t('production.priority.high') }}</option>
                  <option value="urgent">{{ $t('production.priority.urgent') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('common.status') }} *</label>
                <select v-model="jobForm.status" required class="input-field mt-1">
                  <option value="">{{ $t('production.select_status') }}</option>
                  <option value="pending">{{ $t('production.status.pending') }}</option>
                  <option value="scheduled">{{ $t('production.status.scheduled') }}</option>
                  <option value="in_progress">{{ $t('production.status.in_progress') }}</option>
                  <option value="paused">{{ $t('production.status.paused') }}</option>
                  <option value="completed">{{ $t('production.status.completed') }}</option>
                  <option value="cancelled">{{ $t('production.status.cancelled') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('production.start_date') }}</label>
                <input
                  v-model="jobForm.start_date"
                  type="datetime-local"
                  class="input-field mt-1"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('production.expected_end_date') }}</label>
                <input
                  v-model="jobForm.expected_end_date"
                  type="datetime-local"
                  class="input-field mt-1"
                />
              </div>
            </div>

            <!-- Production Details -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('production.production_details') }}</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('production.machine_line') }}</label>
                  <select v-model="jobForm.machine_id" class="input-field mt-1">
                    <option value="">{{ $t('production.select_machine') }}</option>
                    <option v-for="machine in machines" :key="machine.id" :value="machine.id">
                      {{ machine.name }} - {{ machine.type }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('production.operator') }}</label>
                  <select v-model="jobForm.operator_id" class="input-field mt-1">
                    <option value="">{{ $t('production.select_operator') }}</option>
                    <option v-for="operator in operators" :key="operator.id" :value="operator.id">
                      {{ operator.name }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('production.formula_version') }}</label>
                  <select v-model="jobForm.formula_id" class="input-field mt-1">
                    <option value="">{{ $t('production.select_formula') }}</option>
                    <option v-for="formula in formulas" :key="formula.id" :value="formula.id">
                      {{ formula.version }} ({{ formula.name }})
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('production.batch_size') }}</label>
                  <input
                    v-model.number="jobForm.batch_size"
                    type="number"
                    min="1"
                    step="0.01"
                    class="input-field mt-1"
                    placeholder="0"
                  />
                </div>
              </div>
            </div>

            <!-- Quality Control -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('production.quality_control') }}</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('production.quality_check_required') }}</label>
                  <div class="mt-2">
                    <label class="flex items-center">
                      <input
                        v-model="jobForm.quality_check_required"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">{{ $t('production.required') }}</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('production.sample_size') }}</label>
                  <input
                    v-model.number="jobForm.sample_size"
                    type="number"
                    min="0"
                    step="1"
                    class="input-field mt-1"
                    placeholder="0"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('production.tolerance') }} (%)</label>
                  <input
                    v-model.number="jobForm.tolerance"
                    type="number"
                    min="0"
                    max="100"
                    step="0.01"
                    class="input-field mt-1"
                    placeholder="0.00"
                  />
                </div>
              </div>
            </div>

            <!-- Notes -->
            <div>
              <label class="block text-sm font-medium text-gray-700">{{ $t('common.notes') }}</label>
              <textarea
                v-model="jobForm.notes"
                class="input-field mt-1"
                rows="3"
                :placeholder="$t('production.notes_placeholder')"
              ></textarea>
            </div>

            <!-- Actions -->
            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="closeModal"
                class="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md text-sm font-medium"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                type="submit"
                :disabled="saving"
                class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
              >
                {{ saving ? $t('production.saving') : $t('production.save_job') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Job Details Modal -->
    <div v-if="showDetailsModal" @click="showDetailsModal = false" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div @click.stop class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ $t('production.job_details_title') }} - {{ selectedJob?.job_number }}
            </h3>
            <button
              @click="showDetailsModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <div v-if="selectedJob" class="space-y-6">
            <!-- Job Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('production.job_information') }}</h4>
                <dl class="space-y-2">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('production.job_number') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.job_number }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('production.product') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.product_name }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('production.order') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.order_number }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('common.quantity') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.quantity }} {{ selectedJob.unit }}</dd>
                  </div>
                </dl>
              </div>

              <div>
                <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('production.status_progress') }}</h4>
                <dl class="space-y-2">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('common.status') }}:</dt>
                    <dd class="text-sm">
                      <span :class="getStatusColor(selectedJob.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                        {{ $t(`production.status.${selectedJob.status}`) }}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('production.priority_label') }}:</dt>
                    <dd class="text-sm">
                      <span :class="getPriorityColor(selectedJob.priority)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                        {{ $t(`production.priority.${selectedJob.priority}`) }}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('production.progress') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.progress }}%</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('production.operator') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.operator_name || '-' }}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <!-- Progress Bar -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('production.production_progress') }}</h4>
              <div class="w-full bg-gray-200 rounded-full h-4">
                <div
                  :class="getProgressColor(selectedJob.progress)"
                  class="h-4 rounded-full transition-all duration-300"
                  :style="{ width: selectedJob.progress + '%' }"
                ></div>
              </div>
              <p class="text-sm text-gray-600 mt-2">{{ selectedJob.progress }}% {{ $t('production.completed_text') }}</p>
            </div>

            <!-- Production Timeline -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('production.production_timeline') }}</h4>
              <div class="space-y-4">
                <div class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-green-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('production.job_created') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedJob.created_at) }}</p>
                  </div>
                </div>
                <div v-if="selectedJob.start_date" class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-blue-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('production.production_started') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedJob.start_date) }}</p>
                  </div>
                </div>
                <div v-if="selectedJob.expected_end_date" class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-gray-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('production.expected_completion') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedJob.expected_end_date) }}</p>
                  </div>
                </div>
                <div v-if="selectedJob.completed_at" class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-green-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('production.production_completed') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedJob.completed_at) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quality Control -->
            <div v-if="selectedJob.quality_check_required">
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('production.quality_control') }}</h4>
              <div class="bg-gray-50 p-4 rounded-lg">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('production.sample_size') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedJob.sample_size || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('production.tolerance') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedJob.tolerance ? selectedJob.tolerance + '%' : '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('production.quality_status') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedJob.quality_status || $t('production.pending_status') }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Notes -->
            <div v-if="selectedJob.notes">
              <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('common.notes') }}</h4>
              <p class="text-sm text-gray-700 bg-gray-50 p-3 rounded-lg">{{ selectedJob.notes }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'

// Data
const productionJobs = ref([])
const orders = ref([])
const products = ref([])
const machines = ref([])
const operators = ref([])
const formulas = ref([])
const loading = ref(false)
const saving = ref(false)
const searchQuery = ref('')
const statusFilter = ref('')
const productFilter = ref('')
const priorityFilter = ref('')
const showAddModal = ref(false)
const showEditModal = ref(false)
const showDetailsModal = ref(false)
const editingJob = ref(null)
const selectedJob = ref(null)
// ESC key to close modals
function handleKeydown (event) {
  if (event.key === 'Escape') {
    if (showAddModal.value || showEditModal.value) closeModal()
    if (showDetailsModal.value) showDetailsModal.value = false
  }
}

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(10)
const totalJobs = ref(0)

const jobForm = ref({
  order_id: '',
  product_id: '',
  quantity: 0,
  unit: '',
  priority: '',
  status: '',
  start_date: '',
  expected_end_date: '',
  machine_id: '',
  operator_id: '',
  formula_id: '',
  batch_size: 0,
  quality_check_required: false,
  sample_size: 0,
  tolerance: 0,
  notes: ''
})

// Computed
const filteredJobs = computed(() => {
  let filtered = productionJobs.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(job =>
      job.job_number.toLowerCase().includes(query) ||
      job.product_name.toLowerCase().includes(query) ||
      job.order_number.toLowerCase().includes(query)
    )
  }

  if (statusFilter.value) {
    filtered = filtered.filter(job => job.status === statusFilter.value)
  }

  if (productFilter.value) {
    filtered = filtered.filter(job => job.product_id === parseInt(productFilter.value))
  }

  if (priorityFilter.value) {
    filtered = filtered.filter(job => job.priority === priorityFilter.value)
  }

  return filtered
})

// Mobile carousel computed/state
const currentJobIndex = ref(0)
const currentJob = computed(() => filteredJobs.value[currentJobIndex.value] || null)

// Touch state for swipe
const jobTouchStartX = ref(0)
const jobTouchStartY = ref(0)
const jobIsDragging = ref(false)
// end coords not required; using deltas directly

function nextJob () {
  if (currentJobIndex.value < filteredJobs.value.length - 1) currentJobIndex.value++
}
function previousJob () {
  if (currentJobIndex.value > 0) currentJobIndex.value--
}
function handleJobTouchStart (e) {
  const t = e.touches[0]
  jobTouchStartX.value = t.clientX
  jobTouchStartY.value = t.clientY
  jobIsDragging.value = false
}
function handleJobTouchMove (e) {
  if (!jobTouchStartX.value && !jobTouchStartY.value) return
  const t = e.touches[0]
  const dx = t.clientX - jobTouchStartX.value
  const dy = t.clientY - jobTouchStartY.value
  if (Math.abs(dx) > Math.abs(dy)) {
    jobIsDragging.value = true
    e.preventDefault()
  }
}
function handleJobTouchEnd (e) {
  if (!jobIsDragging.value) return
  const t = e.changedTouches[0]
  const dx = t.clientX - jobTouchStartX.value
  if (Math.abs(dx) > 50) {
    if (dx > 0) {
      previousJob()
    } else {
      nextJob()
    }
  }
  jobTouchStartX.value = 0
  jobTouchStartY.value = 0
  jobIsDragging.value = false
}

// Mouse drag (desktop parity like Products)
function handleJobMouseDown (e) {
  jobTouchStartX.value = e.clientX
  jobTouchStartY.value = e.clientY
  jobIsDragging.value = false
}
function handleJobMouseMove (e) {
  if (!jobTouchStartX.value && !jobTouchStartY.value) return
  const dx = e.clientX - jobTouchStartX.value
  const dy = e.clientY - jobTouchStartY.value
  if (Math.abs(dx) > Math.abs(dy)) jobIsDragging.value = true
}
function handleJobMouseUp (e) {
  if (!jobIsDragging.value) return
  const dx = e.clientX - jobTouchStartX.value
  if (Math.abs(dx) > 50) {
    if (dx > 0) {
      previousJob()
    } else {
      nextJob()
    }
  }
  jobTouchStartX.value = 0
  jobTouchStartY.value = 0
  jobIsDragging.value = false
}

// Reset index on filters
watch([searchQuery, statusFilter, productFilter, priorityFilter], () => { currentJobIndex.value = 0 })

// Minimal modal closer kept earlier was duplicate; consolidated below

const totalPages = computed(() => Math.ceil(totalJobs.value / itemsPerPage.value))

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, currentPage.value - 2)
  const end = Math.min(totalPages.value, currentPage.value + 2)

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Methods
function getStatusColor (status) {
  const colors = {
    pending: 'bg-yellow-100 text-yellow-800',
    scheduled: 'bg-blue-100 text-blue-800',
    in_progress: 'bg-green-100 text-green-800',
    paused: 'bg-orange-100 text-orange-800',
    completed: 'bg-green-100 text-green-800',
    cancelled: 'bg-red-100 text-red-800'
  }
  return colors[status] || 'bg-gray-100 text-gray-800'
}

function getPriorityColor (priority) {
  const colors = {
    low: 'bg-gray-100 text-gray-800',
    medium: 'bg-blue-100 text-blue-800',
    high: 'bg-orange-100 text-orange-800',
    urgent: 'bg-red-100 text-red-800'
  }
  return colors[priority] || 'bg-gray-100 text-gray-800'
}

function getProgressColor (progress) {
  if (progress < 25) return 'bg-red-500'
  if (progress < 50) return 'bg-orange-500'
  if (progress < 75) return 'bg-yellow-500'
  return 'bg-green-500'
}

function formatDate (dateString) {
  return new Date(dateString).toLocaleDateString('tr-TR')
}

function formatDateTime (dateString) {
  return new Date(dateString).toLocaleString('tr-TR')
}

async function loadProductionJobs () {
  loading.value = true
  try {
    // Load production jobs from API
    productionJobs.value = []
  } catch (error) {
    console.error('Error loading production jobs:', error)
  } finally {
    loading.value = false
  }
}

async function loadOrders () {
  try {
    // Load data from API
    // Mock data removed
  } catch (error) {
    console.error('Error loading orders:', error)
  }
}

async function loadProducts () {
  try {
    // Load data from API
    // Mock data removed
  } catch (error) {
    console.error('Error loading products:', error)
  }
}

async function loadMachines () {
  try {
    // Load data from API
    // Mock data removed
  } catch (error) {
    console.error('Error loading machines:', error)
  }
}

async function loadOperators () {
  try {
    // Load data from API
    // Mock data removed
  } catch (error) {
    console.error('Error loading operators:', error)
  }
}

async function loadFormulas () {
  try {
    // Load data from API
    // Mock data removed
  } catch (error) {
    console.error('Error loading formulas:', error)
  }
}

function viewJob (job) {
  selectedJob.value = job
  showDetailsModal.value = true
}

function editJob (job) {
  editingJob.value = job
  jobForm.value = {
    order_id: job.order_id,
    product_id: job.product_id,
    quantity: job.quantity,
    unit: job.unit,
    priority: job.priority,
    status: job.status,
    start_date: job.start_date ? new Date(job.start_date).toISOString().slice(0, 16) : '',
    expected_end_date: job.expected_end_date ? new Date(job.expected_end_date).toISOString().slice(0, 16) : '',
    machine_id: job.machine_id,
    operator_id: job.operator_id,
    formula_id: job.formula_id,
    batch_size: job.batch_size,
    quality_check_required: job.quality_check_required,
    sample_size: job.sample_size,
    tolerance: job.tolerance,
    notes: job.notes
  }
  showEditModal.value = true
}

async function startJob (job) {
  if (confirm(`Start production job ${job.job_number}?`)) {
    try {
      // TODO: Implement start API call
      job.status = 'in_progress'
      job.start_date = new Date().toISOString()
      job.progress = 0
    } catch (error) {
      console.error('Error starting job:', error)
    }
  }
}

async function pauseJob (job) {
  if (confirm(`Pause production job ${job.job_number}?`)) {
    try {
      // TODO: Implement pause API call
      job.status = 'paused'
    } catch (error) {
      console.error('Error pausing job:', error)
    }
  }
}

async function resumeJob (job) {
  if (confirm(`Resume production job ${job.job_number}?`)) {
    try {
      // TODO: Implement resume API call
      job.status = 'in_progress'
    } catch (error) {
      console.error('Error resuming job:', error)
    }
  }
}

async function completeJob (job) {
  if (confirm(`Complete production job ${job.job_number}?`)) {
    try {
      // TODO: Implement complete API call
      job.status = 'completed'
      job.progress = 100
      job.completed_at = new Date().toISOString()
    } catch (error) {
      console.error('Error completing job:', error)
    }
  }
}

async function deleteJob (job) {
  if (confirm(`Are you sure you want to delete production job ${job.job_number}?`)) {
    try {
      // TODO: Implement delete API call
      productionJobs.value = productionJobs.value.filter(j => j.id !== job.id)
      totalJobs.value = productionJobs.value.length
    } catch (error) {
      console.error('Error deleting job:', error)
    }
  }
}

async function saveJob () {
  saving.value = true
  try {
    if (showAddModal.value) {
      // TODO: Implement create API call
      const newJob = {
        id: Date.now(),
        job_number: `PJ-2024-${String(productionJobs.value.length + 1).padStart(3, '0')}`,
        order_id: jobForm.value.order_id,
        order_number: orders.value.find(o => o.id === jobForm.value.order_id)?.order_number || '',
        product_id: jobForm.value.product_id,
        product_name: products.value.find(p => p.id === jobForm.value.product_id)?.name || '',
        quantity: jobForm.value.quantity,
        unit: jobForm.value.unit,
        status: jobForm.value.status,
        priority: jobForm.value.priority,
        progress: 0,
        start_date: jobForm.value.start_date,
        expected_end_date: jobForm.value.expected_end_date,
        completed_at: null,
        operator_id: jobForm.value.operator_id,
        operator_name: operators.value.find(o => o.id === jobForm.value.operator_id)?.name || null,
        machine_id: jobForm.value.machine_id,
        machine_name: machines.value.find(m => m.id === jobForm.value.machine_id)?.name || '',
        formula_id: jobForm.value.formula_id,
        formula_version: formulas.value.find(f => f.id === jobForm.value.formula_id)?.version || '',
        batch_size: jobForm.value.batch_size,
        quality_check_required: jobForm.value.quality_check_required,
        sample_size: jobForm.value.sample_size,
        tolerance: jobForm.value.tolerance,
        quality_status: 'Pending',
        notes: jobForm.value.notes,
        created_at: new Date().toISOString()
      }
      productionJobs.value.unshift(newJob)
      totalJobs.value = productionJobs.value.length
    } else {
      // TODO: Implement update API call
      const index = productionJobs.value.findIndex(j => j.id === editingJob.value.id)
      if (index !== -1) {
        productionJobs.value[index] = {
          ...productionJobs.value[index],
          order_id: jobForm.value.order_id,
          order_number: orders.value.find(o => o.id === jobForm.value.order_id)?.order_number || '',
          product_id: jobForm.value.product_id,
          product_name: products.value.find(p => p.id === jobForm.value.product_id)?.name || '',
          quantity: jobForm.value.quantity,
          unit: jobForm.value.unit,
          priority: jobForm.value.priority,
          status: jobForm.value.status,
          start_date: jobForm.value.start_date,
          expected_end_date: jobForm.value.expected_end_date,
          operator_id: jobForm.value.operator_id,
          operator_name: operators.value.find(o => o.id === jobForm.value.operator_id)?.name || null,
          machine_id: jobForm.value.machine_id,
          machine_name: machines.value.find(m => m.id === jobForm.value.machine_id)?.name || '',
          formula_id: jobForm.value.formula_id,
          formula_version: formulas.value.find(f => f.id === jobForm.value.formula_id)?.version || '',
          batch_size: jobForm.value.batch_size,
          quality_check_required: jobForm.value.quality_check_required,
          sample_size: jobForm.value.sample_size,
          tolerance: jobForm.value.tolerance,
          notes: jobForm.value.notes
        }
      }
    }
    closeModal()
  } catch (error) {
    console.error('Error saving job:', error)
  } finally {
    saving.value = false
  }
}

function closeModal () {
  showAddModal.value = false
  showEditModal.value = false
  showDetailsModal.value = false
  editingJob.value = null
  selectedJob.value = null
  jobForm.value = {
    order_id: '',
    product_id: '',
    quantity: 0,
    unit: '',
    priority: '',
    status: '',
    start_date: '',
    expected_end_date: '',
    machine_id: '',
    operator_id: '',
    formula_id: '',
    batch_size: 0,
    quality_check_required: false,
    sample_size: 0,
    tolerance: 0,
    notes: ''
  }
}

// Pagination methods
function goToPage (page) {
  currentPage.value = page
}

function previousPage () {
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

function nextPage () {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

// Watch for product changes to update unit
watch(() => jobForm.value.product_id, (newProductId) => {
  const product = products.value.find(p => p.id === newProductId)
  if (product) {
    jobForm.value.unit = product.unit
  }
})

// Lifecycle
onMounted(() => {
  loadProductionJobs()
  loadOrders()
  loadProducts()
  loadMachines()
  loadOperators()
  loadFormulas()
  document.addEventListener('keydown', handleKeydown)
})
</script>
