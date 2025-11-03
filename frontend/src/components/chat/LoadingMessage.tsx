import { Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface LoadingMessageProps {
  status: string
  onCancel?: () => void
}

export function LoadingMessage({ status, onCancel }: LoadingMessageProps) {
  return (
    <div className="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
      <Loader2 className="animate-spin h-5 w-5 text-blue-500 mt-0.5" />
      <div className="flex-1">
        <p className="text-sm text-gray-700 dark:text-gray-300">{status}</p>
        <div className="flex gap-1 mt-2">
          <div
            className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
            style={{ animationDelay: '0s' }}
          />
          <div
            className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
            style={{ animationDelay: '0.2s' }}
          />
          <div
            className="w-2 h-2 bg-blue-500 rounded-full animate-bounce"
            style={{ animationDelay: '0.4s' }}
          />
        </div>
      </div>
      {onCancel && (
        <Button variant="ghost" size="sm" onClick={onCancel}>
          Cancel
        </Button>
      )}
    </div>
  )
}

