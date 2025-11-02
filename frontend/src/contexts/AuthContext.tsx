import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '@/lib/api'
import { User, LoginResponse } from '@/types'

interface AuthContextType {
  user: User | null
  isAuthenticated: boolean
  loading: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  checkAuth: () => Promise<void>
  isAdmin: () => boolean
  isSuperAdmin: () => boolean
  isBrandAdmin: () => boolean
  isBrandUser: () => boolean
  canManageBrand: (brandId: number) => boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

const TOKEN_KEY = 'auth_token'

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  const isAuthenticated = !!user

  const isAdmin = () => {
    return user?.role === 'admin'
  }

  const isSuperAdmin = () => {
    return user?.brand_role === 'super_admin'
  }

  const isBrandAdmin = () => {
    return user?.brand_role === 'brand_admin'
  }

  const isBrandUser = () => {
    return user?.brand_role === 'brand_user'
  }

  const canManageBrand = (brandId: number) => {
    if (!user) return false
    if (isSuperAdmin()) return true
    if (isBrandAdmin() && user.brand_id === brandId) return true
    return false
  }

  const checkAuth = async () => {
    const token = localStorage.getItem(TOKEN_KEY)
    if (!token) {
      setLoading(false)
      return
    }

    try {
      const response = await api.get('/auth/me')
      const userData = response.data
      
      // If user has brand_id and is not super_admin, fetch brand name
      if (userData.brand_id && userData.brand_role !== 'super_admin') {
        try {
          const brandResponse = await api.get(`/brands/${userData.brand_id}`)
          userData.brand_name = brandResponse.data.name
        } catch (error) {
          // If brand fetch fails, continue without brand_name
          console.warn('Failed to fetch brand name:', error)
        }
      }
      
      setUser(userData)
    } catch (error) {
      // Token invalid or expired
      localStorage.removeItem(TOKEN_KEY)
      setUser(null)
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      const response = await api.post<LoginResponse>('/auth/login', {
        email,
        password,
      })
      
      const { token, user: userData } = response.data
      
      localStorage.setItem(TOKEN_KEY, token)
      
      // If user has brand_id and is not super_admin, fetch brand name
      if (userData.brand_id && userData.brand_role !== 'super_admin') {
        try {
          const brandResponse = await api.get(`/brands/${userData.brand_id}`)
          userData.brand_name = brandResponse.data.name
        } catch (error) {
          // If brand fetch fails, continue without brand_name
          console.warn('Failed to fetch brand name:', error)
        }
      }
      
      setUser(userData)
      
      // Redirect based on brand role
      if (userData.brand_role === 'super_admin') {
        navigate('/brands')
      } else if (userData.brand_role === 'brand_admin' || userData.brand_role === 'brand_user') {
        navigate('/chat')
      } else {
        // Fallback for any other role
        navigate('/brands')
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed')
    }
  }

  const logout = async () => {
    try {
      await api.post('/auth/logout')
    } catch (error) {
      // Even if logout fails, clear local state
      console.error('Logout error:', error)
    } finally {
      localStorage.removeItem(TOKEN_KEY)
      setUser(null)
      navigate('/login')
    }
  }

  useEffect(() => {
    checkAuth()
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated,
        loading,
        login,
        logout,
        checkAuth,
        isAdmin,
        isSuperAdmin,
        isBrandAdmin,
        isBrandUser,
        canManageBrand,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

