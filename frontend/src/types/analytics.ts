/** Analytics TypeScript types matching backend schemas */

export interface AnalyticsOverview {
  total_code_generations: number
  active_users: number
  average_confidence: number
  approval_rate: number
  rejection_rate: number
  period_start?: string | null
  period_end?: string | null
}

export interface UsageDataPoint {
  date: string
  count: number
  brand_name?: string | null
}

export interface QualityMetrics {
  confidence_distribution: Record<string, number>
  status_breakdown: Record<string, number>
  average_confidence: number
}

export interface BrandPerformance {
  brand_id: number
  brand_name: string
  code_generations: number
  average_confidence: number
  approval_rate: number
  top_users: string[]
}

export interface UserActivity {
  user_id: number
  user_email: string
  user_name?: string | null
  code_generations: number
  average_confidence: number
  last_active: string
}

export interface LLMCostMetrics {
  total_cost_usd: number
  average_cost_per_generation: number
  total_tokens: number
  total_generations: number
  period_start?: string | null
  period_end?: string | null
}

export interface BrandLLMCost {
  brand_name: string
  total_cost_usd: number
  generations: number
  cost_per_generation?: number | null
}

export interface AnalyticsParams {
  start_date?: string
  end_date?: string
  brand_id?: number
  interval?: 'day' | 'week' | 'month'
  limit?: number
}

