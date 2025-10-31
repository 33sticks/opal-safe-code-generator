import { useState } from 'react'
import { useGeneratedCodes, useGeneratedCode } from '@/hooks/useApi'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Eye, Copy, Check } from 'lucide-react'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { EmptyState } from '@/components/ui/EmptyState'
import { GeneratedCode } from '@/types'
import { format } from 'date-fns'
import { CodeEditor } from '@/components/monaco/CodeEditor'
import { useToast } from '@/hooks/use-toast'

// Utility function to normalize code string - converts escape sequences to actual characters
function normalizeCodeString(code: string): string {
  if (!code) return ''
  
  // Replace literal escape sequences with actual characters
  // This handles cases where code might be stored with escaped newlines
  return code
    .replace(/\\n/g, '\n')      // Convert \n to actual newline
    .replace(/\\t/g, '\t')        // Convert \t to actual tab
    .replace(/\\r/g, '\r')        // Convert \r to actual carriage return
    .replace(/\\"/g, '"')         // Convert \" to actual quote
    .replace(/\\'/g, "'")         // Convert \' to actual single quote
    .replace(/\\\\/g, '\\')       // Convert \\ to single backslash (do this last)
}

export function GeneratedCodeTable() {
  const { data: codes, isLoading, error } = useGeneratedCodes()
  const [viewingCode, setViewingCode] = useState<number | null>(null)
  const { data: code } = useGeneratedCode(viewingCode || 0)
  const [copied, setCopied] = useState(false)
  const { toast } = useToast()

  // Normalize the code string to ensure proper formatting
  const normalizedCode = code?.generated_code ? normalizeCodeString(code.generated_code) : ''

  const handleCopyCode = async () => {
    if (!normalizedCode) return
    
    try {
      // Copy the normalized (clean) JavaScript code
      await navigator.clipboard.writeText(normalizedCode)
      setCopied(true)
      toast({
        title: 'Copied!',
        description: 'Code copied to clipboard',
      })
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      toast({
        title: 'Error',
        description: 'Failed to copy code',
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
        Error loading generated code: {error.message}
      </div>
    )
  }

  if (!codes || codes.length === 0) {
    return <EmptyState title="No generated code found" description="Generated code will appear here once created." />
  }

  return (
    <>
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>ID</TableHead>
              <TableHead>Brand ID</TableHead>
              <TableHead>Confidence Score</TableHead>
              <TableHead>Validation Status</TableHead>
              <TableHead>Deployment Status</TableHead>
              <TableHead>Created</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {codes.map((code: GeneratedCode) => (
              <TableRow key={code.id}>
                <TableCell>{code.id}</TableCell>
                <TableCell>{code.brand_id}</TableCell>
                <TableCell>
                  {code.confidence_score !== null && code.confidence_score !== undefined
                    ? `${(code.confidence_score * 100).toFixed(1)}%`
                    : 'N/A'}
                </TableCell>
                <TableCell>
                  <span className="rounded-full px-2 py-1 text-xs bg-muted">
                    {code.validation_status}
                  </span>
                </TableCell>
                <TableCell>
                  <span className="rounded-full px-2 py-1 text-xs bg-muted">
                    {code.deployment_status}
                  </span>
                </TableCell>
                <TableCell>
                  {format(new Date(code.created_at), 'MMM d, yyyy')}
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => setViewingCode(code.id)}
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      <Dialog open={viewingCode !== null} onOpenChange={(open) => !open && setViewingCode(null)}>
        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Generated Code #{viewingCode}</DialogTitle>
            <DialogDescription>
              View the full generated code content
            </DialogDescription>
          </DialogHeader>
          {code && (
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <span className="font-medium">Brand ID:</span> {code.brand_id}
                </div>
                <div>
                  <span className="font-medium">Confidence:</span>{' '}
                  {code.confidence_score !== null && code.confidence_score !== undefined
                    ? `${(code.confidence_score * 100).toFixed(1)}%`
                    : 'N/A'}
                </div>
                <div>
                  <span className="font-medium">Validation:</span> {code.validation_status}
                </div>
                <div>
                  <span className="font-medium">Deployment:</span> {code.deployment_status}
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium">Generated Code:</h4>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleCopyCode}
                    className="flex items-center gap-2"
                  >
                    {copied ? (
                      <>
                        <Check className="h-4 w-4" />
                        Copied
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4" />
                        Copy Code
                      </>
                    )}
                  </Button>
                </div>
                <CodeEditor
                  value={normalizedCode}
                  onChange={() => {}}
                  language="javascript"
                  height="400px"
                  readOnly={true}
                />
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}

