import { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ChatLayout } from '@/components/chat/ChatLayout'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { CheckCircle } from 'lucide-react'
import { sendChatMessage, getConversations, getConversation } from '@/lib/api'
import { useToast } from '@/hooks/use-toast'
import { useAuth } from '@/contexts/AuthContext'
import type { Message, ConversationPreview, ChatMessageResponse, GeneratedCode } from '@/types/chat'

const GENERATION_TIMEOUT = 30000 // 30 seconds
const PROGRESS_UPDATE_INTERVAL = 1500 // 1.5 seconds

const PROGRESS_STEPS = [
  'Analyzing your request...',
  'Searching for relevant selectors...',
  'Building context for AI...',
  'Generating code...',
  'Validating output...',
  'Almost done...',
]

export function Chat() {
  const [selectedConversationId, setSelectedConversationId] = useState<string | null>(null)
  const [messages, setMessages] = useState<Message[]>([])
  const [generatedCodeMap, setGeneratedCodeMap] = useState<Map<number, GeneratedCode>>(new Map())
  const [showCodeSubmitted, setShowCodeSubmitted] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [generationStatus, setGenerationStatus] = useState<string>('')
  const [generationError, setGenerationError] = useState<string | null>(null)
  const [showSuccess, setShowSuccess] = useState(false)
  const [lastMessageForRetry, setLastMessageForRetry] = useState<string | null>(null)
  const progressIntervalRef = useRef<NodeJS.Timeout | null>(null)
  const timeoutRef = useRef<NodeJS.Timeout | null>(null)
  const { toast } = useToast()
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const { isSuperAdmin } = useAuth()

  // Redirect super admins away from chat
  useEffect(() => {
    if (isSuperAdmin()) {
      navigate('/brands', { replace: true })
    }
  }, [isSuperAdmin, navigate])

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

  // Cleanup intervals on unmount
  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  // Simulate progress updates
  const simulateProgress = () => {
    let currentStep = 0
    setGenerationStatus(PROGRESS_STEPS[0])

    progressIntervalRef.current = setInterval(() => {
      currentStep++
      if (currentStep < PROGRESS_STEPS.length) {
        setGenerationStatus(PROGRESS_STEPS[currentStep])
      }
    }, PROGRESS_UPDATE_INTERVAL)

    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
        progressIntervalRef.current = null
      }
    }
  }

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
      // Clear any previous errors
      setGenerationError(null)
      setLastMessageForRetry(message)
      
      // Start loading state and progress simulation for code generation
      // (We don't know if it will generate code yet, but we'll show loading during the request)
      setIsGenerating(true)
      simulateProgress()
      
      // Set timeout
      timeoutRef.current = setTimeout(() => {
        setIsGenerating(false)
        setGenerationError('Code generation is taking longer than expected. Please try again.')
        if (progressIntervalRef.current) {
          clearInterval(progressIntervalRef.current)
          progressIntervalRef.current = null
        }
        toast({
          title: 'Timeout',
          description: 'Code generation is taking longer than expected. Please try again.',
          variant: 'destructive',
        })
      }, GENERATION_TIMEOUT)
      
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
      // Clear timeout and progress interval
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
        progressIntervalRef.current = null
      }

      // Stop loading state
      setIsGenerating(false)
      setGenerationStatus('')
      setLastMessageForRetry(null)

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
        // Show success message
        setShowCodeSubmitted(true)
        // Show success animation
        setShowSuccess(true)
        setTimeout(() => setShowSuccess(false), 2000)
        // Auto-hide after 10 seconds
        setTimeout(() => setShowCodeSubmitted(false), 10000)
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
      // Clear loading state on error
      setIsGenerating(false)
      setGenerationStatus('')
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current)
        progressIntervalRef.current = null
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
        timeoutRef.current = null
      }

      setGenerationError(error.message || 'Failed to generate code')
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
    setGenerationError(null)
    sendMessageMutation.mutate({
      message,
      conversationId: selectedConversationId,
    })
  }

  const handleRetry = () => {
    if (lastMessageForRetry) {
      setGenerationError(null)
      sendMessageMutation.mutate({
        message: lastMessageForRetry,
        conversationId: selectedConversationId,
      })
    }
  }

  const handleCancelGeneration = () => {
    // UI-only cancel - doesn't abort backend request
    setIsGenerating(false)
    setGenerationStatus('')
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current)
      progressIntervalRef.current = null
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
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
      {showCodeSubmitted && (
        <Card className="m-4 border-green-200 bg-green-50 dark:bg-green-950">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-green-600 dark:text-green-400" />
                <span className="text-sm font-medium text-green-900 dark:text-green-100">
                  Code submitted for review
                </span>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    navigate('/my-requests')
                    setShowCodeSubmitted(false)
                  }}
                >
                  View My Requests
                </Button>
                <button
                  onClick={() => setShowCodeSubmitted(false)}
                  className="text-green-600 hover:text-green-800"
                >
                  ×
                </button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
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
        isGenerating={isGenerating}
        generationStatus={generationStatus}
        generationError={generationError}
        showSuccess={showSuccess}
        onRetry={handleRetry}
        onCancelGeneration={handleCancelGeneration}
      />
    </div>
  )
}
