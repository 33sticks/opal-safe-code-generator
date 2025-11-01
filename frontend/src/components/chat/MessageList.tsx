import { useEffect, useRef } from 'react'
import { MessageBubble } from './MessageBubble'
import type { Message, GeneratedCode } from '@/types/chat'

interface MessageListProps {
  messages: Message[]
  generatedCodeMap: Map<number, GeneratedCode>
}

export function MessageList({ messages, generatedCodeMap }: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  return (
    <div className="flex-1 overflow-y-auto p-4">
      <div className="space-y-2">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            <p>No messages yet. Start a conversation!</p>
          </div>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              generatedCode={
                message.generated_code_id
                  ? generatedCodeMap.get(message.generated_code_id) || null
                  : null
              }
            />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
    </div>
  )
}

