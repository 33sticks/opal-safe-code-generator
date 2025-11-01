import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMyRequests } from '@/hooks/useApi'
import { StatusBadge } from '@/components/admin/StatusBadge'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Code, Download, Copy, Eye, MessageSquare } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { cn } from '@/lib/utils'
import { useToast } from '@/hooks/use-toast'
import type { GeneratedCode } from '@/types'

export function MyRequests() {
  const [filter, setFilter] = useState<'all' | 'pending' | 'approved' | 'rejected'>('all')
  // Always fetch all requests to calculate counts correctly
  const { data: allRequests = [], isLoading, error } = useMyRequests()
  const navigate = useNavigate()
  const { toast } = useToast()


  // Calculate counts from all requests
  const pendingCount = allRequests.filter(r => r.status === 'generated' || r.status === 'reviewed').length
  const approvedCount = allRequests.filter(r => r.status === 'approved').length
  const rejectedCount = allRequests.filter(r => r.status === 'rejected').length

  // Filter requests based on selected filter
  const filteredRequests = allRequests.filter(r => {
    if (filter === 'all') return true
    if (filter === 'pending') return r.status === 'generated' || r.status === 'reviewed'
    return r.status === filter
  })

  const handleCopyCode = (code: string) => {
    navigator.clipboard.writeText(code)
    toast({
      title: 'Copied!',
      description: 'Code copied to clipboard',
    })
  }

  const handleDownloadCode = (code: string, brandName?: string) => {
    const blob = new Blob([code], { type: 'text/javascript' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${brandName || 'code'}-${Date.now()}.js`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    toast({
      title: 'Downloaded!',
      description: 'Code file downloaded',
    })
  }

  const handleViewConversation = (conversationId?: string | null) => {
    if (conversationId) {
      navigate(`/chat?conversation=${conversationId}`)
    } else {
      navigate('/chat')
    }
  }

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">My Requests</h1>
        <EmptyState
          icon={<Code className="h-12 w-12 text-muted-foreground" />}
          title="Error loading requests"
          description={error instanceof Error ? error.message : 'Failed to load requests'}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">My Requests</h1>
        <p className="text-muted-foreground">
          View and manage your code generation requests
        </p>
      </div>

      <div className="flex gap-2 border-b">
        <button
          onClick={() => setFilter('all')}
          className={cn(
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors capitalize',
            filter === 'all'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          )}
        >
          All
        </button>
        <button
          onClick={() => setFilter('pending')}
          className={cn(
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors capitalize',
            filter === 'pending'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          )}
        >
          Pending ({pendingCount})
        </button>
        <button
          onClick={() => setFilter('approved')}
          className={cn(
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors capitalize',
            filter === 'approved'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          )}
        >
          Approved ({approvedCount})
        </button>
        <button
          onClick={() => setFilter('rejected')}
          className={cn(
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors capitalize',
            filter === 'rejected'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          )}
        >
          Rejected ({rejectedCount})
        </button>
      </div>

      {filteredRequests.length === 0 ? (
        <EmptyState
          icon={<Code className="h-12 w-12 text-muted-foreground" />}
          title="No requests"
          description={
            filter === 'all'
              ? 'You have not generated any code yet'
              : `You have no ${filter} requests`
          }
        />
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredRequests.map((request) => {
            if (!request) return null
            return (
              <RequestCard
                key={request.id}
                request={request}
                onCopyCode={handleCopyCode}
                onDownloadCode={handleDownloadCode}
                onViewConversation={handleViewConversation}
              />
            )
          })}
        </div>
      )}
    </div>
  )
}

interface RequestCardProps {
  request: GeneratedCode
  onCopyCode: (code: string) => void
  onDownloadCode: (code: string, brandName?: string) => void
  onViewConversation: (conversationId?: string | null) => void
}

function RequestCard({ request, onCopyCode, onDownloadCode, onViewConversation }: RequestCardProps) {
  const navigate = useNavigate()
  const { toast } = useToast()

  if (!request) return null

  // Use brand_name from API, fallback to brand_id if not available
  // Handle empty string, null, and undefined cases
  const brandDisplayName = (() => {
    // Debug: Log the request object to see what we're receiving
    if (process.env.NODE_ENV === 'development') {
      console.log('RequestCard - request.brand_name:', request.brand_name, 'request.brand_id:', request.brand_id)
    }
    
    // Explicitly check for brand_name in multiple ways
    if (request.brand_name && typeof request.brand_name === 'string' && request.brand_name.trim()) {
      return request.brand_name.trim()
    }
    // Fallback to brand_id if brand_name is missing
    if (request.brand_id) {
      return `Brand ${request.brand_id}`
    }
    return 'Unknown Brand'
  })()

  return (
    <div className="rounded-lg border bg-card p-4 space-y-3">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <h3 className="font-semibold text-sm">{brandDisplayName}</h3>
          <p className="text-xs text-muted-foreground mt-1">
            {request.conversation_preview || 'No description'}
          </p>
        </div>
        <StatusBadge status={request.status} />
      </div>

      <div className="flex items-center gap-4 text-xs text-muted-foreground">
        {request.confidence_score && (
          <span>Confidence: {Math.round(request.confidence_score * 100)}%</span>
        )}
        <span>{formatDistanceToNow(new Date(request.created_at), { addSuffix: true })}</span>
      </div>

      {request.reviewed_at && (
        <div className="text-xs text-muted-foreground">
          Reviewed: {formatDistanceToNow(new Date(request.reviewed_at), { addSuffix: true })}
        </div>
      )}

      {request.reviewer_notes && (
        <div className="rounded bg-muted p-2">
          <p className="text-xs font-medium">Reviewer Notes:</p>
          <p className="text-xs text-muted-foreground mt-1">{request.reviewer_notes}</p>
        </div>
      )}

      {request.rejection_reason && (
        <div className="rounded bg-red-50 dark:bg-red-950 p-2">
          <p className="text-xs font-medium text-red-900 dark:text-red-100">Rejection Reason:</p>
          <p className="text-xs text-red-800 dark:text-red-200 mt-1">{request.rejection_reason}</p>
        </div>
      )}

      <div className="flex gap-2 flex-wrap">
        {request.status === 'approved' && (
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onCopyCode(request.generated_code)}
              className="flex-1"
            >
              <Copy className="h-3 w-3 mr-1" />
              Copy
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onDownloadCode(request.generated_code, request.brand_name)}
              className="flex-1"
            >
              <Download className="h-3 w-3 mr-1" />
              Download
            </Button>
          </>
        )}
        {(request.status === 'generated' || request.status === 'reviewed') && (
          <Button
            variant="outline"
            size="sm"
            onClick={() => onViewConversation(request.conversation_id)}
            className="flex-1"
          >
            <Eye className="h-3 w-3 mr-1" />
            View Conversation
          </Button>
        )}
        {request.status === 'rejected' && (
          <>
            <Button
              variant="outline"
              size="sm"
              onClick={() => onViewConversation(request.conversation_id)}
              className="flex-1"
            >
              <MessageSquare className="h-3 w-3 mr-1" />
              View Conversation
            </Button>
            <Button
              variant="default"
              size="sm"
              onClick={() => {
                navigate('/chat')
                toast({
                  title: 'Start new request',
                  description: 'Create a new code request in the chat',
                })
              }}
              className="flex-1"
            >
              Request New Code
            </Button>
          </>
        )}
      </div>
    </div>
  )
}

