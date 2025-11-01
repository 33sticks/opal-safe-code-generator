import { Card } from '@/components/ui/card'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { DollarSign } from 'lucide-react'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import { format } from 'date-fns'
import type { LLMCostMetrics, UsageDataPoint } from '@/types/analytics'

interface LLMCostOverviewProps {
  data?: LLMCostMetrics
  costOverTime?: UsageDataPoint[]
  isLoading: boolean
}

export function LLMCostOverview({ data, costOverTime, isLoading }: LLMCostOverviewProps) {
  if (isLoading) {
    return (
      <Card className="p-6">
        <LoadingSpinner />
      </Card>
    )
  }

  if (!data) {
    return (
      <Card className="p-6">
        <EmptyState
          icon={<DollarSign className="h-12 w-12 text-muted-foreground" />}
          title="No cost data"
          description="Cost data is only available for new code generations"
        />
      </Card>
    )
  }

  const costChartData = costOverTime?.map((point) => ({
    date: format(new Date(point.date), 'MMM dd'),
    cost: point.count * (data.average_cost_per_generation || 0),
  }))

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">LLM Usage & Costs</h3>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="p-4 bg-blue-50 rounded-lg">
          <p className="text-sm text-muted-foreground">Total Cost</p>
          <p className="text-2xl font-bold mt-1">${data.total_cost_usd.toFixed(2)}</p>
        </div>
        <div className="p-4 bg-green-50 rounded-lg">
          <p className="text-sm text-muted-foreground">Avg per Generation</p>
          <p className="text-2xl font-bold mt-1">${data.average_cost_per_generation.toFixed(4)}</p>
        </div>
        <div className="p-4 bg-purple-50 rounded-lg">
          <p className="text-sm text-muted-foreground">Total Tokens</p>
          <p className="text-2xl font-bold mt-1">
            {(data.total_tokens / 1_000_000).toFixed(2)}M
          </p>
        </div>
        <div className="p-4 bg-orange-50 rounded-lg">
          <p className="text-sm text-muted-foreground">Generations</p>
          <p className="text-2xl font-bold mt-1">{data.total_generations.toLocaleString()}</p>
        </div>
      </div>
      {costChartData && costChartData.length > 0 && (
        <div>
          <h4 className="text-sm font-medium mb-2">Cost Trend Over Time</h4>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={costChartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value) => `$${Number(value).toFixed(2)}`} />
              <Legend />
              <Line
                type="monotone"
                dataKey="cost"
                stroke="#8884d8"
                strokeWidth={2}
                name="Daily Cost"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </Card>
  )
}

