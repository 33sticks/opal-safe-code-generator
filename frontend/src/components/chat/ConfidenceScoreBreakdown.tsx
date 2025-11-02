import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { CheckCircle2, XCircle, AlertTriangle, Info } from 'lucide-react'
import type { ConfidenceBreakdown } from '@/types/chat'

interface ConfidenceScoreBreakdownProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  breakdown: ConfidenceBreakdown | null
  score: number | null
}

export function ConfidenceScoreBreakdown({
  open,
  onOpenChange,
  breakdown,
  score,
}: ConfidenceScoreBreakdownProps) {
  if (!breakdown && score === null) {
    return null
  }

  const overallScore = breakdown?.overall_score ?? score ?? 0
  const scorePercentage = Math.round(overallScore * 100)
  
  // Determine confidence level
  const getConfidenceLevel = (score: number): { label: string; color: string } => {
    if (score >= 0.8) return { label: 'High Confidence', color: 'text-green-600 dark:text-green-400' }
    if (score >= 0.6) return { label: 'Medium Confidence', color: 'text-yellow-600 dark:text-yellow-400' }
    return { label: 'Low Confidence', color: 'text-red-600 dark:text-red-400' }
  }

  const confidenceLevel = getConfidenceLevel(overallScore)

  // Get recommendation display
  const getRecommendationDisplay = (rec: string) => {
    switch (rec) {
      case 'safe_to_use':
        return {
          label: 'Safe to Use',
          description: 'This code meets all validation criteria and follows best practices. You can proceed with deployment.',
          icon: CheckCircle2,
          color: 'bg-green-50 border-green-200 text-green-900 dark:bg-green-900/20 dark:border-green-800 dark:text-green-300',
        }
      case 'review_carefully':
        return {
          label: 'Review Carefully',
          description: 'This code passed validation but may need manual review before deployment. Check the details below.',
          icon: AlertTriangle,
          color: 'bg-yellow-50 border-yellow-200 text-yellow-900 dark:bg-yellow-900/20 dark:border-yellow-800 dark:text-yellow-300',
        }
      case 'needs_fixes':
        return {
          label: 'Needs Fixes',
          description: 'This code has validation issues that should be addressed before deployment. See the violations below.',
          icon: XCircle,
          color: 'bg-red-50 border-red-200 text-red-900 dark:bg-red-900/20 dark:border-red-800 dark:text-red-300',
        }
      default:
        return {
          label: 'Unknown',
          description: 'Unable to determine recommendation.',
          icon: Info,
          color: 'bg-gray-50 border-gray-200 text-gray-900 dark:bg-gray-900/20 dark:border-gray-800 dark:text-gray-300',
        }
    }
  }

  const recommendation = breakdown
    ? getRecommendationDisplay(breakdown.recommendation)
    : null

  // Get validation status display
  const getValidationStatusDisplay = (status: string) => {
    switch (status) {
      case 'passed':
        return { icon: CheckCircle2, color: 'text-green-600 dark:text-green-400', label: 'Passed' }
      case 'failed':
        return { icon: XCircle, color: 'text-red-600 dark:text-red-400', label: 'Failed' }
      case 'warning':
        return { icon: AlertTriangle, color: 'text-yellow-600 dark:text-yellow-400', label: 'Warning' }
      default:
        return { icon: Info, color: 'text-gray-600 dark:text-gray-400', label: 'Unknown' }
    }
  }

  const validationStatus = breakdown
    ? getValidationStatusDisplay(breakdown.validation_status)
    : null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Confidence Score Breakdown</DialogTitle>
          <DialogDescription>
            Understand how this confidence score was calculated and what it means for your code.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-6 mt-4">
          {/* Overall Score */}
          <div className="space-y-2">
            <h3 className="text-sm font-semibold">Overall Score</h3>
            <div className="flex items-center gap-4">
              <div className="text-3xl font-bold">{scorePercentage}%</div>
              <div className={confidenceLevel.color}>
                <span className="font-medium">{confidenceLevel.label}</span>
              </div>
            </div>
            <p className="text-sm text-muted-foreground">
              This score reflects how well the generated code matches your templates, follows your rules, and uses valid selectors.
            </p>
          </div>

          {breakdown && (
            <>
              {/* Recommendation Banner */}
              {recommendation && (
                <div className={`rounded-lg border p-4 ${recommendation.color}`}>
                  <div className="flex items-start gap-3">
                    <recommendation.icon className="h-5 w-5 mt-0.5 flex-shrink-0" />
                    <div className="flex-1">
                      <h4 className="font-semibold mb-1">{recommendation.label}</h4>
                      <p className="text-sm">{recommendation.description}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Validation Status */}
              {validationStatus && (
                <div className="space-y-2">
                  <h3 className="text-sm font-semibold">Validation Status</h3>
                  <div className="flex items-center gap-2">
                    <validationStatus.icon className={`h-5 w-5 ${validationStatus.color}`} />
                    <span className={validationStatus.color}>{validationStatus.label}</span>
                  </div>
                  {breakdown.is_valid && (
                    <p className="text-sm text-muted-foreground">
                      The code passed all validation checks.
                    </p>
                  )}
                  {!breakdown.is_valid && (
                    <p className="text-sm text-muted-foreground">
                      The code did not pass all validation checks. See details below.
                    </p>
                  )}
                </div>
              )}

              {/* Quality Metrics Breakdown */}
              <div className="space-y-3">
                <h3 className="text-sm font-semibold">Quality Metrics</h3>
                <div className="space-y-2">
                  {/* Template Match Quality */}
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-2">
                      <Info className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Template Match Quality</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">
                        {Math.round((breakdown.template_score / 0.3) * 100)}%
                      </span>
                      <span className="text-xs text-muted-foreground">(30% weight)</span>
                    </div>
                  </div>

                  {/* Rules Compliance */}
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-2">
                      <Info className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Rules Compliance</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">
                        {Math.round((breakdown.rule_score / 0.4) * 100)}%
                      </span>
                      <span className="text-xs text-muted-foreground">(40% weight)</span>
                    </div>
                  </div>

                  {/* Selector Validation */}
                  <div className="flex items-center justify-between p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-2">
                      <Info className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">Selector Validation</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium">
                        {Math.round((breakdown.selector_score / 0.3) * 100)}%
                      </span>
                      <span className="text-xs text-muted-foreground">(30% weight)</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Contributing Factors */}
              {(breakdown.rule_violations.length > 0 || breakdown.invalid_selectors.length > 0) && (
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold">Issues Found</h3>
                  
                  {/* Rule Violations */}
                  {breakdown.rule_violations.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
                        <span className="text-sm font-medium">
                          Rule Violations ({breakdown.rule_violations.length})
                        </span>
                      </div>
                      <ul className="list-disc list-inside space-y-1 ml-6 text-sm text-muted-foreground">
                        {breakdown.rule_violations.map((violation, idx) => (
                          <li key={idx}>{violation}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Invalid Selectors */}
                  {breakdown.invalid_selectors.length > 0 && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                        <span className="text-sm font-medium">
                          Invalid Selectors ({breakdown.invalid_selectors.length})
                        </span>
                      </div>
                      <ul className="list-disc list-inside space-y-1 ml-6 text-sm text-muted-foreground">
                        {breakdown.invalid_selectors.map((selector, idx) => (
                          <li key={idx}>{selector}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}

              {/* No Issues */}
              {breakdown.rule_violations.length === 0 &&
                breakdown.invalid_selectors.length === 0 && (
                  <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg dark:bg-green-900/20 dark:border-green-800">
                    <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
                    <span className="text-sm text-green-900 dark:text-green-300">
                      No validation issues found. The code follows all rules and uses valid selectors.
                    </span>
                  </div>
                )}
            </>
          )}

          {/* Fallback for when breakdown is not available */}
          {!breakdown && score !== null && (
            <div className="p-4 bg-muted rounded-lg">
              <p className="text-sm text-muted-foreground">
                Detailed breakdown is not available for this code. The confidence score is {scorePercentage}%.
              </p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
}

