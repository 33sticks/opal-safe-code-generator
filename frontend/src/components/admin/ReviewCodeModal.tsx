import { useState, useRef, useLayoutEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { MessageList } from '@/components/chat/MessageList'
import { CodeBlock } from '@/components/chat/CodeBlock'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { useCodeConversation, useReviewGeneratedCode } from '@/hooks/useApi'
import { useToast } from '@/hooks/use-toast'
import type { GeneratedCode } from '@/types'
import type { Message } from '@/types/chat'
import { AlertTriangle } from 'lucide-react'

interface ReviewCodeModalProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  code: GeneratedCode | null
}

export function ReviewCodeModal({
  open,
  onOpenChange,
  code,
}: ReviewCodeModalProps) {
  const [reviewDecision, setReviewDecision] = useState<'approved' | 'rejected' | null>(null)
  const [notes, setNotes] = useState('')
  const scrollContainerRef = useRef<HTMLDivElement>(null)
  const scrollPositionRef = useRef<number>(0)
  const { toast } = useToast()
  const reviewMutation = useReviewGeneratedCode()
  const { data: conversation, isLoading: isLoadingConversation } = useCodeConversation(
    code?.id || null
  )

  // Convert conversation messages to Message format for MessageList
  const messages: Message[] = conversation?.messages.map((msg, index) => ({
    id: index,
    role: msg.role,
    content: msg.content,
    created_at: msg.created_at || new Date().toISOString(),
    generated_code_id: code?.id || null,
  })) || []

  // Prepare GeneratedCode for CodeBlock (from chat types)
  const codeForBlock = code
    ? {
        id: code.id,
        brand_id: code.brand_id,
        generated_code: code.generated_code,
        confidence_score: code.confidence_score,
        validation_status: code.validation_status as any,
        deployment_status: code.deployment_status as any,
        created_at: code.created_at,
        request_data: code.request_data,
        user_feedback: code.user_feedback,
        error_logs: code.error_logs,
        confidence_breakdown: code.confidence_breakdown ?? null,
      }
    : null

  // Restore scroll position after reviewDecision state updates
  // Use multiple restoration attempts to override browser's default scroll behavior
  useLayoutEffect(() => {
    if (scrollContainerRef.current && scrollPositionRef.current !== 0) {
      const savedPosition = scrollPositionRef.current
      
      // Immediate restoration
      scrollContainerRef.current.scrollTop = savedPosition
      
      // Restore again after browser's render cycle (prevents browser override)
      requestAnimationFrame(() => {
        if (scrollContainerRef.current) {
          scrollContainerRef.current.scrollTop = savedPosition
        }
      })
      
      // Final restoration after a microtask delay (catches late browser scroll)
      setTimeout(() => {
        if (scrollContainerRef.current) {
          scrollContainerRef.current.scrollTop = savedPosition
        }
      }, 0)
      
      // Reset after restoring to avoid interfering with normal scrolling
      scrollPositionRef.current = 0
    }
  }, [reviewDecision])

  // Reset scroll position ref when modal opens/closes
  useLayoutEffect(() => {
    if (!open) {
      scrollPositionRef.current = 0
    }
  }, [open])

  // Handle review decision change while preserving scroll position
  const handleDecisionChange = (decision: 'approved' | 'rejected') => {
    // Store current scroll position before state update
    if (scrollContainerRef.current) {
      scrollPositionRef.current = scrollContainerRef.current.scrollTop
    }
    
    setReviewDecision(decision)
  }

  // Prevent focus-based scrolling
  const handleRadioFocus = (_e: React.FocusEvent<HTMLInputElement>) => {
    const savedPosition = scrollPositionRef.current
    
    // Immediately restore scroll position to prevent browser scroll
    if (scrollContainerRef.current && savedPosition !== 0) {
      scrollContainerRef.current.scrollTop = savedPosition
    }
    
    // Also restore after a microtask to catch any browser-initiated scroll
    requestAnimationFrame(() => {
      if (scrollContainerRef.current && savedPosition !== 0) {
        scrollContainerRef.current.scrollTop = savedPosition
      }
    })
  }

  // Handle click to capture scroll position immediately
  const handleRadioClick = (_e: React.MouseEvent<HTMLInputElement>) => {
    // Capture scroll position on click (before onChange fires)
    if (scrollContainerRef.current) {
      scrollPositionRef.current = scrollContainerRef.current.scrollTop
    }
  }

  const handleSubmit = async () => {
    if (!code || !reviewDecision) {
      toast({
        title: 'Error',
        description: 'Please select a review decision',
        variant: 'destructive',
      })
      return
    }

    try {
      await reviewMutation.mutateAsync({
        id: code.id,
        status: reviewDecision,
        notes: notes || undefined,
      })
      toast({
        title: 'Success',
        description: `Code ${reviewDecision === 'approved' ? 'approved' : 'rejected'} successfully`,
      })
      onOpenChange(false)
      // Reset form
      setReviewDecision(null)
      setNotes('')
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to submit review',
        variant: 'destructive',
      })
    }
  }

  const handleClose = () => {
    onOpenChange(false)
    // Reset form on close
    setReviewDecision(null)
    setNotes('')
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-5xl max-h-[90vh] flex flex-col">
        <DialogHeader>
          <DialogTitle>Review Code</DialogTitle>
          <DialogDescription>
            Review the conversation and generated code before approving or rejecting.
          </DialogDescription>
        </DialogHeader>

        <div ref={scrollContainerRef} className="flex-1 overflow-y-auto space-y-6 min-h-0">
          {/* Warning Banner for User-Provided Selectors */}
          {code?.requires_review && code?.selector_source === 'user_provided' && (
            <div className="mb-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="flex items-start gap-3">
                <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-yellow-900">User-Provided Selector - Requires Validation</h4>
                  <p className="text-sm text-yellow-800 mt-1">
                    This code uses a selector provided directly by the user:
                    <code className="mx-1 px-2 py-0.5 bg-yellow-100 rounded font-mono text-xs">
                      {code.selector_metadata?.selector_used || 'Unknown selector'}
                    </code>
                  </p>
                  <p className="text-sm text-yellow-800 mt-2">
                    ⚠️ Please verify this selector is correct before approving this code.
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Conversation History */}
          <div>
            <h3 className="font-semibold mb-2">Conversation History:</h3>
            <div className="border rounded-lg overflow-hidden h-[200px]">
              {isLoadingConversation ? (
                <div className="flex items-center justify-center h-full">
                  <LoadingSpinner />
                </div>
              ) : conversation ? (
                <MessageList messages={messages} generatedCodeMap={new Map()} />
              ) : (
                <div className="flex items-center justify-center h-full text-muted-foreground">
                  <p>No conversation available (legacy code)</p>
                </div>
              )}
            </div>
          </div>

          {/* Generated Code */}
          {code && (
            <div>
              <h3 className="font-semibold mb-2">Generated Code:</h3>
              {codeForBlock && (
                <div>
                  <CodeBlock code={codeForBlock} />
                </div>
              )}
            </div>
          )}

          {/* Review Form */}
          <div className="space-y-4 border-t pt-4">
            <div>
              <Label className="text-base font-semibold mb-3 block">
                Review Decision:
              </Label>
              <div className="space-y-2">
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="reviewDecision"
                    value="approved"
                    checked={reviewDecision === 'approved'}
                    onChange={() => handleDecisionChange('approved')}
                    onClick={handleRadioClick}
                    onFocus={handleRadioFocus}
                    className="w-4 h-4"
                  />
                  <span>Approve</span>
                </label>
                <label className="flex items-center space-x-2 cursor-pointer">
                  <input
                    type="radio"
                    name="reviewDecision"
                    value="rejected"
                    checked={reviewDecision === 'rejected'}
                    onChange={() => handleDecisionChange('rejected')}
                    onClick={handleRadioClick}
                    onFocus={handleRadioFocus}
                    className="w-4 h-4"
                  />
                  <span>Reject</span>
                </label>
              </div>
            </div>

            <div>
              <Label htmlFor="reviewerNotes">Notes (optional):</Label>
              <Textarea
                id="reviewerNotes"
                placeholder="Add any notes about this review..."
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
                rows={4}
                className="mt-1"
              />
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="flex justify-end space-x-2 border-t pt-4">
          <Button variant="outline" onClick={handleClose} disabled={reviewMutation.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!reviewDecision || reviewMutation.isPending}
          >
            {reviewMutation.isPending ? 'Submitting...' : 'Submit Review'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

