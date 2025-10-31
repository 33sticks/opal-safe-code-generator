import { GeneratedCodeTable } from './GeneratedCodeTable'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

export function GeneratedCodePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Generated Code</h1>
        <p className="text-muted-foreground">
          View all generated code entries (read-only)
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>All Generated Code</CardTitle>
        </CardHeader>
        <CardContent>
          <GeneratedCodeTable />
        </CardContent>
      </Card>
    </div>
  )
}

