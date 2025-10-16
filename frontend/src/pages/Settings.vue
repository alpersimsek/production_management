<template>
  <div>
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <h1 class="text-3xl font-bold text-gray-900">{{ $t('settings.system_settings') }}</h1>
      </div>
    </header>

    <main>
      <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div class="px-4 py-6 sm:px-0">
          <!-- Settings Navigation -->
          <div class="bg-white shadow rounded-lg mb-8">
            <div class="border-b border-gray-200">
              <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                <button
                  v-for="tab in settingsTabs"
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
              <!-- User Management -->
              <div v-if="activeTab === 'users'" class="space-y-6">
                <div class="flex justify-between items-center">
                  <h3 class="text-lg font-medium text-gray-900">{{ $t('settings.user_management') }}</h3>
                  <button
                    @click="showAddUserModal = true"
                    class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    {{ $t('settings.add_user') }}
                  </button>
                </div>

                <div class="bg-white shadow overflow-hidden sm:rounded-md">
                  <table class="min-w-full divide-y divide-gray-200">
                    <thead class="bg-gray-50">
                      <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {{ $t('common.user') }}
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {{ $t('common.role') }}
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {{ $t('common.department') }}
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {{ $t('common.status') }}
                        </th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {{ $t('common.last_login') }}
                        </th>
                        <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                          {{ $t('common.actions') }}
                        </th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200">
                      <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50">
                        <td class="px-6 py-4 whitespace-nowrap">
                          <div class="flex items-center">
                            <div class="flex-shrink-0 h-10 w-10">
                              <div class="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                                <span class="text-sm font-medium text-gray-700">{{ user.name.charAt(0) }}</span>
                              </div>
                            </div>
                            <div class="ml-4">
                              <div class="text-sm font-medium text-gray-900">{{ user.name }}</div>
                              <div class="text-sm text-gray-500">{{ user.email }}</div>
                            </div>
                          </div>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                          {{ user.role }}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {{ user.department }}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap">
                          <span
                            :class="user.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                            class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                          >
                            {{ user.isActive ? $t('common.active') : $t('common.inactive') }}
                          </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {{ user.lastLogin ? formatDate(user.lastLogin) : $t('common.never') }}
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                          <button
                            @click="editUser(user)"
                            class="text-primary-600 hover:text-primary-900 mr-3"
                          >
                            {{ $t('common.edit') }}
                          </button>
                          <button
                            @click="toggleUserStatus(user)"
                            :class="user.isActive ? 'text-red-600 hover:text-red-900' : 'text-green-600 hover:text-green-900'"
                          >
                            {{ user.isActive ? $t('common.deactivate') : $t('common.activate') }}
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Role Management -->
              <div v-if="activeTab === 'roles'" class="space-y-6">
                <div class="flex justify-between items-center">
                  <h3 class="text-lg font-medium text-gray-900">{{ $t('settings.role_management') }}</h3>
                  <button
                    @click="showAddRoleModal = true"
                    class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    {{ $t('settings.add_role') }}
                  </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div v-for="role in roles" :key="role.id" class="bg-gray-50 p-4 rounded-lg">
                    <div class="flex justify-between items-start mb-2">
                      <h4 class="text-sm font-medium text-gray-900">{{ role.name }}</h4>
                      <span class="text-xs text-gray-500">{{ role.userCount }} {{ $t('settings.users_count') }}</span>
                    </div>
                    <p class="text-sm text-gray-600 mb-3">{{ role.description }}</p>
                    <div class="space-y-1">
                      <div v-for="permission in role.permissions" :key="permission" class="text-xs text-gray-500">
                        • {{ permission }}
                      </div>
                    </div>
                    <div class="mt-3 flex gap-2">
                      <button
                        @click="editRole(role)"
                        class="text-primary-600 hover:text-primary-900 text-xs"
                      >
                        {{ $t('common.edit') }}
                      </button>
                      <button
                        @click="deleteRole(role)"
                        class="text-red-600 hover:text-red-900 text-xs"
                      >
                        {{ $t('common.delete') }}
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Language Settings -->
              <div v-if="activeTab === 'language'" class="space-y-6">
                <h3 class="text-lg font-medium text-gray-900">{{ $t('settings.language_settings') }}</h3>

                <div class="bg-gray-50 p-6 rounded-lg">
                  <div class="space-y-4">
                    <div>
                      <label class="block text-sm font-medium text-gray-700 mb-2">
                        {{ $t('settings.default_application_language') }}
                      </label>
                      <select
                        v-model="defaultLanguage"
                        @change="updateDefaultLanguage"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                      >
                        <option value="en">🇺🇸 English</option>
                        <option value="tr">🇹🇷 Türkçe</option>
                      </select>
                      <p class="mt-2 text-sm text-gray-500">
                        {{ $t('settings.language_description') }}
                      </p>
                    </div>

                    <div class="border-t pt-4">
                      <h4 class="text-sm font-medium text-gray-900 mb-3">{{ $t('settings.current_language_status') }}</h4>
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-white p-3 rounded border">
                          <div class="flex items-center justify-between">
                            <span class="text-sm font-medium text-gray-700">{{ $t('settings.your_language') }}</span>
                            <span class="text-sm text-gray-500">{{ currentUserLanguage }}</span>
                          </div>
                        </div>
                        <div class="bg-white p-3 rounded border">
                          <div class="flex items-center justify-between">
                            <span class="text-sm font-medium text-gray-700">{{ $t('settings.system_default') }}</span>
                            <span class="text-sm text-gray-500">{{ defaultLanguage }}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- System Settings -->
              <div v-if="activeTab === 'system'" class="space-y-6">
                <h3 class="text-lg font-medium text-gray-900">{{ $t('settings.system_configuration') }}</h3>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- General Settings -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-4">{{ $t('settings.general_settings') }}</h4>
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.company_name') }}</label>
                        <input
                          v-model="systemSettings.companyName"
                          type="text"
                          class="input-field mt-1"
                        />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.default_currency') }}</label>
                        <select v-model="systemSettings.currency" class="input-field mt-1">
                          <option value="TRY">Turkish Lira (₺)</option>
                          <option value="USD">US Dollar ($)</option>
                          <option value="EUR">Euro (€)</option>
                        </select>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.time_zone') }}</label>
                        <select v-model="systemSettings.timezone" class="input-field mt-1">
                          <option value="Europe/Istanbul">Europe/Istanbul</option>
                          <option value="UTC">UTC</option>
                        </select>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.language') }}</label>
                        <select v-model="systemSettings.language" class="input-field mt-1">
                          <option value="tr">Türkçe</option>
                          <option value="en">English</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <!-- Production Settings -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-4">{{ $t('settings.production_settings') }}</h4>
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.default_batch_size') }}</label>
                        <input
                          v-model.number="systemSettings.defaultBatchSize"
                          type="number"
                          class="input-field mt-1"
                        />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.quality_check_required') }}</label>
                        <div class="mt-2">
                          <label class="flex items-center">
                            <input
                              v-model="systemSettings.qualityCheckRequired"
                              type="checkbox"
                              class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                            />
                            <span class="ml-2 text-sm text-gray-700">{{ $t('settings.enable_by_default') }}</span>
                          </label>
                        </div>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.waste_threshold') }}</label>
                        <input
                          v-model.number="systemSettings.wasteThreshold"
                          type="number"
                          step="0.1"
                          min="0"
                          max="100"
                          class="input-field mt-1"
                        />
                      </div>
                    </div>
                  </div>

                  <!-- Notification Settings -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-4">{{ $t('settings.notification_settings') }}</h4>
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.email_notifications') }}</label>
                        <div class="mt-2 space-y-2">
                          <label class="flex items-center">
                            <input
                              v-model="notificationSettings.emailOrders"
                              type="checkbox"
                              class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                            />
                            <span class="ml-2 text-sm text-gray-700">{{ $t('settings.order_updates') }}</span>
                          </label>
                          <label class="flex items-center">
                            <input
                              v-model="notificationSettings.emailProduction"
                              type="checkbox"
                              class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                            />
                            <span class="ml-2 text-sm text-gray-700">{{ $t('settings.production_alerts') }}</span>
                          </label>
                          <label class="flex items-center">
                            <input
                              v-model="notificationSettings.emailInventory"
                              type="checkbox"
                              class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                            />
                            <span class="ml-2 text-sm text-gray-700">{{ $t('settings.low_stock_alerts') }}</span>
                          </label>
                        </div>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.sms_notifications') }}</label>
                        <div class="mt-2">
                          <label class="flex items-center">
                            <input
                              v-model="notificationSettings.smsEnabled"
                              type="checkbox"
                              class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                            />
                            <span class="ml-2 text-sm text-gray-700">{{ $t('settings.enable_sms_alerts') }}</span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>

                  <!-- Security Settings -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-4">{{ $t('settings.security_settings') }}</h4>
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.session_timeout') }}</label>
                        <input
                          v-model.number="securitySettings.sessionTimeout"
                          type="number"
                          min="5"
                          max="480"
                          class="input-field mt-1"
                        />
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.password_policy') }}</label>
                        <div class="mt-2 space-y-2">
                          <label class="flex items-center">
                            <input
                              v-model="securitySettings.passwordMinLength"
                              type="number"
                              min="6"
                              max="20"
                              class="input-field w-20"
                            />
                            <span class="ml-2 text-sm text-gray-700">{{ $t('settings.minimum_length') }}</span>
                          </label>
                          <label class="flex items-center">
                            <input
                              v-model="securitySettings.passwordRequireSpecial"
                              type="checkbox"
                              class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                            />
                            <span class="ml-2 text-sm text-gray-700">{{ $t('settings.require_special_characters') }}</span>
                          </label>
                        </div>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.two_factor_authentication') }}</label>
                        <div class="mt-2">
                          <label class="flex items-center">
                            <input
                              v-model="securitySettings.twoFactorEnabled"
                              type="checkbox"
                              class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                            />
                            <span class="ml-2 text-sm text-gray-700">{{ $t('settings.enable_2fa') }}</span>
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="flex justify-end">
                  <button
                    @click="saveSystemSettings"
                    class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                  >
                    {{ $t('settings.save_settings') }}
                  </button>
                </div>
              </div>

              <!-- Backup & Maintenance -->
              <div v-if="activeTab === 'backup'" class="space-y-6">
                <h3 class="text-lg font-medium text-gray-900">{{ $t('settings.backup_maintenance') }}</h3>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- Backup Settings -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-4">{{ $t('settings.backup_settings') }}</h4>
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.auto_backup') }}</label>
                        <div class="mt-2">
                          <label class="flex items-center">
                            <input
                              v-model="backupSettings.autoBackup"
                              type="checkbox"
                              class="rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50"
                            />
                            <span class="ml-2 text-sm text-gray-700">{{ $t('settings.enable_automatic_backups') }}</span>
                          </label>
                        </div>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.backup_frequency') }}</label>
                        <select v-model="backupSettings.frequency" class="input-field mt-1">
                          <option value="daily">{{ $t('settings.daily') }}</option>
                          <option value="weekly">{{ $t('settings.weekly') }}</option>
                          <option value="monthly">{{ $t('settings.monthly') }}</option>
                        </select>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.retention_period') }}</label>
                        <select v-model="backupSettings.retention" class="input-field mt-1">
                          <option value="7">{{ $t('settings.days_7') }}</option>
                          <option value="30">{{ $t('settings.days_30') }}</option>
                          <option value="90">{{ $t('settings.days_90') }}</option>
                          <option value="365">{{ $t('settings.year_1') }}</option>
                        </select>
                      </div>
                    </div>
                  </div>

                  <!-- Maintenance -->
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h4 class="text-sm font-medium text-gray-900 mb-4">{{ $t('settings.system_maintenance') }}</h4>
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.database_cleanup') }}</label>
                        <p class="text-sm text-gray-600 mb-2">{{ $t('settings.cleanup_description') }}</p>
                        <button
                          @click="cleanupDatabase"
                          class="bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-2 rounded-md text-sm font-medium"
                        >
                          {{ $t('settings.clean_database') }}
                        </button>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.cache_management') }}</label>
                        <p class="text-sm text-gray-600 mb-2">{{ $t('settings.cache_description') }}</p>
                        <button
                          @click="clearCache"
                          class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm font-medium"
                        >
                          {{ $t('settings.clear_cache') }}
                        </button>
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">{{ $t('settings.system_health') }}</label>
                        <p class="text-sm text-gray-600 mb-2">{{ $t('settings.health_description') }}</p>
                        <button
                          @click="checkSystemHealth"
                          class="bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-md text-sm font-medium"
                        >
                          {{ $t('settings.health_check') }}
                        </button>
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

    <!-- Add User Modal -->
    <div v-if="showAddUserModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-2xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">{{ $t('settings.add_new_user') }}</h3>
            <button
              @click="showAddUserModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <form @submit.prevent="saveUser" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('settings.full_name') }} *</label>
                <input
                  v-model="userForm.name"
                  type="text"
                  required
                  class="input-field mt-1"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('settings.email') }} *</label>
                <input
                  v-model="userForm.email"
                  type="email"
                  required
                  class="input-field mt-1"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('common.role') }} *</label>
                <select v-model="userForm.role" required class="input-field mt-1">
                  <option value="">{{ $t('settings.select_role') }}</option>
                  <option v-for="role in roles" :key="role.id" :value="role.name">
                    {{ role.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('common.department') }}</label>
                <select v-model="userForm.department" class="input-field mt-1">
                  <option value="">{{ $t('settings.select_department') }}</option>
                  <option value="Üretim">{{ $t('settings.departments.production') }}</option>
                  <option value="Paketleme">{{ $t('settings.departments.packaging') }}</option>
                  <option value="Depo">{{ $t('settings.departments.warehouse') }}</option>
                  <option value="Sevkiyat">{{ $t('settings.departments.shipment') }}</option>
                  <option value="Plasiyer">{{ $t('settings.departments.sales') }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('settings.phone') }}</label>
                <input
                  v-model="userForm.phone"
                  type="tel"
                  class="input-field mt-1"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('settings.password') }} *</label>
                <input
                  v-model="userForm.password"
                  type="password"
                  required
                  class="input-field mt-1"
                />
              </div>
            </div>

            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="showAddUserModal = false"
                class="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md text-sm font-medium"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                type="submit"
                class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                {{ $t('settings.save_user') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Edit User Modal -->
    <div v-if="showEditUserModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-2xl shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-medium text-gray-900">{{ $t('common.edit') }} {{ $t('common.user') }}</h3>
            <button
              @click="showEditUserModal = false"
              class="text-gray-400 hover:text-gray-600"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>

          <form @submit.prevent="updateUser" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('settings.full_name') }} *</label>
                <input
                  v-model="editingUser.name"
                  type="text"
                  required
                  class="input-field mt-1"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('settings.email') }} *</label>
                <input
                  v-model="editingUser.email"
                  type="email"
                  required
                  class="input-field mt-1"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('common.role') }} *</label>
                <select v-model="editingUser.role" required class="input-field mt-1">
                  <option value="">{{ $t('settings.select_role') }}</option>
                  <option v-for="role in roles" :key="role.id" :value="role.name">
                    {{ role.name }}
                  </option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('common.department') }}</label>
                <select v-model="editingUser.department" class="input-field mt-1">
                  <option value="">{{ $t('settings.select_department') }}</option>
                  <option value="Üretim">{{ $t('settings.departments.production') }}</option>
                  <option value="Paketleme">{{ $t('settings.departments.packaging') }}</option>
                  <option value="Depo">{{ $t('settings.departments.warehouse') }}</option>
                  <option value="Sevkiyat">{{ $t('settings.departments.shipment') }}</option>
                  <option value="Plasiyer">{{ $t('settings.departments.sales') }}</option>
                </select>
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('settings.phone') }}</label>
                <input
                  v-model="editingUser.phone"
                  type="tel"
                  class="input-field mt-1"
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700">{{ $t('common.status') }}</label>
                <select v-model="editingUser.isActive" class="input-field mt-1">
                  <option :value="true">{{ $t('common.active') }}</option>
                  <option :value="false">{{ $t('common.inactive') }}</option>
                </select>
              </div>
            </div>

            <div class="flex justify-end space-x-3 pt-4">
              <button
                type="button"
                @click="showEditUserModal = false"
                class="bg-gray-300 hover:bg-gray-400 text-gray-800 px-4 py-2 rounded-md text-sm font-medium"
              >
                {{ $t('common.cancel') }}
              </button>
              <button
                type="submit"
                class="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
              >
                {{ $t('common.update') }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale, t } = useI18n()

// Data
const activeTab = ref('users')
const showAddUserModal = ref(false)
const showEditUserModal = ref(false)
const showAddRoleModal = ref(false)
const editingUser = ref(null)

// Language Settings
const defaultLanguage = ref(localStorage.getItem('app-default-language') || 'en')
const currentUserLanguage = computed(() => locale.value)

// Settings Tabs
const settingsTabs = ref([
  { id: 'users', name: t('settings.users') },
  { id: 'roles', name: t('settings.roles_label') },
  { id: 'language', name: t('settings.language') },
  { id: 'system', name: t('settings.system') },
  { id: 'backup', name: t('settings.backup') }
])

// Users Data
const users = ref([
  {
    id: 1,
    name: 'Ahmet Yılmaz',
    email: 'ahmet@olgahan.com',
    role: t('settings.roles.admin'),
    department: 'Üretim',
    isActive: true,
    lastLogin: '2024-01-20T10:30:00Z'
  },
  {
    id: 2,
    name: 'Mehmet Kaya',
    email: 'mehmet@olgahan.com',
    role: t('settings.roles.operator'),
    department: 'Paketleme',
    isActive: true,
    lastLogin: '2024-01-20T09:15:00Z'
  },
  {
    id: 3,
    name: 'Ayşe Demir',
    email: 'ayse@olgahan.com',
    role: t('settings.roles.manager'),
    department: 'Depo',
    isActive: false,
    lastLogin: '2024-01-15T14:20:00Z'
  },
  {
    id: 4,
    name: 'Fatma Özkan',
    email: 'fatma@olgahan.com',
    role: t('settings.roles.manager'),
    department: 'Üretim',
    isActive: true,
    lastLogin: '2024-01-20T08:45:00Z'
  },
  {
    id: 5,
    name: 'Ali Çelik',
    email: 'ali@olgahan.com',
    role: t('settings.roles.operator'),
    department: 'Üretim',
    isActive: true,
    lastLogin: '2024-01-20T11:20:00Z'
  },
  {
    id: 6,
    name: 'Zeynep Arslan',
    email: 'zeynep@olgahan.com',
    role: t('settings.roles.operator'),
    department: 'Depo',
    isActive: true,
    lastLogin: '2024-01-20T07:30:00Z'
  },
  {
    id: 7,
    name: 'Mustafa Yıldız',
    email: 'mustafa@olgahan.com',
    role: t('settings.roles.operator'),
    department: 'Sevkiyat',
    isActive: true,
    lastLogin: '2024-01-19T16:45:00Z'
  },
  {
    id: 8,
    name: 'Elif Korkmaz',
    email: 'elif@olgahan.com',
    role: t('settings.roles.manager'),
    department: 'Paketleme',
    isActive: true,
    lastLogin: '2024-01-20T09:00:00Z'
  },
  {
    id: 9,
    name: 'Hasan Güneş',
    email: 'hasan@olgahan.com',
    role: t('settings.roles.operator'),
    department: 'Plasiyer',
    isActive: false,
    lastLogin: '2024-01-18T13:15:00Z'
  },
  {
    id: 10,
    name: 'Selin Aktaş',
    email: 'selin@olgahan.com',
    role: t('settings.roles.manager'),
    department: 'Sevkiyat',
    isActive: true,
    lastLogin: '2024-01-20T12:10:00Z'
  },
  {
    id: 11,
    name: 'Burak Şahin',
    email: 'burak@olgahan.com',
    role: t('settings.roles.operator'),
    department: 'Üretim',
    isActive: true,
    lastLogin: '2024-01-20T10:45:00Z'
  },
  {
    id: 12,
    name: 'Gülay Yılmaz',
    email: 'gulay@olgahan.com',
    role: t('settings.roles.manager'),
    department: 'Plasiyer',
    isActive: true,
    lastLogin: '2024-01-19T15:30:00Z'
  }
])

// Roles Data
const roles = ref([
  {
    id: 1,
    name: t('settings.roles.admin'),
    description: t('settings.role_descriptions.admin'),
    userCount: 1,
    permissions: [t('settings.permissions.all_permissions'), t('settings.permissions.user_management'), t('settings.permissions.system_settings')]
  },
  {
    id: 2,
    name: t('settings.roles.manager'),
    description: t('settings.role_descriptions.manager'),
    userCount: 5,
    permissions: [t('settings.permissions.view_reports'), t('settings.permissions.manage_orders'), t('settings.permissions.view_analytics')]
  },
  {
    id: 3,
    name: t('settings.roles.operator'),
    description: t('settings.role_descriptions.operator'),
    userCount: 6,
    permissions: [t('settings.permissions.production_jobs'), t('settings.permissions.quality_control'), t('settings.permissions.inventory_updates')]
  }
])

// System Settings
const systemSettings = ref({
  companyName: 'Olgahan Kimya',
  currency: 'TRY',
  timezone: 'Europe/Istanbul',
  language: 'tr',
  defaultBatchSize: 100,
  qualityCheckRequired: true,
  wasteThreshold: 5.0
})

// Notification Settings
const notificationSettings = ref({
  emailOrders: true,
  emailProduction: true,
  emailInventory: true,
  smsEnabled: false
})

// Security Settings
const securitySettings = ref({
  sessionTimeout: 60,
  passwordMinLength: 8,
  passwordRequireSpecial: true,
  twoFactorEnabled: false
})

// Backup Settings
const backupSettings = ref({
  autoBackup: true,
  frequency: 'daily',
  retention: '30'
})

// User Form
const userForm = ref({
  name: '',
  email: '',
  role: '',
  department: '',
  phone: '',
  password: ''
})

// Methods
function formatDate (dateString) {
  return new Date(dateString).toLocaleDateString('tr-TR')
}

function editUser (user) {
  editingUser.value = { ...user }
  showEditUserModal.value = true
}

function toggleUserStatus (user) {
  user.isActive = !user.isActive
  // TODO: Implement API call to update user status
}

function editRole (role) {
  // TODO: Implement edit role functionality
  console.log('Edit role:', role)
}

function deleteRole (role) {
  if (confirm(t('settings.delete_role_confirm', { roleName: role.name }))) {
    // TODO: Implement delete role functionality
    console.log('Delete role:', role)
  }
}

function updateUser () {
  // Find the user in the users array and update it
  const userIndex = users.value.findIndex(user => user.id === editingUser.value.id)
  if (userIndex !== -1) {
    users.value[userIndex] = { ...editingUser.value }
  }
  showEditUserModal.value = false
  editingUser.value = null
  console.log('User updated:', editingUser.value)
}

function saveSystemSettings () {
  // TODO: Implement save system settings functionality
  console.log('Save system settings')
}

function updateDefaultLanguage () {
  localStorage.setItem('app-default-language', defaultLanguage.value)
  // Emit event to notify other components about the default language change
  window.dispatchEvent(new CustomEvent('default-language-changed', {
    detail: { language: defaultLanguage.value }
  }))
  console.log('Default language updated to:', defaultLanguage.value)
}

function cleanupDatabase () {
  if (confirm(t('settings.cleanup_database_confirm'))) {
    // TODO: Implement database cleanup
    console.log('Database cleanup initiated')
  }
}

function clearCache () {
  if (confirm(t('settings.clear_cache_confirm'))) {
    // TODO: Implement cache clearing
    console.log('Cache cleared')
  }
}

function checkSystemHealth () {
  // TODO: Implement system health check
  console.log('System health check initiated')
}

// Lifecycle
onMounted(() => {
  // Load settings data
})
</script>
