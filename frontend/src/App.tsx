import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from '@/components/ui/toaster'
import { Layout } from '@/components/layout/Layout'
import { BrandsPage } from '@/pages/Brands/BrandsPage'
import { TemplatesPage } from '@/pages/Templates/TemplatesPage'
import { SelectorsPage } from '@/pages/Selectors/SelectorsPage'
import { RulesPage } from '@/pages/Rules/RulesPage'
import { GeneratedCodePage } from '@/pages/GeneratedCode/GeneratedCodePage'

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
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/brands" replace />} />
            <Route path="/brands" element={<BrandsPage />} />
            <Route path="/templates" element={<TemplatesPage />} />
            <Route path="/selectors" element={<SelectorsPage />} />
            <Route path="/rules" element={<RulesPage />} />
            <Route path="/generated-code" element={<GeneratedCodePage />} />
          </Routes>
        </Layout>
        <Toaster />
      </BrowserRouter>
    </QueryClientProvider>
  )
}

export default App

