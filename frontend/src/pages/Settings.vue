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
          <!-- Settings Accordion -->
          <div class="space-y-4">
            <!-- Mobile Accordion -->
            <div class="block lg:hidden space-y-4">
              <div v-for="tab in settingsTabs" :key="tab.id" class="bg-white border rounded-lg shadow-sm">
                <button
                  @click="toggleAccordion(tab.id)"
                  class="w-full px-4 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <div class="flex items-center space-x-3">
                    <span class="text-2xl">{{ getTabIcon(tab.id) }}</span>
                    <div>
                      <h3 class="font-medium text-gray-900">{{ tab.name }}</h3>
                      <p class="text-sm text-gray-500">{{ $t(`settings.tab_descriptions.${tab.id}`) }}</p>
                    </div>
                  </div>
                  <div class="flex items-center space-x-2">
                    <span v-if="tab.id === 'users'" class="text-sm text-gray-500">{{ users.length }} {{ $t('settings.users_count') }}</span>
                    <svg
                      :class="['w-5 h-5 text-gray-400 transition-transform', expandedAccordions.includes(tab.id) ? 'rotate-180' : '']"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
                    </svg>
                  </div>
                </button>

                <!-- Accordion Content -->
                <div v-if="expandedAccordions.includes(tab.id)" class="border-t border-gray-200">
                  <div class="p-4">
                    <!-- User Management Content -->
                    <div v-if="tab.id === 'users'" class="space-y-4">
                      <div class="flex justify-between items-center">
                        <h4 class="font-medium text-gray-900">{{ $t('settings.user_management') }}</h4>
                        <button
                          @click="showAddUserModal = true"
                          class="bg-primary-600 hover:bg-primary-700 text-white px-3 py-2 rounded-md text-sm font-medium"
                        >
                          {{ $t('settings.add_user') }}
                        </button>
                      </div>

                      <!-- User List -->
                      <div class="space-y-2">
                        <div v-for="user in users" :key="user.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div class="flex items-center space-x-3">
                            <div class="w-10 h-10 bg-gray-300 rounded-full flex items-center justify-center">
                              <span class="text-sm font-medium text-gray-700">{{ user.name.charAt(0) }}</span>
                            </div>
                            <div>
                              <div class="font-medium text-gray-900">{{ user.name }}</div>
                              <div class="text-sm text-gray-500">{{ user.email }}</div>
                            </div>
                          </div>
                          <div class="flex items-center space-x-2">
                            <span
                              :class="user.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                              class="px-2 py-1 text-xs font-semibold rounded-full"
                            >
                              {{ user.isActive ? $t('common.active') : $t('common.inactive') }}
                            </span>
                            <button
                              @click="editUser(user)"
                              class="text-primary-600 hover:text-primary-900 text-sm"
                            >
                              {{ $t('common.edit') }}
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Role Management Content -->
                    <div v-if="tab.id === 'roles'" class="space-y-4">
                      <div class="flex justify-between items-center">
                        <h4 class="font-medium text-gray-900">{{ $t('settings.role_management') }}</h4>
                        <button
                          @click="showAddRoleModal = true"
                          class="bg-primary-600 hover:bg-primary-700 text-white px-3 py-2 rounded-md text-sm font-medium"
                        >
                          {{ $t('settings.add_role') }}
                        </button>
                      </div>

                      <div class="space-y-3">
                        <div v-for="role in roles" :key="role.id" class="p-3 bg-gray-50 rounded-lg">
                          <div class="flex justify-between items-start mb-2">
                            <h5 class="font-medium text-gray-900">{{ role.name }}</h5>
                            <span class="text-xs text-gray-500">{{ role.userCount }} {{ $t('settings.users_count') }}</span>
                          </div>
                          <p class="text-sm text-gray-600 mb-2">{{ role.description }}</p>
                          <div class="flex gap-2">
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

                    <!-- Language Settings Content -->
                    <div v-if="tab.id === 'language'" class="space-y-4">
                      <h4 class="font-medium text-gray-900">{{ $t('settings.language_settings') }}</h4>
                      <div class="space-y-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700 mb-2">
                            {{ $t('settings.default_application_language') }}
                          </label>
                          <select
                            v-model="defaultLanguage"
                            @change="updateDefaultLanguage"
                            class="w-full border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                          >
                            <option value="en">🇺🇸 English</option>
                            <option value="tr">🇹🇷 Türkçe</option>
                          </select>
                        </div>
                        <div class="grid grid-cols-2 gap-4">
                          <div class="bg-white p-3 rounded border">
                            <div class="text-sm font-medium text-gray-700">{{ $t('settings.your_language') }}</div>
                            <div class="text-sm text-gray-500">{{ currentUserLanguage }}</div>
                          </div>
                          <div class="bg-white p-3 rounded border">
                            <div class="text-sm font-medium text-gray-700">{{ $t('settings.system_default') }}</div>
                            <div class="text-sm text-gray-500">{{ defaultLanguage }}</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- System Settings Content -->
                    <div v-if="tab.id === 'system'" class="space-y-4">
                      <h4 class="font-medium text-gray-900">{{ $t('settings.system_configuration') }}</h4>
                      <div class="space-y-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700">{{ $t('settings.company_name') }}</label>
                          <input
                            v-model="systemSettings.companyName"
                            type="text"
                            class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
                          />
                        </div>
                        <div>
                          <label class="block text-sm font-medium text-gray-700">{{ $t('settings.default_currency') }}</label>
                          <select v-model="systemSettings.currency" class="w-full mt-1 border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500">
                            <option value="TRY">Turkish Lira (₺)</option>
                            <option value="USD">US Dollar ($)</option>
                            <option value="EUR">Euro (€)</option>
                          </select>
                        </div>
                        <button
                          @click="saveSystemSettings"
                          class="w-full bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-md text-sm font-medium"
                        >
                          {{ $t('settings.save_settings') }}
                        </button>
                      </div>
                    </div>

                    <!-- Backup & Maintenance Content -->
                    <div v-if="tab.id === 'backup'" class="space-y-4">
                      <h4 class="font-medium text-gray-900">{{ $t('settings.backup_maintenance') }}</h4>
                      <div class="space-y-4">
                        <div class="p-3 bg-gray-50 rounded-lg">
                          <h5 class="font-medium text-gray-900 mb-2">{{ $t('settings.backup_settings') }}</h5>
                          <div class="space-y-2">
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
                        <div class="space-y-2">
                          <button
                            @click="cleanupDatabase"
                            class="w-full bg-yellow-600 hover:bg-yellow-700 text-white px-3 py-2 rounded-md text-sm font-medium"
                          >
                            {{ $t('settings.clean_database') }}
                          </button>
                          <button
                            @click="clearCache"
                            class="w-full bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-md text-sm font-medium"
                          >
                            {{ $t('settings.clear_cache') }}
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Desktop Tabs -->
            <div class="hidden lg:block bg-white shadow rounded-lg mb-8">
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
                <!-- Desktop content will be the same as mobile accordion content -->
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
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('common.user') }}</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('common.role') }}</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('common.department') }}</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('common.status') }}</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('common.last_login') }}</th>
                          <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">{{ $t('common.actions') }}</th>
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
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ user.role }}</td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ user.department }}</td>
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

                <!-- Other tabs content can be added here -->
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
                      </div>
                      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="bg-white p-3 rounded border">
                          <div class="text-sm font-medium text-gray-700">{{ $t('settings.your_language') }}</div>
                          <div class="text-sm text-gray-500">{{ currentUserLanguage }}</div>
                        </div>
                        <div class="bg-white p-3 rounded border">
                          <div class="text-sm font-medium text-gray-700">{{ $t('settings.system_default') }}</div>
                          <div class="text-sm text-gray-500">{{ defaultLanguage }}</div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- System Settings -->
                <div v-if="activeTab === 'system'" class="space-y-6">
                  <h3 class="text-lg font-medium text-gray-900">{{ $t('settings.system_configuration') }}</h3>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
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
                      </div>
                    </div>
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
    <div v-if="showAddUserModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-2xl shadow-lg rounded-md bg-white" @click.stop>
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
    <div v-if="showEditUserModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
      <div class="relative top-10 mx-auto p-5 border w-4/5 max-w-2xl shadow-lg rounded-md bg-white" @click.stop>
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
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale, t } = useI18n()

// Data
const activeTab = ref('users')
const showAddUserModal = ref(false)
const showEditUserModal = ref(false)
const showAddRoleModal = ref(false)
const editingUser = ref(null)

// Accordion state
const expandedAccordions = ref([]) // Start with users expanded

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

// Accordion functions
function toggleAccordion (tabId) {
  const index = expandedAccordions.value.indexOf(tabId)
  if (index > -1) {
    expandedAccordions.value.splice(index, 1)
  } else {
    expandedAccordions.value.push(tabId)
  }
}

function getTabIcon (tabId) {
  const icons = {
    users: '👥',
    roles: '🔐',
    language: '🌐',
    system: '⚙️',
    backup: '💾'
  }
  return icons[tabId] || '📋'
}

// ESC key handler
function handleKeydown (event) {
  if (event.key === 'Escape') {
    closeModal()
  }
}

// Modal close function
function closeModal () {
  showAddUserModal.value = false
  showEditUserModal.value = false
  showAddRoleModal.value = false
  editingUser.value = null
}

// Users Data
const users = ref([])

// Roles Data
const roles = ref([])

// System Settings
const systemSettings = ref({
  companyName: 'Demo Kimya',
  currency: 'TRY',
  timezone: 'Europe/Istanbul',
  language: 'tr',
  defaultBatchSize: 100,
  qualityCheckRequired: true,
  wasteThreshold: 5.0
})

// Notification Settings (commented out as not used in current accordion design)
// const notificationSettings = ref({
//   emailOrders: true,
//   emailProduction: true,
//   emailInventory: true,
//   smsEnabled: false
// })

// Security Settings (commented out as not used in current accordion design)
// const securitySettings = ref({
//   sessionTimeout: 60,
//   passwordMinLength: 8,
//   passwordRequireSpecial: true,
//   twoFactorEnabled: false
// })

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
}

function deleteRole (role) {
  if (confirm(t('settings.delete_role_confirm', { roleName: role.name }))) {
    // TODO: Implement delete role functionality
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
}

function saveSystemSettings () {
  // TODO: Implement save system settings functionality
}

function updateDefaultLanguage () {
  localStorage.setItem('app-default-language', defaultLanguage.value)
  // Emit event to notify other components about the default language change
  window.dispatchEvent(new CustomEvent('default-language-changed', {
    detail: { language: defaultLanguage.value }
  }))
}

function cleanupDatabase () {
  if (confirm(t('settings.cleanup_database_confirm'))) {
    // TODO: Implement database cleanup
  }
}

function clearCache () {
  if (confirm(t('settings.clear_cache_confirm'))) {
    // TODO: Implement cache clearing
  }
}

// function checkSystemHealth () {
//   // TODO: Implement system health check
// }

// Lifecycle
onMounted(() => {
  // Load settings data
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>
