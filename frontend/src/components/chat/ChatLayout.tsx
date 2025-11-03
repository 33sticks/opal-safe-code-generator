import { ConversationsList } from './ConversationsList'
import { MessageList } from './MessageList'
import { ChatInput } from './ChatInput'
import type { ConversationPreview, Message, GeneratedCode } from '@/types/chat'

interface ChatLayoutProps {
  conversations: ConversationPreview[]
  selectedConversationId: string | null
  messages: Message[]
  generatedCodeMap: Map<number, GeneratedCode>
  onSelectConversation: (id: string) => void
  onNewChat: () => void
  onSendMessage: (message: string) => void
  isSending?: boolean
  isLoadingHistory?: boolean
  isGenerating?: boolean
  generationStatus?: string
  generationError?: string | null
  showSuccess?: boolean
  onRetry?: () => void
  onCancelGeneration?: () => void
}

export function ChatLayout({
  conversations,
  selectedConversationId,
  messages,
  generatedCodeMap,
  onSelectConversation,
  onNewChat,
  onSendMessage,
  isSending = false,
  isLoadingHistory = false,
  isGenerating = false,
  generationStatus = '',
  generationError = null,
  showSuccess = false,
  onRetry,
  onCancelGeneration,
}: ChatLayoutProps) {
  return (
    <div className="flex h-full">
      <ConversationsList
        conversations={conversations}
        selectedConversationId={selectedConversationId}
        onSelectConversation={onSelectConversation}
        onNewChat={onNewChat}
      />
      <div className="flex-1 flex flex-col">
        <MessageList
          messages={messages}
          generatedCodeMap={generatedCodeMap}
          isLoading={isLoadingHistory}
          isGenerating={isGenerating}
          generationStatus={generationStatus}
          generationError={generationError}
          showSuccess={showSuccess}
          onRetry={onRetry}
          onCancelGeneration={onCancelGeneration}
        />
        <ChatInput
          onSendMessage={onSendMessage}
          disabled={isSending || isGenerating}
          isGenerating={isGenerating}
        />
      </div>
    </div>
  )
}

