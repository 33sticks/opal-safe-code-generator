import { useState } from 'react'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { Building2, BarChart } from 'lucide-react'
import {
  BarChart as RechartsBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import type { BrandPerformance } from '@/types/analytics'

interface BrandPerformanceProps {
  data?: BrandPerformance[]
  isLoading: boolean
}

export function BrandPerformanceComponent({ data, isLoading }: BrandPerformanceProps) {
  const [viewMode, setViewMode] = useState<'chart' | 'table'>('chart')

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
          icon={<Building2 className="h-12 w-12 text-muted-foreground" />}
          title="No brand performance data"
          description="No code generations found for this period"
        />
      </Card>
    )
  }

  const chartData = data.map((brand) => ({
    name: brand.brand_name,
    generations: brand.code_generations,
    confidence: Math.round(brand.average_confidence * 100),
    approvalRate: Math.round(brand.approval_rate),
  }))

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Brand Performance</h3>
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'chart' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('chart')}
          >
            <BarChart className="h-4 w-4 mr-2" />
            Chart
          </Button>
          <Button
            variant={viewMode === 'table' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setViewMode('table')}
          >
            Table
          </Button>
        </div>
      </div>
      {viewMode === 'chart' ? (
        <ResponsiveContainer width="100%" height={300}>
          <RechartsBarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="generations" fill="#8884d8" name="Code Generations" />
          </RechartsBarChart>
        </ResponsiveContainer>
      ) : (
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Brand</TableHead>
                <TableHead>Generations</TableHead>
                <TableHead>Avg Confidence</TableHead>
                <TableHead>Approval Rate</TableHead>
                <TableHead>Top Users</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {data.map((brand) => (
                <TableRow key={brand.brand_id}>
                  <TableCell className="font-medium">{brand.brand_name}</TableCell>
                  <TableCell>{brand.code_generations}</TableCell>
                  <TableCell>{Math.round(brand.average_confidence * 100)}%</TableCell>
                  <TableCell>{brand.approval_rate.toFixed(1)}%</TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {brand.top_users.slice(0, 3).join(', ')}
                    {brand.top_users.length > 3 && '...'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      )}
    </Card>
  )
}

