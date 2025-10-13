import { useAuthStore } from '@/store/auth'

export async function authGuard (to, from, next) {
  const auth = useAuthStore()

  // If we don't have tokens in state, try to initialize from localStorage
  if (!auth.tokens) {
    await auth.initializeAuth()
  }

  if (!auth.isAuthenticated) {
    return next({ name: 'login', query: { redirect: to.fullPath } })
  }
  next()
}

export function roleGuard (roles) {
  return (to, from, next) => {
    const auth = useAuthStore()
    if (!auth.isAuthenticated) return next({ name: 'login' })
    if (!roles.includes(auth.user?.role ?? '')) return next({ name: 'orders' })
    next()
  }
}
