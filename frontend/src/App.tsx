import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from '@/components/ui/toaster'
import { AuthProvider } from '@/contexts/AuthContext'
import { ProtectedRoute } from '@/components/ProtectedRoute'
import { Layout } from '@/components/layout/Layout'
import { Login } from '@/pages/Login'
import { ForgotPassword } from '@/pages/ForgotPassword'
import { Chat } from '@/pages/Chat'
import { BrandsPage } from '@/pages/Brands/BrandsPage'
import { TemplatesPage } from '@/pages/Templates/TemplatesPage'
import { SelectorsPage } from '@/pages/Selectors/SelectorsPage'
import { RulesPage } from '@/pages/Rules/RulesPage'
import { GeneratedCodePage } from '@/pages/GeneratedCode/GeneratedCodePage'
import { Notifications } from '@/pages/Notifications'
import { MyRequests } from '@/pages/MyRequests'
import { UsersPage } from '@/pages/Users/UsersPage'
import { AnalyticsPage } from '@/pages/Analytics/AnalyticsPage'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            
            {/* Protected routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Navigate to="/brands" replace />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Chat />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/brands"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Layout>
                    <BrandsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/templates"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Layout>
                    <TemplatesPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/selectors"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Layout>
                    <SelectorsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/rules"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Layout>
                    <RulesPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/generated-code"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Layout>
                    <GeneratedCodePage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/users"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Layout>
                    <UsersPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute requiredRole="admin">
                  <Layout>
                    <AnalyticsPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/notifications"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Notifications />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/my-requests"
              element={
                <ProtectedRoute>
                  <Layout>
                    <MyRequests />
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
          <Toaster />
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

