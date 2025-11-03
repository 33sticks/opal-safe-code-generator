import { useState, KeyboardEvent } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { Send, Loader2 } from 'lucide-react'

interface ChatInputProps {
  onSendMessage: (message: string) => void
  disabled?: boolean
  isGenerating?: boolean
}

export function ChatInput({ onSendMessage, disabled, isGenerating = false }: ChatInputProps) {
  const [message, setMessage] = useState('')

  const handleSend = () => {
    if (message.trim() && !disabled && !isGenerating) {
      onSendMessage(message.trim())
      setMessage('')
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="border-t p-4 flex gap-2">
      <Textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={
          isGenerating
            ? 'Generating code...'
            : 'Type your message... (Press Enter to send, Shift+Enter for new line)'
        }
        disabled={disabled || isGenerating}
        className="flex-1 min-h-[60px] max-h-[120px] resize-none"
      />
      <Button
        onClick={handleSend}
        disabled={!message.trim() || disabled || isGenerating}
        size="icon"
        className="h-[60px] w-[60px]"
      >
        {isGenerating ? (
          <Loader2 className="h-5 w-5 animate-spin" />
        ) : (
          <Send className="h-5 w-5" />
        )}
      </Button>
    </div>
  )
}

