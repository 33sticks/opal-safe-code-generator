import { cn } from '@/lib/utils'
import type { CodeStatus } from '@/types'

interface StatusBadgeProps {
  status: CodeStatus
  className?: string
}

const statusStyles: Record<CodeStatus, string> = {
  generated: 'bg-gray-100 text-gray-800 border-gray-300',
  reviewed: 'bg-blue-100 text-blue-800 border-blue-300',
  approved: 'bg-green-100 text-green-800 border-green-300',
  rejected: 'bg-red-100 text-red-800 border-red-300',
  deployed: 'bg-purple-100 text-purple-800 border-purple-300',
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold capitalize',
        statusStyles[status],
        className
      )}
    >
      {status}
    </span>
  )
}

