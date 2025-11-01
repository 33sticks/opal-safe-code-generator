import { Card } from '@/components/ui/card'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { TrendingUp } from 'lucide-react'
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import type { QualityMetrics } from '@/types/analytics'

interface QualityMetricsProps {
  data?: QualityMetrics
  isLoading: boolean
}

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00']

export function QualityMetricsComponent({ data, isLoading }: QualityMetricsProps) {
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
          icon={<TrendingUp className="h-12 w-12 text-muted-foreground" />}
          title="No quality metrics"
          description="No data available for this period"
        />
      </Card>
    )
  }

  // Format confidence distribution for pie chart
  const confidenceData = Object.entries(data.confidence_distribution).map(([name, value]) => ({
    name,
    value,
  }))

  // Format status breakdown for bar chart
  const statusData = Object.entries(data.status_breakdown).map(([name, value]) => ({
    name,
    count: value,
  }))

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">Quality Metrics</h3>
      <div className="space-y-6">
        <div>
          <h4 className="text-sm font-medium mb-2">Confidence Distribution</h4>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie
                data={confidenceData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {confidenceData.map((_entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div>
          <h4 className="text-sm font-medium mb-2">Status Breakdown</h4>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={statusData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="pt-4 border-t">
          <div className="flex justify-between items-center">
            <span className="text-sm text-muted-foreground">Average Confidence</span>
            <span className="text-lg font-semibold">
              {(data.average_confidence * 100).toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    </Card>
  )
}

