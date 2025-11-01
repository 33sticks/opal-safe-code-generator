import { useQuery } from '@tanstack/react-query'
import {
  getAnalyticsOverview,
  getUsageOverTime,
  getQualityMetrics,
  getBrandPerformance,
  getUserActivity,
  getLLMCosts,
  getLLMCostsByBrand,
} from '@/lib/api'
import type { AnalyticsParams } from '@/types/analytics'
import { useAuth } from '@/contexts/AuthContext'

export const useAnalyticsOverview = (params: AnalyticsParams) => {
  return useQuery({
    queryKey: ['analytics', 'overview', params],
    queryFn: () => getAnalyticsOverview(params),
  })
}

export const useUsageOverTime = (params: AnalyticsParams) => {
  return useQuery({
    queryKey: ['analytics', 'usage-over-time', params],
    queryFn: () => getUsageOverTime(params),
  })
}

export const useQualityMetrics = (params: AnalyticsParams) => {
  return useQuery({
    queryKey: ['analytics', 'quality-metrics', params],
    queryFn: () => getQualityMetrics(params),
  })
}

export const useBrandPerformance = (params: AnalyticsParams) => {
  return useQuery({
    queryKey: ['analytics', 'brand-performance', params],
    queryFn: () => getBrandPerformance(params),
  })
}

export const useUserActivity = (params: AnalyticsParams) => {
  return useQuery({
    queryKey: ['analytics', 'user-activity', params],
    queryFn: () => getUserActivity(params),
  })
}

export const useLLMCosts = (params: AnalyticsParams) => {
  const { isSuperAdmin } = useAuth()
  return useQuery({
    queryKey: ['analytics', 'llm-costs', params],
    queryFn: () => getLLMCosts(params),
    enabled: isSuperAdmin(), // Only fetch for super admins
  })
}

export const useLLMCostsByBrand = (params: AnalyticsParams) => {
  const { isSuperAdmin } = useAuth()
  return useQuery({
    queryKey: ['analytics', 'llm-costs-by-brand', params],
    queryFn: () => getLLMCostsByBrand(params),
    enabled: isSuperAdmin(), // Only fetch for super admins
  })
}

