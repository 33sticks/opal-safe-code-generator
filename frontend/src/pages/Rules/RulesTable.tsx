import { useState } from 'react'
import { useRules, useDeleteRule } from '@/hooks/useApi'
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
import { CodeRule } from '@/types'
import { format } from 'date-fns'

interface RulesTableProps {
  onEdit: (id: number) => void
}

export function RulesTable({ onEdit }: RulesTableProps) {
  const { data: rules, isLoading, error } = useRules()
  const deleteRule = useDeleteRule()
  const { toast } = useToast()
  const [deleteId, setDeleteId] = useState<number | null>(null)

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await deleteRule.mutateAsync(deleteId)
      toast({
        title: 'Success',
        description: 'Rule deleted successfully',
      })
      setDeleteId(null)
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to delete rule',
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
        Error loading rules: {error.message}
      </div>
    )
  }

  if (!rules || rules.length === 0) {
    return <EmptyState title="No rules found" description="Create your first rule to get started." />
  }

  return (
    <>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Brand</TableHead>
              <TableHead>Rule Type</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rules.map((rule: CodeRule) => (
              <TableRow key={rule.id}>
                <TableCell>{rule.id}</TableCell>
                <TableCell>{rule.brand_name || `Brand ${rule.brand_id}`}</TableCell>
                <TableCell className="font-medium">{rule.rule_type}</TableCell>
                <TableCell>{rule.priority}</TableCell>
                <TableCell>
                  {format(new Date(rule.created_at), 'MMM d, yyyy')}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onEdit(rule.id)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteId(rule.id)}
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
        title="Delete Rule"
        description={`Are you sure you want to delete this rule? This action cannot be undone.`}
      />
    </>
  )
}

