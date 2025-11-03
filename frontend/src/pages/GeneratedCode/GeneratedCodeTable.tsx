import { useState, useMemo } from 'react'
import { useGeneratedCodes, useBrands, useDeleteGeneratedCode } from '@/hooks/useApi'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { StatusBadge } from '@/components/admin/StatusBadge'
import { ViewConversationModal } from '@/components/admin/ViewConversationModal'
import { ReviewCodeModal } from '@/components/admin/ReviewCodeModal'
import { useCodeConversation } from '@/hooks/useApi'
import { GeneratedCode, CodeStatus } from '@/types'
import { formatDistanceToNow } from 'date-fns'
import { MessageSquare, Eye, CheckCircle, XCircle, Trash2, AlertTriangle } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'

export function GeneratedCodeTable() {
  const [statusFilter, setStatusFilter] = useState<CodeStatus | 'all'>('all')
  const [brandFilter, setBrandFilter] = useState<number | 'all'>('all')
  const [searchQuery, setSearchQuery] = useState('')
  const [viewingConversationId, setViewingConversationId] = useState<number | null>(null)
  const [reviewingCodeId, setReviewingCodeId] = useState<number | null>(null)
  const [deletingCodeId, setDeletingCodeId] = useState<number | null>(null)

  const { toast } = useToast()
  const deleteMutation = useDeleteGeneratedCode()

  // Fetch data with filters
  const filters = useMemo(() => {
    const params: { status?: CodeStatus; brand_id?: number } = {}
    if (statusFilter !== 'all') {
      params.status = statusFilter
    }
    if (brandFilter !== 'all') {
      params.brand_id = brandFilter
    }
    return params
  }, [statusFilter, brandFilter])

  const { data: codes, isLoading, error } = useGeneratedCodes(filters)
  const { data: brands } = useBrands()
  const { data: conversation, isLoading: isLoadingConversation } = useCodeConversation(
    viewingConversationId
  )

  // Filter codes by search query (search in conversation preview)
  const filteredCodes = useMemo(() => {
    if (!codes) return []
    if (!searchQuery) return codes
    const query = searchQuery.toLowerCase()
    return codes.filter(
      (code) =>
        code.conversation_preview?.toLowerCase().includes(query) ||
        code.brand_name?.toLowerCase().includes(query) ||
        code.user_email?.toLowerCase().includes(query)
    )
  }, [codes, searchQuery])

  const handleDelete = async () => {
    if (!deletingCodeId) return
    try {
      await deleteMutation.mutateAsync(deletingCodeId)
      toast({
        title: 'Success',
        description: 'Code deleted successfully',
      })
      setDeletingCodeId(null)
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to delete code',
        variant: 'destructive',
      })
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="py-8 text-center text-destructive">
        Error loading generated code: {error instanceof Error ? error.message : 'Unknown error'}
      </div>
    )
  }

  if (!filteredCodes || filteredCodes.length === 0) {
    return (
      <>
        <div className="flex gap-4 mb-6">
          <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as CodeStatus | 'all')}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="generated">Generated</SelectItem>
              <SelectItem value="reviewed">Reviewed</SelectItem>
              <SelectItem value="approved">Approved</SelectItem>
              <SelectItem value="rejected">Rejected</SelectItem>
              <SelectItem value="deployed">Deployed</SelectItem>
            </SelectContent>
          </Select>

          <Select value={brandFilter === 'all' ? 'all' : String(brandFilter)} onValueChange={(value) => setBrandFilter(value === 'all' ? 'all' : Number(value))}>
            <SelectTrigger className="w-[180px]">
              <SelectValue placeholder="Brand" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Brands</SelectItem>
              {brands?.map((brand) => (
                <SelectItem key={brand.id} value={String(brand.id)}>
                  {brand.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Input
            placeholder="Search conversation preview..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-sm"
          />
        </div>
        <EmptyState
          title="No generated code found"
          description="Generated code will appear here once created."
        />
      </>
    )
  }

  const codeToView = viewingConversationId ? filteredCodes.find((c) => c.id === viewingConversationId) : null
  const codeToReview = reviewingCodeId ? filteredCodes.find((c) => c.id === reviewingCodeId) : null

  return (
    <>
      {/* Filters */}
      <div className="flex gap-4 mb-6">
        <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as CodeStatus | 'all')}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="generated">Generated</SelectItem>
            <SelectItem value="reviewed">Reviewed</SelectItem>
            <SelectItem value="approved">Approved</SelectItem>
            <SelectItem value="rejected">Rejected</SelectItem>
            <SelectItem value="deployed">Deployed</SelectItem>
          </SelectContent>
        </Select>

        <Select value={brandFilter === 'all' ? 'all' : String(brandFilter)} onValueChange={(value) => setBrandFilter(value === 'all' ? 'all' : Number(value))}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Brand" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Brands</SelectItem>
            {brands?.map((brand) => (
              <SelectItem key={brand.id} value={String(brand.id)}>
                {brand.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Input
          placeholder="Search conversation preview..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="max-w-sm"
        />
      </div>

      {/* Cards */}
      <div className="space-y-4">
        {filteredCodes.map((code: GeneratedCode) => (
          <Card key={code.id}>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <CardTitle className="text-lg">
                    {code.brand_name || `Brand ${code.brand_id}`} - Generated Code #{code.id}
                  </CardTitle>
                  <div className="flex items-center gap-3 mt-2">
                    <StatusBadge status={code.status} />
                    {code.requires_review && (
                      <span className="inline-flex items-center rounded-full border border-yellow-200 bg-yellow-50 text-yellow-800 px-2.5 py-0.5 text-xs font-semibold">
                        <AlertTriangle className="h-3 w-3 mr-1" />
                        Review Required
                      </span>
                    )}
                    {code.confidence_score !== null && code.confidence_score !== undefined && (
                      <span className="text-sm text-muted-foreground">
                        Confidence: {Math.round(code.confidence_score * 100)}%
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {code.conversation_preview && (
                <p className="text-sm text-muted-foreground mb-4 italic">
                  &quot;{code.conversation_preview}&quot;
                </p>
              )}
              <div className="flex items-center justify-between text-sm text-muted-foreground mb-4">
                <div>
                  <span className="font-medium">Generated by:</span> {code.user_email || 'Unknown'} |{' '}
                  {formatDistanceToNow(new Date(code.created_at), { addSuffix: true })}
                </div>
                {code.reviewer_email && (
                  <div>
                    <span className="font-medium">Reviewed by:</span> {code.reviewer_email}
                    {code.reviewed_at && (
                      <> | {formatDistanceToNow(new Date(code.reviewed_at), { addSuffix: true })}</>
                    )}
                  </div>
                )}
              </div>
              {code.status === 'approved' && code.reviewer_notes && (
                <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded-md">
                  <div className="flex items-start gap-2">
                    <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-green-900">Approved</p>
                      <p className="text-sm text-green-700">{code.reviewer_notes}</p>
                    </div>
                  </div>
                </div>
              )}
              {code.status === 'rejected' && code.rejection_reason && (
                <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
                  <div className="flex items-start gap-2">
                    <XCircle className="h-5 w-5 text-red-600 mt-0.5" />
                    <div>
                      <p className="text-sm font-medium text-red-900">Rejected</p>
                      <p className="text-sm text-red-700">{code.rejection_reason}</p>
                    </div>
                  </div>
                </div>
              )}
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setViewingConversationId(code.id)}
                  disabled={!code.conversation_id}
                >
                  <MessageSquare className="h-4 w-4 mr-2" />
                  View Conversation
                </Button>
                {code.status === 'generated' && (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setReviewingCodeId(code.id)}
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    Review
                  </Button>
                )}
                <AlertDialog open={deletingCodeId === code.id} onOpenChange={(open) => !open && setDeletingCodeId(null)}>
                  <AlertDialogTrigger asChild>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setDeletingCodeId(code.id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete
                    </Button>
                  </AlertDialogTrigger>
                  <AlertDialogContent>
                    <AlertDialogHeader>
                      <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                      <AlertDialogDescription>
                        This will permanently delete this generated code. This action cannot be undone.
                      </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                      <AlertDialogCancel onClick={() => setDeletingCodeId(null)}>
                        Cancel
                      </AlertDialogCancel>
                      <AlertDialogAction
                        onClick={handleDelete}
                        className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
                        disabled={deleteMutation.isPending}
                      >
                        {deleteMutation.isPending ? 'Deleting...' : 'Delete'}
                      </AlertDialogAction>
                    </AlertDialogFooter>
                  </AlertDialogContent>
                </AlertDialog>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Modals */}
      {codeToView && (
        <ViewConversationModal
          open={viewingConversationId !== null}
          onOpenChange={(open) => !open && setViewingConversationId(null)}
          conversation={conversation ?? null}
          isLoading={isLoadingConversation}
        />
      )}

      {codeToReview && (
        <ReviewCodeModal
          open={reviewingCodeId !== null}
          onOpenChange={(open) => !open && setReviewingCodeId(null)}
          code={codeToReview}
        />
      )}
    </>
  )
}
