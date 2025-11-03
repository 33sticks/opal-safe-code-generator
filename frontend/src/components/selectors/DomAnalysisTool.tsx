import { useState } from 'react'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Label } from '@/components/ui/label'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { AnalysisResults } from './AnalysisResults'
import { useAnalyzeDom, useCreateSelectorsBulk } from '@/hooks/useApi'
import { DomAnalysisResult, PageType, DOMSelectorCreate, SelectorStatus } from '@/types'
import { useToast } from '@/hooks/use-toast'

interface DomAnalysisToolProps {
  brandId?: number
}

export function DomAnalysisTool({ brandId }: DomAnalysisToolProps) {
  const [html, setHtml] = useState('')
  const [pageType, setPageType] = useState<PageType>(PageType.PDP)
  const [results, setResults] = useState<DomAnalysisResult | null>(null)
  const [selectedSelectors, setSelectedSelectors] = useState<Set<number>>(new Set())
  const { toast } = useToast()

  const analyzeMutation = useAnalyzeDom()
  const createBulkMutation = useCreateSelectorsBulk()

  const handleAnalyze = async () => {
    if (!html.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Please paste HTML content before analyzing',
        variant: 'destructive',
      })
      return
    }

    try {
      const result = await analyzeMutation.mutateAsync({
        html: html.trim(),
        page_type: pageType,
        brand_id: brandId,
      })
      setResults(result)
      setSelectedSelectors(new Set()) // Reset selections on new analysis
    } catch (error) {
      toast({
        title: 'Analysis Failed',
        description: error instanceof Error ? error.message : 'Failed to analyze HTML',
        variant: 'destructive',
      })
    }
  }

  const handleToggleSelector = (index: number) => {
    const newSelected = new Set(selectedSelectors)
    if (newSelected.has(index)) {
      newSelected.delete(index)
    } else {
      newSelected.add(index)
    }
    setSelectedSelectors(newSelected)
  }

  const handleAddSelectors = async () => {
    if (selectedSelectors.size === 0) {
      toast({
        title: 'No Selectors Selected',
        description: 'Please select at least one selector to add to the database.',
        variant: 'destructive',
      })
      return
    }

    if (!brandId) {
      toast({
        title: 'Brand ID Required',
        description: 'Brand ID is required to create selectors.',
        variant: 'destructive',
      })
      return
    }

    if (!results) {
      toast({
        title: 'No Results',
        description: 'Please analyze HTML first before adding selectors.',
        variant: 'destructive',
      })
      return
    }

    try {
      // Build selector objects from selected indices
      const selectorsToAdd: DOMSelectorCreate[] = Array.from(selectedSelectors).map(index => ({
        brand_id: brandId,
        selector: results.selectors[index].selector,
        page_type: pageType,
        description: results.selectors[index].description,
        status: SelectorStatus.ACTIVE,
        relationships: {
          parent: results.selectors[index].parent || null,
          children: results.selectors[index].children || [],
          siblings: results.selectors[index].siblings || [],
          stability_score: results.selectors[index].stability_score,
          element_type: results.selectors[index].element_type,
        },
      }))

      const response = await createBulkMutation.mutateAsync(selectorsToAdd)

      // Show success toast with detailed feedback
      const message = response.skipped > 0
        ? `Added ${response.created} selector${response.created !== 1 ? 's' : ''} to database (${response.skipped} duplicate${response.skipped !== 1 ? 's' : ''} skipped)`
        : `Added ${response.created} selector${response.created !== 1 ? 's' : ''} to database`

      toast({
        title: 'Success',
        description: message,
      })

      // Clear form after successful addition
      setSelectedSelectors(new Set())
      setResults(null)
      setHtml('')
    } catch (error) {
      toast({
        title: 'Failed to Add Selectors',
        description: error instanceof Error ? error.message : 'An error occurred while adding selectors to the database.',
        variant: 'destructive',
      })
    }
  }

  return (
    <div className="space-y-6">
      {/* HTML Input Section */}
      <div className="space-y-4">
        <div>
          <Label htmlFor="html-input" className="text-base font-medium">
            Paste HTML from your browser DevTools:
          </Label>
          <Textarea
            id="html-input"
            value={html}
            onChange={(e) => setHtml(e.target.value)}
            placeholder="<div>Paste your HTML here...</div>"
            className="mt-2 font-mono text-sm min-h-[200px]"
            disabled={analyzeMutation.isPending}
          />
        </div>

        <div className="flex items-center gap-4">
          <div className="flex-1">
            <Label htmlFor="page-type" className="text-base font-medium">
              Page Type:
            </Label>
            <Select
              value={pageType}
              onValueChange={(value) => setPageType(value as PageType)}
              disabled={analyzeMutation.isPending}
            >
              <SelectTrigger id="page-type" className="mt-2">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={PageType.PDP}>PDP (Product Detail Page)</SelectItem>
                <SelectItem value={PageType.CART}>Cart</SelectItem>
                <SelectItem value={PageType.CHECKOUT}>Checkout</SelectItem>
                <SelectItem value={PageType.HOME}>Home</SelectItem>
                <SelectItem value={PageType.CATEGORY}>Category</SelectItem>
                <SelectItem value={PageType.SEARCH}>Search</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-end">
            <Button
              onClick={handleAnalyze}
              disabled={analyzeMutation.isPending || !html.trim()}
              className="min-w-[140px]"
            >
              {analyzeMutation.isPending ? (
                <>
                  <LoadingSpinner size="sm" className="mr-2" />
                  Analyzing...
                </>
              ) : (
                'Analyze HTML'
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {analyzeMutation.isPending && (
        <div className="flex items-center justify-center py-8 space-x-2 text-muted-foreground">
          <LoadingSpinner size="md" />
          <span>Analyzing HTML structure...</span>
        </div>
      )}

      {/* Results Section */}
      {results && !analyzeMutation.isPending && (
        <div className="border-t pt-6">
          <AnalysisResults
            results={results}
            selectedSelectors={selectedSelectors}
            onToggleSelector={handleToggleSelector}
            onAddSelectors={handleAddSelectors}
            isAdding={createBulkMutation.isPending}
          />
        </div>
      )}
    </div>
  )
}

