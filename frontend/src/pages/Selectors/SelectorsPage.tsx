import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Plus } from 'lucide-react'
import { SelectorsTable } from './SelectorsTable'
import { SelectorsForm } from './SelectorsForm'
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { DomAnalysisTool } from '@/components/selectors/DomAnalysisTool'
import { useAuth } from '@/contexts/AuthContext'

export function SelectorsPage() {
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [editingSelector, setEditingSelector] = useState<number | null>(null)
  const { user } = useAuth()

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">DOM Selectors</h1>
          <p className="text-muted-foreground">
            Manage DOM selectors for page targeting
          </p>
        </div>
        <Button onClick={() => setIsCreateDialogOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          Create Selector
        </Button>
      </div>

      {/* DOM Analysis Tool */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle>🔍 DOM Structure Discovery (Beta)</CardTitle>
          <CardDescription>
            Paste HTML from your browser to automatically discover selectors
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DomAnalysisTool brandId={user?.brand_id || undefined} />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>All Selectors</CardTitle>
        </CardHeader>
        <CardContent>
          <SelectorsTable
            onEdit={(id) => setEditingSelector(id)}
          />
        </CardContent>
      </Card>

      <SelectorsForm
        open={isCreateDialogOpen || editingSelector !== null}
        onOpenChange={(open) => {
          if (!open) {
            setIsCreateDialogOpen(false)
            setEditingSelector(null)
          }
        }}
        selectorId={editingSelector || undefined}
      />
    </div>
  )
}

