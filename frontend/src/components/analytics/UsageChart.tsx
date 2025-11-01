import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { BarChart3 } from 'lucide-react'
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
import type { UsageDataPoint } from '@/types/analytics'

interface UsageChartProps {
  data?: UsageDataPoint[]
  isLoading: boolean
  onIntervalChange?: (interval: 'day' | 'week' | 'month') => void
}

export function UsageChart({ data, isLoading, onIntervalChange }: UsageChartProps) {
  const [interval, setInterval] = useState<'day' | 'week' | 'month'>('day')

  const handleIntervalChange = (newInterval: 'day' | 'week' | 'month') => {
    setInterval(newInterval)
    onIntervalChange?.(newInterval)
  }

  if (isLoading) {
    return (
      <Card className="p-6">
        <LoadingSpinner />
      </Card>
    )
  }

  if (!data || data.length === 0) {
    return (
      <Card className="p-6">
        <EmptyState
          icon={<BarChart3 className="h-12 w-12 text-muted-foreground" />}
          title="No usage data yet"
          description="Generate some code to see usage trends"
        />
      </Card>
    )
  }

  // Format data for chart
  const chartData = data.map((point) => ({
    date: format(new Date(point.date), interval === 'month' ? 'MMM yyyy' : 'MMM dd'),
    count: point.count,
    fullDate: point.date,
  }))

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Usage Over Time</h3>
        <div className="flex gap-2">
          <Button
            variant={interval === 'day' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handleIntervalChange('day')}
          >
            Day
          </Button>
          <Button
            variant={interval === 'week' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handleIntervalChange('week')}
          >
            Week
          </Button>
          <Button
            variant={interval === 'month' ? 'default' : 'outline'}
            size="sm"
            onClick={() => handleIntervalChange('month')}
          >
            Month
          </Button>
        </div>
      </div>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="count"
            stroke="#8884d8"
            strokeWidth={2}
            name="Code Generations"
          />
        </LineChart>
      </ResponsiveContainer>
    </Card>
  )
}

