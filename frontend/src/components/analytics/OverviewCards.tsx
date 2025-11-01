import { Card } from '@/components/ui/card'
import { Code, Users, TrendingUp, CheckCircle } from 'lucide-react'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import type { AnalyticsOverview } from '@/types/analytics'

interface OverviewCardsProps {
  data?: AnalyticsOverview
  isLoading: boolean
}

export function OverviewCards({ data, isLoading }: OverviewCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="p-6">
            <LoadingSpinner />
          </Card>
        ))}
      </div>
    )
  }

  if (!data) {
    return null
  }

  const cards = [
    {
      title: 'Total Code Generations',
      value: data.total_code_generations.toLocaleString(),
      icon: Code,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
    },
    {
      title: 'Active Users',
      value: data.active_users.toLocaleString(),
      icon: Users,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
    },
    {
      title: 'Average Confidence',
      value: `${(data.average_confidence * 100).toFixed(1)}%`,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
    },
    {
      title: 'Approval Rate',
      value: `${data.approval_rate.toFixed(1)}%`,
      icon: CheckCircle,
      color: 'text-emerald-600',
      bgColor: 'bg-emerald-50',
    },
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card) => {
        const Icon = card.icon
        return (
          <Card key={card.title} className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">{card.title}</p>
                <p className="text-2xl font-bold mt-2">{card.value}</p>
              </div>
              <div className={`${card.bgColor} ${card.color} p-3 rounded-lg`}>
                <Icon className="h-6 w-6" />
              </div>
            </div>
          </Card>
        )
      })}
    </div>
  )
}

