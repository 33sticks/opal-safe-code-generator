import { useState } from 'react'
import { useSelectors, useDeleteSelector } from '@/hooks/useApi'
import { Button } from '@/components/ui/button'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Edit, Trash2 } from 'lucide-react'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { ConfirmDialog } from '@/components/ui/ConfirmDialog'
import { useToast } from '@/hooks/use-toast'
import { DOMSelector } from '@/types'
import { format } from 'date-fns'

interface SelectorsTableProps {
  onEdit: (id: number) => void
}

export function SelectorsTable({ onEdit }: SelectorsTableProps) {
  const { data: selectors, isLoading, error } = useSelectors()
  const deleteSelector = useDeleteSelector()
  const { toast } = useToast()
  const [deleteId, setDeleteId] = useState<number | null>(null)

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await deleteSelector.mutateAsync(deleteId)
      toast({
        title: 'Success',
        description: 'Selector deleted successfully',
      })
      setDeleteId(null)
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to delete selector',
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
        Error loading selectors: {error.message}
      </div>
    )
  }

  if (!selectors || selectors.length === 0) {
    return <EmptyState title="No selectors found" description="Create your first selector to get started." />
  }

  return (
    <>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Brand ID</TableHead>
              <TableHead>Page Type</TableHead>
              <TableHead>Selector</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {selectors.map((selector: DOMSelector) => (
              <TableRow key={selector.id}>
                <TableCell>{selector.id}</TableCell>
                <TableCell>{selector.brand_id}</TableCell>
                <TableCell className="font-medium">{selector.page_type}</TableCell>
                <TableCell className="max-w-xs truncate font-mono text-xs">
                  {selector.selector}
                </TableCell>
                <TableCell>
                  <span className="rounded-full px-2 py-1 text-xs bg-muted">
                    {selector.status}
                  </span>
                </TableCell>
                <TableCell>
                  {format(new Date(selector.created_at), 'MMM d, yyyy')}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onEdit(selector.id)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteId(selector.id)}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <ConfirmDialog
        open={deleteId !== null}
        onOpenChange={(open) => !open && setDeleteId(null)}
        onConfirm={handleDelete}
        title="Delete Selector"
        description={`Are you sure you want to delete this selector? This action cannot be undone.`}
      />
    </>
  )
}

