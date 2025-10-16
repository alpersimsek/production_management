<template>
  <div>
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center">
          <h1 class="text-3xl font-bold text-gray-900">{{ $t('packaging.title') }}</h1>
          <button
            @click="showAddModal = true"
            class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
          >
            {{ $t('packaging.new_packaging') }}
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
                  :placeholder="$t('packaging.search_placeholder')"
                  class="input-field"
                />
              </div>
              <div class="flex gap-2">
                <select v-model="statusFilter" class="input-field">
                  <option value="">{{ $t('packaging.all_status') }}</option>
                  <option value="pending">{{ $t('packaging.status.pending') }}</option>
                  <option value="scheduled">{{ $t('packaging.status.scheduled') }}</option>
                  <option value="in_progress">{{ $t('packaging.status.in_progress') }}</option>
                  <option value="paused">{{ $t('packaging.status.paused') }}</option>
                  <option value="completed">{{ $t('packaging.status.completed') }}</option>
                  <option value="cancelled">{{ $t('packaging.status.cancelled') }}</option>
                </select>
                <select v-model="productFilter" class="input-field">
                  <option value="">{{ $t('packaging.all_products') }}</option>
                  <option v-for="product in products" :key="product.id" :value="product.id">
                    {{ product.name }}
                  </option>
                </select>
                <select v-model="priorityFilter" class="input-field">
                  <option value="">{{ $t('packaging.all_priorities') }}</option>
                  <option value="low">{{ $t('packaging.priority.low') }}</option>
                  <option value="medium">{{ $t('packaging.priority.medium') }}</option>
                  <option value="high">{{ $t('packaging.priority.high') }}</option>
                  <option value="urgent">{{ $t('packaging.priority.urgent') }}</option>
                </select>
                <button
                  @click="loadPackagingJobs"
                  class="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                >
                  {{ $t('common.refresh') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Packaging Jobs Table -->
          <div class="bg-white shadow overflow-hidden sm:rounded-md">
            <div v-if="loading" class="p-6 text-center">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
              <p class="mt-2 text-gray-600">{{ $t('packaging.loading') }}</p>
            </div>

            <div v-else-if="packagingJobs.length === 0" class="p-6 text-center text-gray-500">
              {{ $t('packaging.no_jobs_found') }}
            </div>

            <div v-else class="overflow-x-auto">
              <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                  <tr>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('packaging.job_number') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('packaging.product') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('packaging.lot') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('packaging.quantity_label') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('packaging.package_type_label') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('common.status') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('packaging.priority_label') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('packaging.progress') }}
                    </th>
                    <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      {{ $t('packaging.operator') }}
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
                      {{ job.lot_number }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ job.quantity }} {{ job.unit }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {{ $t(`packaging.package_types.${job.package_type}`) }}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="getStatusColor(job.status)"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      >
                        {{ $t(`packaging.status.${job.status}`) }}
                      </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                      <span
                        :class="getPriorityColor(job.priority)"
                        class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      >
                        {{ $t(`packaging.priority.${job.priority}`) }}
                      </span>
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
                        {{ $t('packaging.edit') }}
                      </button>
                      <button
                        v-if="job.status === 'pending' || job.status === 'scheduled'"
                        @click="startJob(job)"
                        class="text-green-600 hover:text-green-900 mr-3"
                      >
                        {{ $t('packaging.start') }}
                      </button>
                      <button
                        v-if="job.status === 'in_progress'"
                        @click="pauseJob(job)"
                        class="text-yellow-600 hover:text-yellow-900 mr-3"
                      >
                        {{ $t('packaging.pause') }}
                      </button>
                      <button
                        v-if="job.status === 'paused'"
                        @click="resumeJob(job)"
                        class="text-green-600 hover:text-green-900 mr-3"
                      >
                        {{ $t('packaging.resume') }}
                      </button>
                      <button
                        v-if="job.status === 'in_progress' || job.status === 'paused'"
                        @click="completeJob(job)"
                        class="text-green-600 hover:text-green-900 mr-3"
                      >
                        {{ $t('packaging.complete') }}
                      </button>
                      <button
                        @click="generateLabels(job)"
                        class="text-purple-600 hover:text-purple-900 mr-3"
                      >
                        {{ $t('packaging.labels') }}
                      </button>
                      <button
                        @click="deleteJob(job)"
                        class="text-red-600 hover:text-red-900"
                      >
                        {{ $t('packaging.delete') }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
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
                Previous
              </button>
              <button
                @click="nextPage"
                :disabled="currentPage === totalPages"
                class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50"
              >
                Next
              </button>
            </div>
            <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p class="text-sm text-gray-700">
                  Showing
                  <span class="font-medium">{{ (currentPage - 1) * itemsPerPage + 1 }}</span>
                  to
                  <span class="font-medium">{{ Math.min(currentPage * itemsPerPage, totalJobs) }}</span>
                  of
                  <span class="font-medium">{{ totalJobs }}</span>
                  results
                </p>
              </div>
              <div>
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    @click="previousPage"
                    :disabled="currentPage === 1"
                    class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                  >
                    Previous
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
                    Next
                  </button>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Add/Edit Packaging Job Modal -->
    <div v-if="showAddModal || showEditModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ showAddModal ? $t('packaging.add_packaging') : $t('packaging.edit_packaging') }}
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
                <label class="block text-sm font-medium text-gray-700">{{ $t('production.job_number') }} *</label>
                <select v-model="jobForm.production_job_id" required class="input-field mt-1">
                  <option value="">{{ $t('production.select_order') }}</option>
                  <option v-for="prodJob in productionJobs" :key="prodJob.id" :value="prodJob.id">
                    {{ prodJob.job_number }} - {{ prodJob.product_name }}
                  </option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.lot') }} *</label>
                <input
                  v-model="jobForm.lot_number"
                  type="text"
                  required
                  class="input-field mt-1"
                  placeholder="LOT-2024-001"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.product') }} *</label>
                <input
                  v-model="jobForm.product_name"
                  type="text"
                  readonly
                  class="input-field mt-1 bg-gray-50"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.quantity_label') }} *</label>
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
                <label class="block text-sm font-medium text-gray-700">{{ $t('common.unit') }}</label>
                <input
                  v-model="jobForm.unit"
                  type="text"
                  readonly
                  class="input-field mt-1 bg-gray-50"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.package_type_label') }} *</label>
                <select v-model="jobForm.package_type" required class="input-field mt-1">
                  <option value="">{{ $t('packaging.select_package_type') }}</option>
                  <option value="bag">{{ $t('packaging.package_types.bag') }}</option>
                  <option value="box">{{ $t('packaging.package_types.box') }}</option>
                  <option value="bottle">{{ $t('packaging.package_types.bottle') }}</option>
                  <option value="can">{{ $t('packaging.package_types.can') }}</option>
                  <option value="tube">{{ $t('packaging.package_types.tube') }}</option>
                  <option value="sachet">{{ $t('packaging.package_types.sachet') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.package_size_label') }}</label>
                <input
                  v-model="jobForm.package_size"
                  type="text"
                  class="input-field mt-1"
                  placeholder="500ml, 1kg, etc."
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.priority_label') }} *</label>
                <select v-model="jobForm.priority" required class="input-field mt-1">
                  <option value="">{{ $t('packaging.select_priority') }}</option>
                  <option value="low">{{ $t('packaging.priority.low') }}</option>
                  <option value="medium">{{ $t('packaging.priority.medium') }}</option>
                  <option value="high">{{ $t('packaging.priority.high') }}</option>
                  <option value="urgent">{{ $t('packaging.priority.urgent') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('common.status') }} *</label>
                <select v-model="jobForm.status" required class="input-field mt-1">
                  <option value="">{{ $t('packaging.select_status') }}</option>
                  <option value="pending">{{ $t('packaging.status.pending') }}</option>
                  <option value="scheduled">{{ $t('packaging.status.scheduled') }}</option>
                  <option value="in_progress">{{ $t('packaging.status.in_progress') }}</option>
                  <option value="paused">{{ $t('packaging.status.paused') }}</option>
                  <option value="completed">{{ $t('packaging.status.completed') }}</option>
                  <option value="cancelled">{{ $t('packaging.status.cancelled') }}</option>
                </select>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.start_date') }}</label>
                <input
                  v-model="jobForm.start_date"
                  type="datetime-local"
                  class="input-field mt-1"
                />
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.expected_end_date') }}</label>
                <input
                  v-model="jobForm.expected_end_date"
                  type="datetime-local"
                  class="input-field mt-1"
                />
              </div>
            </div>

            <!-- Packaging Details -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">Packaging Details</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700">Packaging Line</label>
                  <select v-model="jobForm.packaging_line_id" class="input-field mt-1">
                    <option value="">Select packaging line</option>
                    <option v-for="line in packagingLines" :key="line.id" :value="line.id">
                      {{ line.name }} - {{ line.type }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Operator</label>
                  <select v-model="jobForm.operator_id" class="input-field mt-1">
                    <option value="">Select operator</option>
                    <option v-for="operator in operators" :key="operator.id" :value="operator.id">
                      {{ operator.name }}
                    </option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">Batch Size</label>
                  <input
                    v-model.number="jobForm.batch_size"
                    type="number"
                    min="1"
                    step="1"
                    class="input-field mt-1"
                    placeholder="0"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.packages_per_batch') }}</label>
                  <input
                    v-model.number="jobForm.packages_per_batch"
                    type="number"
                    min="1"
                    step="1"
                    class="input-field mt-1"
                    placeholder="0"
                  />
                </div>
              </div>
            </div>

            <!-- Quality Control -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('packaging.quality_control') }}</h4>
              <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.quality_check_required') }}</label>
                  <div class="mt-2">
                    <label class="flex items-center">
                      <input
                        v-model="jobForm.quality_check_required"
                        type="checkbox"
                        class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                      />
                      <span class="ml-2 text-sm text-gray-700">{{ $t('packaging.required') }}</span>
                    </label>
                  </div>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.sample_size') }}</label>
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
                  <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.tolerance') }} (%)</label>
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

            <!-- Labeling -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('packaging.labeling_tracking') }}</h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.label_type') }}</label>
                  <select v-model="jobForm.label_type" class="input-field mt-1">
                    <option value="">{{ $t('packaging.select_label_type') }}</option>
                    <option value="qr_code">{{ $t('packaging.qr_code') }}</option>
                    <option value="barcode">{{ $t('packaging.barcode') }}</option>
                    <option value="both">{{ $t('packaging.both_qr_barcode') }}</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.batch_number') }}</label>
                  <input
                    v-model="jobForm.batch_number"
                    type="text"
                    class="input-field mt-1"
                    placeholder="BATCH-2024-001"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.expiry_date') }}</label>
                  <input
                    v-model="jobForm.expiry_date"
                    type="date"
                    class="input-field mt-1"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">{{ $t('packaging.packaging_date') }}</label>
                  <input
                    v-model="jobForm.production_date"
                    type="date"
                    class="input-field mt-1"
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
                :placeholder="$t('packaging.notes_placeholder')"
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
                {{ saving ? $t('packaging.saving') : $t('packaging.save_packaging') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Job Details Modal -->
    <div v-if="showDetailsModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-4xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">
              {{ $t('packaging.packaging_details') }} - {{ selectedJob?.job_number }}
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
                <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('packaging.job_information') }}</h4>
                <dl class="space-y-2">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('packaging.job_number') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.job_number }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('packaging.product') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.product_name }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('packaging.lot') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.lot_number }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('packaging.quantity_label') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.quantity }} {{ selectedJob.unit }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('packaging.package_type_label') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ $t(`packaging.package_types.${selectedJob.package_type}`) }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('packaging.package_size_label') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.package_size || '-' }}</dd>
                  </div>
                </dl>
              </div>

              <div>
                <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('packaging.status_progress') }}</h4>
                <dl class="space-y-2">
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('common.status') }}:</dt>
                    <dd class="text-sm">
                      <span :class="getStatusColor(selectedJob.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                        {{ $t(`packaging.status.${selectedJob.status}`) }}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('packaging.priority_label') }}:</dt>
                    <dd class="text-sm">
                      <span :class="getPriorityColor(selectedJob.priority)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                        {{ $t(`packaging.priority.${selectedJob.priority}`) }}
                      </span>
                    </dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('packaging.progress') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.progress }}%</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('packaging.operator') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.operator_name || '-' }}</dd>
                  </div>
                  <div>
                    <dt class="text-sm font-medium text-gray-500">{{ $t('packaging.packaging_line') }}:</dt>
                    <dd class="text-sm text-gray-900">{{ selectedJob.packaging_line_name || '-' }}</dd>
                  </div>
                </dl>
              </div>
            </div>

            <!-- Progress Bar -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-2">{{ $t('packaging.packaging_progress_title') }}</h4>
              <div class="w-full bg-gray-200 rounded-full h-4">
                <div
                  :class="getProgressColor(selectedJob.progress)"
                  class="h-4 rounded-full transition-all duration-300"
                  :style="{ width: selectedJob.progress + '%' }"
                ></div>
              </div>
              <p class="text-sm text-gray-600 mt-2">{{ selectedJob.progress }}% {{ $t('packaging.completed_text') }}</p>
            </div>

            <!-- Packaging Timeline -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('packaging.packaging_timeline_title') }}</h4>
              <div class="space-y-4">
                <div class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-green-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('packaging.job_created') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedJob.created_at) }}</p>
                  </div>
                </div>
                <div v-if="selectedJob.start_date" class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-blue-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('packaging.packaging_started') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedJob.start_date) }}</p>
                  </div>
                </div>
                <div v-if="selectedJob.expected_end_date" class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-gray-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('packaging.expected_completion') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedJob.expected_end_date) }}</p>
                  </div>
                </div>
                <div v-if="selectedJob.completed_at" class="flex items-center space-x-3">
                  <div class="w-3 h-3 bg-green-400 rounded-full"></div>
                  <div>
                    <p class="text-sm font-medium text-gray-900">{{ $t('packaging.packaging_completed') }}</p>
                    <p class="text-xs text-gray-500">{{ formatDateTime(selectedJob.completed_at) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Quality Control -->
            <div v-if="selectedJob.quality_check_required">
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('packaging.quality_control') }}</h4>
              <div class="bg-gray-50 p-4 rounded-lg">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('packaging.sample_size') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedJob.sample_size || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('packaging.tolerance') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedJob.tolerance ? selectedJob.tolerance + '%' : '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('packaging.quality_status') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedJob.quality_status || $t('packaging.pending_status') }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Labeling Information -->
            <div>
              <h4 class="text-md font-medium text-gray-900 mb-4">{{ $t('packaging.labeling_information') }}</h4>
              <div class="bg-gray-50 p-4 rounded-lg">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('packaging.label_type') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedJob.label_type || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('packaging.batch_number') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedJob.batch_number || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('packaging.production_date') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedJob.production_date ? formatDate(selectedJob.production_date) : '-' }}</p>
                  </div>
                  <div>
                    <p class="text-sm font-medium text-gray-500">{{ $t('packaging.expiry_date') }}</p>
                    <p class="text-sm text-gray-900">{{ selectedJob.expiry_date ? formatDate(selectedJob.expiry_date) : '-' }}</p>
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
const packagingJobs = ref([])
const productionJobs = ref([])
const products = ref([])
const packagingLines = ref([])
const operators = ref([])
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

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(10)
const totalJobs = ref(0)

const jobForm = ref({
  production_job_id: '',
  lot_number: '',
  product_name: '',
  quantity: 0,
  unit: '',
  package_type: '',
  package_size: '',
  priority: '',
  status: '',
  start_date: '',
  expected_end_date: '',
  packaging_line_id: '',
  operator_id: '',
  batch_size: 0,
  packages_per_batch: 0,
  quality_check_required: false,
  sample_size: 0,
  tolerance: 0,
  label_type: '',
  batch_number: '',
  expiry_date: '',
  production_date: '',
  notes: ''
})

// Computed
const filteredJobs = computed(() => {
  let filtered = packagingJobs.value

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(job =>
      job.job_number.toLowerCase().includes(query) ||
      job.product_name.toLowerCase().includes(query) ||
      job.lot_number.toLowerCase().includes(query)
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

async function loadPackagingJobs () {
  loading.value = true
  try {
    // Mock data for now
    packagingJobs.value = [
      {
        id: 1,
        job_number: 'PKG-2024-001',
        production_job_id: 1,
        product_id: 1,
        product_name: 'Market Poşeti 30x40',
        lot_number: 'LOT-2024-001',
        quantity: 1000,
        unit: 'kg',
        package_type: 'bag',
        package_size: '1kg',
        status: 'in_progress',
        priority: 'high',
        progress: 75,
        start_date: '2024-01-15T08:00:00Z',
        expected_end_date: '2024-01-20T17:00:00Z',
        completed_at: null,
        operator_id: 1,
        operator_name: 'Ahmet Yılmaz',
        packaging_line_id: 1,
        packaging_line_name: 'Packaging Line 1',
        batch_size: 100,
        packages_per_batch: 10,
        quality_check_required: true,
        sample_size: 10,
        tolerance: 2.5,
        quality_status: 'Passed',
        label_type: 'qr_code',
        batch_number: 'BATCH-2024-001',
        production_date: '2024-01-15',
        expiry_date: '2025-01-15',
        notes: 'High priority packaging for new product launch',
        created_at: '2024-01-15T07:30:00Z'
      },
      {
        id: 2,
        job_number: 'PKG-2024-002',
        production_job_id: 2,
        product_id: 2,
        product_name: 'Bulaşık Deterjanı',
        lot_number: 'LOT-2024-002',
        quantity: 500,
        unit: 'kg',
        package_type: 'bottle',
        package_size: '500ml',
        status: 'scheduled',
        priority: 'medium',
        progress: 0,
        start_date: null,
        expected_end_date: '2024-01-25T17:00:00Z',
        completed_at: null,
        operator_id: null,
        operator_name: null,
        packaging_line_id: 2,
        packaging_line_name: 'Packaging Line 2',
        batch_size: 50,
        packages_per_batch: 5,
        quality_check_required: true,
        sample_size: 5,
        tolerance: 1.0,
        quality_status: 'Pending',
        label_type: 'barcode',
        batch_number: 'BATCH-2024-002',
        production_date: '2024-01-20',
        expiry_date: '2026-01-20',
        notes: 'Regular packaging batch',
        created_at: '2024-01-20T09:15:00Z'
      },
      {
        id: 3,
        job_number: 'PKG-2024-003',
        production_job_id: 3,
        product_id: 3,
        product_name: 'Temizlik Malzemesi',
        lot_number: 'LOT-2024-003',
        quantity: 200,
        unit: 'kg',
        package_type: 'tube',
        package_size: '250ml',
        status: 'completed',
        priority: 'low',
        progress: 100,
        start_date: '2024-01-10T08:00:00Z',
        expected_end_date: '2024-01-12T17:00:00Z',
        completed_at: '2024-01-12T16:30:00Z',
        operator_id: 2,
        operator_name: 'Mehmet Kaya',
        packaging_line_id: 3,
        packaging_line_name: 'Packaging Line 3',
        batch_size: 25,
        packages_per_batch: 2,
        quality_check_required: false,
        sample_size: 0,
        tolerance: 0,
        quality_status: 'N/A',
        label_type: 'both',
        batch_number: 'BATCH-2024-003',
        production_date: '2024-01-10',
        expiry_date: '2025-01-10',
        notes: 'Completed successfully',
        created_at: '2024-01-10T07:45:00Z'
      },
      {
        id: 4,
        job_number: 'PKG-2024-004',
        production_job_id: 1,
        product_id: 4,
        product_name: 'Market Poşeti 20x30',
        lot_number: 'LOT-2024-004',
        quantity: 600,
        unit: 'kg',
        package_type: 'bag',
        package_size: '500g',
        status: 'paused',
        priority: 'medium',
        progress: 40,
        start_date: '2024-01-18T08:00:00Z',
        expected_end_date: '2024-01-22T17:00:00Z',
        completed_at: null,
        operator_id: 1,
        operator_name: 'Ahmet Yılmaz',
        packaging_line_id: 1,
        packaging_line_name: 'Packaging Line 1',
        batch_size: 75,
        packages_per_batch: 8,
        quality_check_required: true,
        sample_size: 8,
        tolerance: 2.0,
        quality_status: 'In Progress',
        label_type: 'qr_code',
        batch_number: 'BATCH-2024-004',
        production_date: '2024-01-18',
        expiry_date: '2025-01-18',
        notes: 'Paused due to label shortage',
        created_at: '2024-01-18T07:30:00Z'
      }
    ]
    totalJobs.value = packagingJobs.value.length
  } catch (error) {
    console.error('Error loading packaging jobs:', error)
  } finally {
    loading.value = false
  }
}

async function loadProductionJobs () {
  try {
    // Mock data for now
    productionJobs.value = [
      { id: 1, job_number: 'PJ-2024-001', product_name: 'Market Poşeti 30x40', unit: 'kg' },
      { id: 2, job_number: 'PJ-2024-002', product_name: 'Bulaşık Deterjanı', unit: 'kg' },
      { id: 3, job_number: 'PJ-2024-003', product_name: 'Temizlik Malzemesi', unit: 'kg' },
      { id: 4, job_number: 'PJ-2024-004', product_name: 'Market Poşeti 20x30', unit: 'kg' }
    ]
  } catch (error) {
    console.error('Error loading production jobs:', error)
  }
}

async function loadProducts () {
  try {
    // Mock data for now
    products.value = [
      { id: 1, name: 'Market Poşeti 30x40', code: 'POS001', unit: 'kg' },
      { id: 2, name: 'Bulaşık Deterjanı', code: 'DET001', unit: 'kg' },
      { id: 3, name: 'Temizlik Malzemesi', code: 'ALS001', unit: 'kg' },
      { id: 4, name: 'Market Poşeti 20x30', code: 'POS002', unit: 'kg' }
    ]
  } catch (error) {
    console.error('Error loading products:', error)
  }
}

async function loadPackagingLines () {
  try {
    // Mock data for now
    packagingLines.value = [
      { id: 1, name: 'Packaging Line 1', type: 'Automatic' },
      { id: 2, name: 'Packaging Line 2', type: 'Semi-Automatic' },
      { id: 3, name: 'Packaging Line 3', type: 'Manual' }
    ]
  } catch (error) {
    console.error('Error loading packaging lines:', error)
  }
}

async function loadOperators () {
  try {
    // Mock data for now
    operators.value = [
      { id: 1, name: 'Ahmet Yılmaz' },
      { id: 2, name: 'Mehmet Kaya' },
      { id: 3, name: 'Ali Demir' }
    ]
  } catch (error) {
    console.error('Error loading operators:', error)
  }
}

function viewJob (job) {
  selectedJob.value = job
  showDetailsModal.value = true
}

function editJob (job) {
  editingJob.value = job
  jobForm.value = {
    production_job_id: job.production_job_id,
    lot_number: job.lot_number,
    product_name: job.product_name,
    quantity: job.quantity,
    unit: job.unit,
    package_type: job.package_type,
    package_size: job.package_size,
    priority: job.priority,
    status: job.status,
    start_date: job.start_date ? new Date(job.start_date).toISOString().slice(0, 16) : '',
    expected_end_date: job.expected_end_date ? new Date(job.expected_end_date).toISOString().slice(0, 16) : '',
    packaging_line_id: job.packaging_line_id,
    operator_id: job.operator_id,
    batch_size: job.batch_size,
    packages_per_batch: job.packages_per_batch,
    quality_check_required: job.quality_check_required,
    sample_size: job.sample_size,
    tolerance: job.tolerance,
    label_type: job.label_type,
    batch_number: job.batch_number,
    expiry_date: job.expiry_date,
    production_date: job.production_date,
    notes: job.notes
  }
  showEditModal.value = true
}

async function startJob (job) {
  if (confirm(`Start packaging job ${job.job_number}?`)) {
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
  if (confirm(`Pause packaging job ${job.job_number}?`)) {
    try {
      // TODO: Implement pause API call
      job.status = 'paused'
    } catch (error) {
      console.error('Error pausing job:', error)
    }
  }
}

async function resumeJob (job) {
  if (confirm(`Resume packaging job ${job.job_number}?`)) {
    try {
      // TODO: Implement resume API call
      job.status = 'in_progress'
    } catch (error) {
      console.error('Error resuming job:', error)
    }
  }
}

async function completeJob (job) {
  if (confirm(`Complete packaging job ${job.job_number}?`)) {
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

async function generateLabels (job) {
  if (confirm(`Generate labels for packaging job ${job.job_number}?`)) {
    try {
      // TODO: Implement label generation API call
      alert(`Labels generated for ${job.job_number}\nQR Code: ${job.lot_number}\nBatch: ${job.batch_number}`)
    } catch (error) {
      console.error('Error generating labels:', error)
    }
  }
}

async function deleteJob (job) {
  if (confirm(`Are you sure you want to delete packaging job ${job.job_number}?`)) {
    try {
      // TODO: Implement delete API call
      packagingJobs.value = packagingJobs.value.filter(j => j.id !== job.id)
      totalJobs.value = packagingJobs.value.length
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
        job_number: `PKG-2024-${String(packagingJobs.value.length + 1).padStart(3, '0')}`,
        production_job_id: jobForm.value.production_job_id,
        product_id: productionJobs.value.find(p => p.id === jobForm.value.production_job_id)?.id || 1,
        product_name: productionJobs.value.find(p => p.id === jobForm.value.production_job_id)?.product_name || '',
        lot_number: jobForm.value.lot_number,
        quantity: jobForm.value.quantity,
        unit: productionJobs.value.find(p => p.id === jobForm.value.production_job_id)?.unit || 'kg',
        package_type: jobForm.value.package_type,
        package_size: jobForm.value.package_size,
        status: jobForm.value.status,
        priority: jobForm.value.priority,
        progress: 0,
        start_date: jobForm.value.start_date,
        expected_end_date: jobForm.value.expected_end_date,
        completed_at: null,
        operator_id: jobForm.value.operator_id,
        operator_name: operators.value.find(o => o.id === jobForm.value.operator_id)?.name || null,
        packaging_line_id: jobForm.value.packaging_line_id,
        packaging_line_name: packagingLines.value.find(l => l.id === jobForm.value.packaging_line_id)?.name || '',
        batch_size: jobForm.value.batch_size,
        packages_per_batch: jobForm.value.packages_per_batch,
        quality_check_required: jobForm.value.quality_check_required,
        sample_size: jobForm.value.sample_size,
        tolerance: jobForm.value.tolerance,
        quality_status: 'Pending',
        label_type: jobForm.value.label_type,
        batch_number: jobForm.value.batch_number,
        expiry_date: jobForm.value.expiry_date,
        production_date: jobForm.value.production_date,
        notes: jobForm.value.notes,
        created_at: new Date().toISOString()
      }
      packagingJobs.value.unshift(newJob)
      totalJobs.value = packagingJobs.value.length
    } else {
      // TODO: Implement update API call
      const index = packagingJobs.value.findIndex(j => j.id === editingJob.value.id)
      if (index !== -1) {
        packagingJobs.value[index] = {
          ...packagingJobs.value[index],
          production_job_id: jobForm.value.production_job_id,
          product_name: productionJobs.value.find(p => p.id === jobForm.value.production_job_id)?.product_name || '',
          lot_number: jobForm.value.lot_number,
          quantity: jobForm.value.quantity,
          unit: productionJobs.value.find(p => p.id === jobForm.value.production_job_id)?.unit || 'kg',
          package_type: jobForm.value.package_type,
          package_size: jobForm.value.package_size,
          priority: jobForm.value.priority,
          status: jobForm.value.status,
          start_date: jobForm.value.start_date,
          expected_end_date: jobForm.value.expected_end_date,
          operator_id: jobForm.value.operator_id,
          operator_name: operators.value.find(o => o.id === jobForm.value.operator_id)?.name || null,
          packaging_line_id: jobForm.value.packaging_line_id,
          packaging_line_name: packagingLines.value.find(l => l.id === jobForm.value.packaging_line_id)?.name || '',
          batch_size: jobForm.value.batch_size,
          packages_per_batch: jobForm.value.packages_per_batch,
          quality_check_required: jobForm.value.quality_check_required,
          sample_size: jobForm.value.sample_size,
          tolerance: jobForm.value.tolerance,
          label_type: jobForm.value.label_type,
          batch_number: jobForm.value.batch_number,
          expiry_date: jobForm.value.expiry_date,
          production_date: jobForm.value.production_date,
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
    production_job_id: '',
    lot_number: '',
    product_name: '',
    quantity: 0,
    unit: '',
    package_type: '',
    package_size: '',
    priority: '',
    status: '',
    start_date: '',
    expected_end_date: '',
    packaging_line_id: '',
    operator_id: '',
    batch_size: 0,
    packages_per_batch: 0,
    quality_check_required: false,
    sample_size: 0,
    tolerance: 0,
    label_type: '',
    batch_number: '',
    expiry_date: '',
    production_date: '',
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

// Watch for production job changes to update product info
watch(() => jobForm.value.production_job_id, (newProductionJobId) => {
  const productionJob = productionJobs.value.find(p => p.id === newProductionJobId)
  if (productionJob) {
    jobForm.value.product_name = productionJob.product_name
    jobForm.value.unit = productionJob.unit
  }
})

// Lifecycle
onMounted(() => {
  loadPackagingJobs()
  loadProductionJobs()
  loadProducts()
  loadPackagingLines()
  loadOperators()
})
</script>
