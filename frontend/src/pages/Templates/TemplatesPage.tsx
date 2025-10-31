import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import { TemplatesTable } from './TemplatesTable'
import { TemplatesForm } from './TemplatesForm'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function TemplatesPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<number | null>(null)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Templates</h1>
          <p className="text-muted-foreground">
            Manage code templates for A/B tests
          </p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create Template
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Templates</CardTitle>
        </CardHeader>
        <CardContent>
          <TemplatesTable
            onEdit={(id) => setEditingTemplate(id)}
          />
        </CardContent>
      </Card>

      <TemplatesForm
        open={isCreateDialogOpen || editingTemplate !== null}
        onOpenChange={(open) => {
          if (!open) {
            setIsCreateDialogOpen(false)
            setEditingTemplate(null)
          }
        }}
        templateId={editingTemplate || undefined}
      />
    </div>
  )
}

