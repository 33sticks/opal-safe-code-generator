import { useState } from 'react'
import { useBrands, useDeleteBrand } from '@/hooks/useApi'
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
import { Brand } from '@/types'
import { format } from 'date-fns'

interface BrandTableProps {
  onEdit: (id: number) => void
}

export function BrandTable({ onEdit }: BrandTableProps) {
  const { data: brands, isLoading, error } = useBrands()
  const deleteBrand = useDeleteBrand()
  const { toast } = useToast()
  const [deleteId, setDeleteId] = useState<number | null>(null)

  const handleDelete = async () => {
    if (!deleteId) return
    try {
      await deleteBrand.mutateAsync(deleteId)
      toast({
        title: 'Success',
        description: 'Brand deleted successfully',
      })
      setDeleteId(null)
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Failed to delete brand',
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
        Error loading brands: {error.message}
      </div>
    )
  }

  if (!brands || brands.length === 0) {
    return <EmptyState title="No brands found" description="Create your first brand to get started." />
  }

  return (
    <>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Domain</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {brands.map((brand: Brand) => (
              <TableRow key={brand.id}>
                <TableCell>{brand.id}</TableCell>
                <TableCell className="font-medium">{brand.name}</TableCell>
                <TableCell>{brand.domain}</TableCell>
                <TableCell>
                  <span className="rounded-full px-2 py-1 text-xs bg-muted">
                    {brand.status}
                  </span>
                </TableCell>
                <TableCell>
                  {format(new Date(brand.created_at), 'MMM d, yyyy')}
                </TableCell>
                <TableCell className="text-right">
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => onEdit(brand.id)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => setDeleteId(brand.id)}
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
        title="Delete Brand"
        description={`Are you sure you want to delete this brand? This action cannot be undone.`}
      />
    </>
  )
}

