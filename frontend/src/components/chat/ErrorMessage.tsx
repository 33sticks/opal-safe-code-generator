import { AlertCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ErrorMessageProps {
  message: string
  onRetry?: () => void
}

export function ErrorMessage({ message, onRetry }: ErrorMessageProps) {
  return (
    <div className="flex items-start gap-3 p-4 bg-red-50 dark:bg-red-950 rounded-lg">
      <AlertCircle className="h-5 w-5 text-red-500 mt-0.5" />
      <div className="flex-1">
        <p className="font-medium text-red-700 dark:text-red-300">Code generation failed</p>
        <p className="text-sm text-red-600 dark:text-red-400 mt-1">{message}</p>
        {onRetry && (
          <Button
            variant="outline"
            size="sm"
            className="mt-2 border-red-300 text-red-700 hover:bg-red-100 dark:border-red-800 dark:text-red-300 dark:hover:bg-red-900"
            onClick={onRetry}
          >
            Try Again
          </Button>
        )}
      </div>
    </div>
  )
}

