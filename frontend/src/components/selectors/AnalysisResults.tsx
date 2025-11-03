import { useState } from 'react'
import { Checkbox } from '@/components/ui/checkbox'
import { Button } from '@/components/ui/button'
import { StabilityScore } from './StabilityScore'
import { DomAnalysisResult } from '@/types'
import { ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react'

interface AnalysisResultsProps {
  results: DomAnalysisResult
  selectedSelectors: Set<number>
  onToggleSelector: (index: number) => void
  onAddSelectors: () => void
}

export function AnalysisResults({
  results,
  selectedSelectors,
  onToggleSelector,
  onAddSelectors,
}: AnalysisResultsProps) {
  const [expandedSelectors, setExpandedSelectors] = useState<Set<number>>(new Set())

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedSelectors)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedSelectors(newExpanded)
  }

  return (
    <div className="space-y-6">
      {/* Suggested Selectors */}
      <div>
        <h3 className="text-lg font-semibold mb-4">
          Suggested Selectors ({results.selectors.length} found)
        </h3>
        <div className="space-y-4">
          {results.selectors.map((selector, index) => {
            const isExpanded = expandedSelectors.has(index)
            const hasDetails = selector.parent || selector.children.length > 0 || selector.siblings.length > 0

            return (
              <div
                key={index}
                className="border rounded-lg p-4 space-y-3"
              >
                <div className="flex items-start gap-3">
                  <Checkbox
                    checked={selectedSelectors.has(index)}
                    onCheckedChange={() => onToggleSelector(index)}
                    className="mt-1"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2">
                      <code className="text-sm font-mono bg-muted px-2 py-1 rounded flex-1 break-all">
                        {selector.selector}
                      </code>
                      {hasDetails && (
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-6 w-6"
                          onClick={() => toggleExpanded(index)}
                        >
                          {isExpanded ? (
                            <ChevronUp className="h-4 w-4" />
                          ) : (
                            <ChevronDown className="h-4 w-4" />
                          )}
                        </Button>
                      )}
                    </div>
                    <div className="mt-2">
                      <StabilityScore score={selector.stability_score} />
                    </div>
                    <p className="text-sm text-muted-foreground mt-2">
                      {selector.description}
                    </p>
                    <div className="mt-2">
                      <span className="text-xs px-2 py-1 rounded bg-secondary text-secondary-foreground">
                        {selector.element_type}
                      </span>
                    </div>

                    {/* Collapsible Details */}
                    {isExpanded && hasDetails && (
                      <div className="mt-4 pt-4 border-t space-y-3">
                        {selector.parent && (
                          <div>
                            <p className="text-xs font-semibold text-muted-foreground mb-1">
                              Parent:
                            </p>
                            <code className="text-xs font-mono bg-muted px-2 py-1 rounded block break-all">
                              {selector.parent}
                            </code>
                          </div>
                        )}
                        {selector.children.length > 0 && (
                          <div>
                            <p className="text-xs font-semibold text-muted-foreground mb-1">
                              Children ({selector.children.length}):
                            </p>
                            <div className="space-y-1">
                              {selector.children.map((child, i) => (
                                <code
                                  key={i}
                                  className="text-xs font-mono bg-muted px-2 py-1 rounded block break-all"
                                >
                                  {child}
                                </code>
                              ))}
                            </div>
                          </div>
                        )}
                        {selector.siblings.length > 0 && (
                          <div>
                            <p className="text-xs font-semibold text-muted-foreground mb-1">
                              Siblings ({selector.siblings.length}):
                            </p>
                            <div className="space-y-1">
                              {selector.siblings.map((sibling, i) => (
                                <code
                                  key={i}
                                  className="text-xs font-mono bg-muted px-2 py-1 rounded block break-all"
                                >
                                  {sibling}
                                </code>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Add Selected Button */}
      <div className="flex justify-end">
        <Button
          onClick={onAddSelectors}
          disabled={selectedSelectors.size === 0}
        >
          Add Selected to Database ({selectedSelectors.size})
        </Button>
      </div>

      {/* Recommendations */}
      {results.recommendations.length > 0 && (
        <div className="border rounded-lg p-4 bg-blue-50 dark:bg-blue-950">
          <h4 className="font-semibold mb-2 text-blue-900 dark:text-blue-100">
            Recommendations
          </h4>
          <ul className="space-y-1 list-disc list-inside text-sm text-blue-800 dark:text-blue-200">
            {results.recommendations.map((rec, index) => (
              <li key={index}>{rec}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Warnings */}
      {results.warnings.length > 0 && (
        <div className="border rounded-lg p-4 bg-yellow-50 dark:bg-yellow-950 border-yellow-200 dark:border-yellow-800">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
            <h4 className="font-semibold text-yellow-900 dark:text-yellow-100">
              Warnings
            </h4>
          </div>
          <ul className="space-y-1 list-disc list-inside text-sm text-yellow-800 dark:text-yellow-200">
            {results.warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Patterns */}
      {results.patterns.length > 0 && (
        <div className="border rounded-lg p-4">
          <h4 className="font-semibold mb-2">Identified Patterns</h4>
          <ul className="space-y-1 list-disc list-inside text-sm text-muted-foreground">
            {results.patterns.map((pattern, index) => (
              <li key={index}>{pattern}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

