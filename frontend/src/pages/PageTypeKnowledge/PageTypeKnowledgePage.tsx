import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import { PageTypeKnowledgeTable } from './PageTypeKnowledgeTable'
import { PageTypeKnowledgeForm } from './PageTypeKnowledgeForm'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function PageTypeKnowledgePage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingKnowledge, setEditingKnowledge] = useState<number | null>(null)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Page Type Knowledge</h1>
          <p className="text-muted-foreground">
            Manage page type knowledge for code generation
          </p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Add Page Knowledge
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Page Knowledge Base</CardTitle>
        </CardHeader>
        <CardContent>
          <PageTypeKnowledgeTable
            onEdit={(id) => setEditingKnowledge(id)}
          />
        </CardContent>
      </Card>

      <PageTypeKnowledgeForm
        open={isCreateDialogOpen || editingKnowledge !== null}
        onOpenChange={(open) => {
          if (!open) {
            setIsCreateDialogOpen(false)
            setEditingKnowledge(null)
          }
        }}
        knowledgeId={editingKnowledge || undefined}
      />
    </div>
  )
}

