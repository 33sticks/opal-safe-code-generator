import { useState, useEffect } from 'react'
import { subDays, format } from 'date-fns'
import { DateRangePicker } from '@/components/analytics/DateRangePicker'
import { OverviewCards } from '@/components/analytics/OverviewCards'
import { UsageChart } from '@/components/analytics/UsageChart'
import { BrandPerformanceComponent } from '@/components/analytics/BrandPerformance'
import { QualityMetricsComponent } from '@/components/analytics/QualityMetrics'
import { LLMCostOverview } from '@/components/analytics/LLMCostOverview'
import { LLMCostByBrand } from '@/components/analytics/LLMCostByBrand'
import {
  useAnalyticsOverview,
  useUsageOverTime,
  useQualityMetrics,
  useBrandPerformance,
  useLLMCosts,
  useLLMCostsByBrand,
} from '@/hooks/useAnalytics'
import { useAuth } from '@/contexts/AuthContext'
import type { AnalyticsParams } from '@/types/analytics'

export function AnalyticsPage() {
  const { isSuperAdmin } = useAuth()
  const [dateRange, setDateRange] = useState({
    start: subDays(new Date(), 30),
    end: new Date(),
  })
  const [interval, setInterval] = useState<'day' | 'week' | 'month'>('day')

  const params: AnalyticsParams = {
    start_date: format(dateRange.start, 'yyyy-MM-dd'),
    end_date: format(dateRange.end, 'yyyy-MM-dd'),
    interval,
  }

  const overviewQuery = useAnalyticsOverview(params)
  const usageQuery = useUsageOverTime({ ...params, interval })
  const qualityQuery = useQualityMetrics(params)
  const brandQuery = useBrandPerformance(params)
  const llmCostsQuery = useLLMCosts(params)
  const llmCostsByBrandQuery = useLLMCostsByBrand(params)

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
        <DateRangePicker
          onRangeChange={setDateRange}
          defaultRange={dateRange}
        />
      </div>

      <OverviewCards data={overviewQuery.data} isLoading={overviewQuery.isLoading} />

      <UsageChart
        data={usageQuery.data}
        isLoading={usageQuery.isLoading}
        onIntervalChange={setInterval}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <BrandPerformanceComponent
          data={brandQuery.data}
          isLoading={brandQuery.isLoading}
        />
        <QualityMetricsComponent
          data={qualityQuery.data}
          isLoading={qualityQuery.isLoading}
        />
      </div>

      {isSuperAdmin() && (
        <div className="space-y-6">
          <LLMCostOverview
            data={llmCostsQuery.data}
            isLoading={llmCostsQuery.isLoading}
          />
          <LLMCostByBrand
            data={llmCostsByBrandQuery.data}
            isLoading={llmCostsByBrandQuery.isLoading}
          />
        </div>
      )}
    </div>
  )
}

