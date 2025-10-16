import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'

/**
 * Role-based access control composable
 * Provides utilities for checking user permissions and roles
 */
export function useRBAC () {
  const authStore = useAuthStore()

  // User role
  const userRole = computed(() => authStore.user?.role || 'guest')

  // Role hierarchy (higher number = more permissions)
  const roleHierarchy = {
    admin: 3,
    manager: 2,
    operator: 1,
    guest: 0
  }

  // Permission definitions
  const permissions = {
    // User Management
    'users:create': ['admin'],
    'users:read': ['admin', 'manager'],
    'users:update': ['admin'],
    'users:delete': ['admin'],

    // Order Management
    'orders:create': ['admin', 'manager'],
    'orders:read': ['admin', 'manager', 'operator'],
    'orders:update': ['admin', 'manager'],
    'orders:delete': ['admin'],
    'orders:approve': ['admin', 'manager'],

    // Customer Management
    'customers:create': ['admin', 'manager'],
    'customers:read': ['admin', 'manager', 'operator'],
    'customers:update': ['admin', 'manager'],
    'customers:delete': ['admin'],

    // Product Management
    'products:create': ['admin'],
    'products:read': ['admin', 'manager', 'operator'],
    'products:update': ['admin'],
    'products:delete': ['admin'],

    // Production Management
    'production:create': ['admin', 'manager', 'operator'],
    'production:read': ['admin', 'manager', 'operator'],
    'production:update': ['admin', 'manager', 'operator'],
    'production:delete': ['admin'],
    'production:assign': ['admin', 'manager'],
    'production:start': ['admin', 'manager', 'operator'],
    'production:finish': ['admin', 'manager', 'operator'],

    // Lot Management
    'lots:create': ['admin', 'manager', 'operator'],
    'lots:read': ['admin', 'manager', 'operator'],
    'lots:update': ['admin', 'manager', 'operator'],
    'lots:delete': ['admin'],
    'lots:waste': ['admin', 'manager', 'operator'],
    'lots:log': ['admin', 'manager', 'operator'],

    // Packaging Management
    'packaging:create': ['admin', 'manager', 'operator'],
    'packaging:read': ['admin', 'manager', 'operator'],
    'packaging:update': ['admin', 'manager', 'operator'],
    'packaging:delete': ['admin'],

    // Warehouse Management
    'warehouse:create': ['admin', 'manager'],
    'warehouse:read': ['admin', 'manager', 'operator'],
    'warehouse:update': ['admin', 'manager', 'operator'],
    'warehouse:delete': ['admin'],
    'warehouse:receipt': ['admin', 'manager', 'operator'],
    'warehouse:approve': ['admin', 'manager'],

    // Shipment Management
    'shipments:create': ['admin', 'manager'],
    'shipments:read': ['admin', 'manager', 'operator'],
    'shipments:update': ['admin', 'manager'],
    'shipments:delete': ['admin'],
    'shipments:plan': ['admin', 'manager'],
    'shipments:deliver': ['admin', 'manager', 'operator'],

    // Analytics
    'analytics:fire': ['admin', 'manager'],
    'analytics:performance': ['admin', 'manager'],
    'analytics:termin': ['admin', 'manager'],
    'analytics:sales': ['admin', 'manager'],
    'analytics:waste': ['admin', 'manager'],
    'analytics:quality': ['admin', 'manager'],
    'analytics:production': ['admin', 'manager'],

    // Settings
    'settings:read': ['admin', 'manager'],
    'settings:update': ['admin'],
    'settings:fire_thresholds': ['admin'],
    'settings:termin_minimum': ['admin'],

    // File Management
    'files:upload': ['admin', 'manager', 'operator'],
    'files:download': ['admin', 'manager', 'operator'],
    'files:delete': ['admin']
  }

  /**
   * Check if user has a specific permission
   */
  function hasPermission (permission) {
    if (!authStore.isAuthenticated) return false
    const allowedRoles = permissions[permission] || []
    return allowedRoles.includes(userRole.value)
  }

  /**
   * Check if user has any of the specified permissions
   */
  function hasAnyPermission (permissionList) {
    return permissionList.some(permission => hasPermission(permission))
  }

  /**
   * Check if user has all of the specified permissions
   */
  function hasAllPermissions (permissionList) {
    return permissionList.every(permission => hasPermission(permission))
  }

  /**
   * Check if user has a specific role
   */
  function hasRole (role) {
    return userRole.value === role
  }

  /**
   * Check if user has any of the specified roles
   */
  function hasAnyRole (roles) {
    return roles.includes(userRole.value)
  }

  /**
   * Check if user has a role with higher or equal hierarchy level
   */
  function hasRoleLevel (requiredRole) {
    const userLevel = roleHierarchy[userRole.value] || 0
    const requiredLevel = roleHierarchy[requiredRole] || 0
    return userLevel >= requiredLevel
  }

  /**
   * Get user's role level
   */
  function getRoleLevel () {
    return roleHierarchy[userRole.value] || 0
  }

  /**
   * Check if user can access a specific module
   */
  function canAccessModule (module) {
    const modulePermissions = {
      dashboard: ['admin', 'manager', 'operator'],
      orders: ['admin', 'manager', 'operator'],
      customers: ['admin', 'manager', 'operator'],
      products: ['admin', 'manager', 'operator'],
      production: ['admin', 'manager', 'operator'],
      packaging: ['admin', 'manager', 'operator'],
      warehouse: ['admin', 'manager', 'operator'],
      shipments: ['admin', 'manager', 'operator'],
      analytics: ['admin', 'manager'],
      settings: ['admin', 'manager']
    }

    const allowedRoles = modulePermissions[module] || []
    return allowedRoles.includes(userRole.value)
  }

  /**
   * Get available modules for current user
   */
  function getAvailableModules () {
    const allModules = ['dashboard', 'orders', 'customers', 'products', 'production', 'packaging', 'warehouse', 'shipments', 'analytics', 'settings']
    return allModules.filter(module => canAccessModule(module))
  }

  return {
    userRole,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    hasRole,
    hasAnyRole,
    hasRoleLevel,
    getRoleLevel,
    canAccessModule,
    getAvailableModules,
    permissions,
    roleHierarchy
  }
}
