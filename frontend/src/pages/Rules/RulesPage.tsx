import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import { RulesTable } from './RulesTable'
import { RulesForm } from './RulesForm'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function RulesPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingRule, setEditingRule] = useState<number | null>(null)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Code Rules</h1>
          <p className="text-muted-foreground">
            Manage validation rules for generated code
          </p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create Rule
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Rules</CardTitle>
        </CardHeader>
        <CardContent>
          <RulesTable
            onEdit={(id) => setEditingRule(id)}
          />
        </CardContent>
      </Card>

      <RulesForm
        open={isCreateDialogOpen || editingRule !== null}
        onOpenChange={(open) => {
          if (!open) {
            setIsCreateDialogOpen(false)
            setEditingRule(null)
          }
        }}
        ruleId={editingRule || undefined}
      />
    </div>
  )
}

