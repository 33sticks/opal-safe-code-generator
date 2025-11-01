import { useState } from 'react'
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
      }
    : null

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

        <div className="flex-1 overflow-y-auto space-y-6 min-h-0">
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
                    onChange={() => setReviewDecision('approved')}
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
                    onChange={() => setReviewDecision('rejected')}
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

