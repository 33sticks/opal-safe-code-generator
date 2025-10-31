import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import { BrandTable } from './BrandTable'
import { BrandForm } from './BrandForm'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function BrandsPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingBrand, setEditingBrand] = useState<number | null>(null)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Brands</h1>
          <p className="text-muted-foreground">
            Manage your brands and their configurations
          </p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create Brand
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Brands</CardTitle>
        </CardHeader>
        <CardContent>
          <BrandTable
            onEdit={(id) => setEditingBrand(id)}
          />
        </CardContent>
      </Card>

      <BrandForm
        open={isCreateDialogOpen || editingBrand !== null}
        onOpenChange={(open) => {
          if (!open) {
            setIsCreateDialogOpen(false)
            setEditingBrand(null)
          }
        }}
        brandId={editingBrand || undefined}
      />
    </div>
  )
}

