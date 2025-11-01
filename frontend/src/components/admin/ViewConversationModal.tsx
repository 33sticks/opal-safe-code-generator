import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { MessageList } from '@/components/chat/MessageList'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import type { ConversationForCodeResponse } from '@/types/chat'
import type { Message } from '@/types/chat'

interface ViewConversationModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  conversation: ConversationForCodeResponse | null
  isLoading?: boolean
}

export function ViewConversationModal({
  open,
  onOpenChange,
  conversation,
  isLoading = false,
}: ViewConversationModalProps) {
  // Convert conversation messages to Message format for MessageList
  const messages: Message[] = conversation?.messages.map((msg, index) => ({
    id: index,
    role: msg.role,
    content: msg.content,
    created_at: msg.created_at || new Date().toISOString(),
    generated_code_id: null,
  })) || []

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Conversation History</DialogTitle>
          <DialogDescription>
            {conversation && (
              <div className="space-y-1 mt-2">
                <div>
                  <span className="font-medium">User:</span> {conversation.user.email}
                  {conversation.user.name && ` (${conversation.user.name})`}
                </div>
                {conversation.brand && (
                  <div>
                    <span className="font-medium">Brand:</span> {conversation.brand.name}
                  </div>
                )}
              </div>
            )}
          </DialogDescription>
        </DialogHeader>
        <div className="flex-1 overflow-hidden min-h-0">
          {isLoading ? (
            <div className="flex items-center justify-center h-full">
              <LoadingSpinner size="lg" />
            </div>
          ) : conversation ? (
            <div className="h-full overflow-y-auto">
              <MessageList messages={messages} generatedCodeMap={new Map()} />
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-muted-foreground">
              <p>No conversation available</p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

