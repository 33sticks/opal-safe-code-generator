import { useState } from 'react'
import { useTemplates, useDeleteTemplate } from '@/hooks/useApi'
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
import { Template } from '@/types'
import { format } from 'date-fns'

interface TemplatesTableProps {
  onEdit: (id: number) => void
}

export function TemplatesTable({ onEdit }: TemplatesTableProps) {
  const { data: templates, isLoading, error } = useTemplates()
  const deleteTemplate = useDeleteTemplate()
  const { toast } = useToast()
  const [deleteId, setDeleteId] = useState<number | null>(null)

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await deleteTemplate.mutateAsync(deleteId)
      toast({
        title: 'Success',
        description: 'Template deleted successfully',
      })
      setDeleteId(null)
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to delete template',
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
        Error loading templates: {error.message}
      </div>
    )
  }

  if (!templates || templates.length === 0) {
    return <EmptyState title="No templates found" description="Create your first template to get started." />
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
            {templates.map((template: Template) => (
              <TableRow key={template.id}>
                <TableCell>{template.id}</TableCell>
                <TableCell>{template.brand_name || `Brand ${template.brand_id}`}</TableCell>
                <TableCell className="font-medium">{template.test_type}</TableCell>
                <TableCell>{template.version}</TableCell>
                <TableCell>
                  {template.is_active ? (
                    <span className="text-green-600">Yes</span>
                  ) : (
                    <span className="text-muted-foreground">No</span>
                  )}
                </TableCell>
                <TableCell>
                  {format(new Date(template.created_at), 'MMM d, yyyy')}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onEdit(template.id)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteId(template.id)}
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
        title="Delete Template"
        description={`Are you sure you want to delete this template? This action cannot be undone.`}
      />
    </>
  )
}

