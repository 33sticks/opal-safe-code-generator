import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { LoadingMessage } from './LoadingMessage'
import { ErrorMessage } from './ErrorMessage'
import { CheckCircle } from 'lucide-react'
import type { Message, GeneratedCode } from '@/types/chat'

interface MessageListProps {
  messages: Message[]
  generatedCodeMap: Map<number, GeneratedCode>
  isLoading?: boolean
  isGenerating?: boolean
  generationStatus?: string
  generationError?: string | null
  showSuccess?: boolean
  onRetry?: () => void
  onCancelGeneration?: () => void
}

export function MessageList({
  messages,
  generatedCodeMap,
  isLoading = false,
  isGenerating = false,
  generationStatus = '',
  generationError = null,
  showSuccess = false,
  onRetry,
  onCancelGeneration,
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isGenerating, generationError])

  if (isLoading) {
    return (
      <div className="flex-1 overflow-y-auto p-4 flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div className="flex-1 overflow-y-auto p-4">
      <div className="space-y-2">
        {messages.length === 0 && !isGenerating && !generationError ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p>No messages yet. Start a conversation!</p>
          </div>
        ) : (
          <>
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                generatedCode={
                  message.generated_code_id
                    ? generatedCodeMap.get(message.generated_code_id) || null
                    : null
                }
              />
            ))}
            {showSuccess && (
              <div className="flex items-center gap-2 text-green-600 dark:text-green-400 p-2">
                <CheckCircle className="h-5 w-5" />
                <span className="text-sm font-medium">Code generated successfully!</span>
              </div>
            )}
            {isGenerating && (
              <LoadingMessage
                status={generationStatus || 'Generating code...'}
                onCancel={onCancelGeneration}
              />
            )}
            {generationError && !isGenerating && (
              <ErrorMessage message={generationError} onRetry={onRetry} />
            )}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}

