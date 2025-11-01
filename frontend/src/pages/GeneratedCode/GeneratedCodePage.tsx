import { GeneratedCodeTable } from './GeneratedCodeTable'

export function GeneratedCodePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Generated Code Review</h1>
        <p className="text-muted-foreground">
          Review and manage all generated code entries with conversation context
        </p>
      </div>

      <GeneratedCodeTable />
    </div>
  )
}

