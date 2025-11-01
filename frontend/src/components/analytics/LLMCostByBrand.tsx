import { Card } from '@/components/ui/card'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { Building2 } from 'lucide-react'
import {
  BarChart,
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
import type { BrandLLMCost } from '@/types/analytics'

interface LLMCostByBrandProps {
  data?: BrandLLMCost[]
  isLoading: boolean
}

export function LLMCostByBrand({ data, isLoading }: LLMCostByBrandProps) {
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
          title="No cost data by brand"
          description="No cost data available for this period"
        />
      </Card>
    )
  }

  const chartData = data.map((brand) => ({
    name: brand.brand_name,
    cost: brand.total_cost_usd,
    generations: brand.generations,
  }))

  return (
    <Card className="p-6">
      <h3 className="text-lg font-semibold mb-4">LLM Costs by Brand</h3>
      <div className="mb-6">
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip formatter={(value) => `$${Number(value).toFixed(2)}`} />
            <Legend />
            <Bar dataKey="cost" fill="#8884d8" name="Total Cost (USD)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Brand</TableHead>
              <TableHead>Total Cost</TableHead>
              <TableHead>Generations</TableHead>
              <TableHead>Cost per Generation</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((brand) => (
              <TableRow key={brand.brand_name}>
                <TableCell className="font-medium">{brand.brand_name}</TableCell>
                <TableCell>${brand.total_cost_usd.toFixed(2)}</TableCell>
                <TableCell>{brand.generations}</TableCell>
                <TableCell>
                  {brand.cost_per_generation
                    ? `$${brand.cost_per_generation.toFixed(4)}`
                    : 'N/A'}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  )
}

