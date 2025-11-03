import { Star } from 'lucide-react'
import { cn } from '@/lib/utils'

interface StabilityScoreProps {
  score: number
}

export function StabilityScore({ score }: StabilityScoreProps) {
  const stars = Math.round(score * 5)
  
  // Determine color based on score
  const getStarColor = (index: number) => {
    if (index < stars) {
      if (score > 0.8) {
        return 'fill-green-500 text-green-500'
      } else if (score >= 0.5) {
        return 'fill-yellow-500 text-yellow-500'
      } else {
        return 'fill-red-500 text-red-500'
      }
    }
    return 'text-gray-300'
  }

  return (
    <div className="flex items-center gap-1">
      {[...Array(5)].map((_, i) => (
        <Star
          key={i}
          className={cn('h-4 w-4', getStarColor(i))}
        />
      ))}
      <span className="text-sm text-gray-600 ml-2">({score.toFixed(2)})</span>
    </div>
  )
}

