import { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '@/contexts/AuthContext'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRole?: 'admin' | 'user'
}

export function ProtectedRoute({ children, requiredRole }: ProtectedRouteProps) {
  const { isAuthenticated, loading, isSuperAdmin, isBrandAdmin } = useAuth()
  const location = useLocation()

  // Show loading state while checking auth
  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingSpinner className="h-8 w-8" />
      </div>
    )
  }

  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  // Redirect super admins away from chat
  if (location.pathname === '/chat' && isSuperAdmin()) {
    return <Navigate to="/brands" replace />
  }

  // Check role requirements
  if (requiredRole === 'admin') {
    // Allow access if user is super_admin or brand_admin
    const hasAdminAccess = isSuperAdmin() || isBrandAdmin()
    if (!hasAdminAccess) {
      // Super admins go to brands, others to chat
      const redirectTo = isSuperAdmin() ? '/brands' : '/chat'
      return <Navigate to={redirectTo} replace />
    }
  }

  return <>{children}</>
}

