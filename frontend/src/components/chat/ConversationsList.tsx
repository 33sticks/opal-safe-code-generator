import { formatDistanceToNow, isToday, isYesterday, format } from 'date-fns'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import type { ConversationPreview } from '@/types/chat'

interface ConversationsListProps {
  conversations: ConversationPreview[]
  selectedConversationId: string | null
  onSelectConversation: (id: string) => void
  onNewChat: () => void
}

export function ConversationsList({
  conversations,
  selectedConversationId,
  onSelectConversation,
  onNewChat,
}: ConversationsListProps) {
  const groupConversationsByDate = () => {
    const today: ConversationPreview[] = []
    const yesterday: ConversationPreview[] = []
    const older: ConversationPreview[] = []

    conversations.forEach((conv) => {
      const date = new Date(conv.updated_at)
      if (isToday(date)) {
        today.push(conv)
      } else if (isYesterday(date)) {
        yesterday.push(conv)
      } else {
        older.push(conv)
      }
    })

    return { today, yesterday, older }
  }

  const { today, yesterday, older } = groupConversationsByDate()

  const renderConversationGroup = (title: string, convs: ConversationPreview[]) => {
    if (convs.length === 0) return null

    return (
      <div className="mb-4">
        <h3 className="text-xs font-semibold text-muted-foreground mb-2 px-3">
          {title}
        </h3>
        {convs.map((conv) => (
          <button
            key={conv.id}
            onClick={() => onSelectConversation(conv.id)}
            className={`w-full text-left px-3 py-2 rounded-md mb-1 hover:bg-accent transition-colors ${
              selectedConversationId === conv.id
                ? 'bg-accent font-medium'
                : ''
            }`}
          >
            <div className="truncate text-sm">{conv.preview}</div>
            {conv.last_message && (
              <div className="text-xs text-muted-foreground truncate mt-1">
                {conv.last_message}
              </div>
            )}
            <div className="text-xs text-muted-foreground mt-1">
              {formatDistanceToNow(new Date(conv.updated_at), { addSuffix: true })}
            </div>
          </button>
        ))}
      </div>
    )
  }

  return (
    <div className="w-64 border-r flex flex-col h-full bg-muted/30">
      <div className="p-4 border-b">
        <Button onClick={onNewChat} className="w-full" size="sm">
          <Plus className="h-4 w-4 mr-2" />
          New Chat
        </Button>
      </div>
      <div className="flex-1 overflow-y-auto p-2">
        {conversations.length === 0 ? (
          <div className="text-center text-sm text-muted-foreground p-4">
            No conversations yet. Start a new chat!
          </div>
        ) : (
          <>
            {renderConversationGroup('Today', today)}
            {renderConversationGroup('Yesterday', yesterday)}
            {renderConversationGroup('Older', older)}
          </>
        )}
      </div>
    </div>
  )
}

