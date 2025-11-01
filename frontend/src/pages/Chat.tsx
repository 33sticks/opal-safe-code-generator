import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ChatLayout } from '@/components/chat/ChatLayout'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { sendChatMessage, getConversations, getConversation } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import type { Message, ConversationPreview, ChatMessageResponse, GeneratedCode } from '@/types/chat'

export function Chat() {
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [generatedCodeMap, setGeneratedCodeMap] = useState<Map<number, GeneratedCode>>(new Map())
  const { toast } = useToast()
  const queryClient = useQueryClient()

  // Fetch conversations list
  const {
    data: conversations = [],
    isLoading: conversationsLoading,
    error: conversationsError,
  } = useQuery<ConversationPreview[]>({
    queryKey: ['chat', 'conversations'],
    queryFn: getConversations,
  })

  // Fetch conversation history when selected
  const {
    data: conversationHistory,
    isLoading: historyLoading,
  } = useQuery({
    queryKey: ['chat', 'conversation', selectedConversationId],
    queryFn: () => getConversation(selectedConversationId!),
    enabled: !!selectedConversationId,
  })

  // Update messages and generated code when history loads
  useEffect(() => {
    if (conversationHistory) {
      setMessages(conversationHistory.messages)
      
      // Build generated code map
      const codeMap = new Map<number, GeneratedCode>()
      if (conversationHistory.generated_code) {
        conversationHistory.messages.forEach((msg) => {
          if (msg.generated_code_id && conversationHistory.generated_code) {
            codeMap.set(msg.generated_code_id, conversationHistory.generated_code)
          }
        })
      }
      setGeneratedCodeMap(codeMap)
    } else if (!selectedConversationId) {
      setMessages([])
      setGeneratedCodeMap(new Map())
    }
  }, [conversationHistory, selectedConversationId])

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: ({ message, conversationId }: { message: string; conversationId?: string | null }) =>
      sendChatMessage(message, conversationId),
    onMutate: async ({ message }) => {
      // Optimistic update - add user message
      const optimisticMessage: Message = {
        id: Date.now(), // Temporary ID
        role: 'user',
        content: message,
        created_at: new Date().toISOString(),
        generated_code_id: null,
      }
      setMessages((prev) => [...prev, optimisticMessage])
    },
    onSuccess: (response: ChatMessageResponse) => {
      // Add assistant response
      const assistantMessage: Message = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.message,
        created_at: new Date().toISOString(),
        generated_code_id: response.generated_code?.id || null,
      }
      setMessages((prev) => [...prev, assistantMessage])
      
      // Update generated code map if code was generated
      if (response.generated_code) {
        setGeneratedCodeMap((prev) => {
          const newMap = new Map(prev)
          newMap.set(response.generated_code!.id, response.generated_code!)
          return newMap
        })
      }
      
      // Update selected conversation ID if it's new
      if (!selectedConversationId) {
        setSelectedConversationId(response.conversation_id)
      }
      
      // Invalidate conversations list to refresh
      queryClient.invalidateQueries({ queryKey: ['chat', 'conversations'] })
      queryClient.invalidateQueries({
        queryKey: ['chat', 'conversation', response.conversation_id],
      })
    },
    onError: (error: Error) => {
      toast({
        title: 'Error',
        description: error.message || 'Failed to send message',
        variant: 'destructive',
      })
      // Remove optimistic message on error
      setMessages((prev) => prev.slice(0, -1))
    },
  })

  const handleSendMessage = (message: string) => {
    sendMessageMutation.mutate({
      message,
      conversationId: selectedConversationId,
    })
  }

  const handleSelectConversation = (id: string) => {
    setSelectedConversationId(id)
  }

  const handleNewChat = () => {
    setSelectedConversationId(null)
    setMessages([])
    setGeneratedCodeMap(new Map())
  }

  if (conversationsError) {
    return (
      <div className="flex h-full items-center justify-center p-8">
        <div className="text-center space-y-4">
          <h1 className="text-2xl font-bold text-destructive">Error Loading Conversations</h1>
          <p className="text-muted-foreground">
            {(conversationsError as Error).message || 'Failed to load conversations'}
          </p>
        </div>
      </div>
    )
  }

  if (conversationsLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  // Show loading in message area when loading history
  const isLoadingHistory = historyLoading && !!selectedConversationId

  return (
    <div className="h-full flex flex-col">
      <ChatLayout
        conversations={conversations}
        selectedConversationId={selectedConversationId}
        messages={messages}
        generatedCodeMap={generatedCodeMap}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onSendMessage={handleSendMessage}
        isSending={sendMessageMutation.isPending}
        isLoadingHistory={isLoadingHistory}
      />
    </div>
  )
}
