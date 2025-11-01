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
        <MessageList messages={messages} generatedCodeMap={generatedCodeMap} />
        <ChatInput onSendMessage={onSendMessage} disabled={isSending} />
      </div>
    </div>
  )
}

