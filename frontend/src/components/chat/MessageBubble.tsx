import { formatDistanceToNow } from 'date-fns'
import type { Message, GeneratedCode } from '@/types/chat'
import { CodeBlock } from './CodeBlock'

interface MessageBubbleProps {
  message: Message
  generatedCode?: GeneratedCode | null
}

export function MessageBubble({ message, generatedCode }: MessageBubbleProps) {
  const isUser = message.role === 'user'
  
  return (
    <div className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-[80%] ${isUser ? 'items-end' : 'items-start'} flex flex-col`}>
        <div
          className={`rounded-lg px-4 py-2 ${
            isUser
              ? 'bg-blue-500 text-white'
              : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
          }`}
        >
          <p className="whitespace-pre-wrap break-words">{message.content}</p>
        </div>
        {generatedCode && <CodeBlock code={generatedCode} />}
        <span className="text-xs text-muted-foreground mt-1">
          {formatDistanceToNow(new Date(message.created_at), { addSuffix: true })}
        </span>
      </div>
    </div>
  )
}

