import { useState } from 'react'
import { usePageTypeKnowledge, useDeletePageTypeKnowledge } from '@/hooks/useApi'
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
import { PageTypeKnowledge } from '@/types'
import { format } from 'date-fns'

interface PageTypeKnowledgeTableProps {
  onEdit: (id: number) => void
}

export function PageTypeKnowledgeTable({ onEdit }: PageTypeKnowledgeTableProps) {
  const { data: knowledge, isLoading, error } = usePageTypeKnowledge()
  const deleteKnowledge = useDeletePageTypeKnowledge()
  const { toast } = useToast()
  const [deleteId, setDeleteId] = useState<number | null>(null)

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await deleteKnowledge.mutateAsync(deleteId)
      toast({
        title: 'Success',
        description: 'Page knowledge deleted successfully',
      })
      setDeleteId(null)
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to delete page knowledge',
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
        Error loading page knowledge: {error.message}
      </div>
    )
  }

  if (!knowledge || knowledge.length === 0) {
    return <EmptyState title="No page knowledge found" description="Add your first page knowledge entry to get started." />
  }

  return (
    <>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Brand</TableHead>
              <TableHead>Test Type</TableHead>
              <TableHead>Version</TableHead>
              <TableHead>Active</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {knowledge.map((item: PageTypeKnowledge) => (
              <TableRow key={item.id}>
                <TableCell>{item.id}</TableCell>
                <TableCell>{item.brand_name || `Brand ${item.brand_id}`}</TableCell>
                <TableCell className="font-medium">{item.test_type}</TableCell>
                <TableCell>{item.version}</TableCell>
                <TableCell>
                  {item.is_active ? (
                    <span className="text-green-600">Yes</span>
                  ) : (
                    <span className="text-muted-foreground">No</span>
                  )}
                </TableCell>
                <TableCell>
                  {format(new Date(item.created_at), 'MMM d, yyyy')}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onEdit(item.id)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteId(item.id)}
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
        title="Delete Page Knowledge"
        description={`Are you sure you want to delete this page knowledge entry? This action cannot be undone.`}
      />
    </>
  )
}

