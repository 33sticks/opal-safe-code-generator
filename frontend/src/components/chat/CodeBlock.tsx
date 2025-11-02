import { useState, useMemo } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Copy, Check, Info } from 'lucide-react'
import { ConfidenceScoreBreakdown } from './ConfidenceScoreBreakdown'
import type { GeneratedCode } from '@/types/chat'

interface CodeBlockProps {
  code: GeneratedCode
}

export function CodeBlock({ code }: CodeBlockProps) {
  const [copied, setCopied] = useState(false)
  const [showBreakdown, setShowBreakdown] = useState(false)

  // Process the code string to handle escaped newlines and JSON encoding
  const processedCode = useMemo(() => {
    let codeString = code.generated_code

    // If code is a JSON string, try to parse it
    if (typeof codeString === 'string') {
      // Check if it looks like JSON (starts with { or [)
      if (codeString.trim().startsWith('{') || codeString.trim().startsWith('[')) {
        try {
          const parsed = JSON.parse(codeString)
          // If it has a "generated_code" field, extract it
          if (parsed && typeof parsed === 'object' && 'generated_code' in parsed) {
            codeString = parsed.generated_code || codeString
          } else if (typeof parsed === 'string') {
            codeString = parsed
          }
        } catch {
          // Not valid JSON, continue with original string
        }
      }
    }

    // Replace escaped newlines with actual newlines
    codeString = String(codeString).replace(/\\n/g, '\n')
    // Replace escaped tabs
    codeString = codeString.replace(/\\t/g, '\t')
    // Replace other common escape sequences
    codeString = codeString.replace(/\\r/g, '\r')
    codeString = codeString.replace(/\\'/g, "'")
    codeString = codeString.replace(/\\"/g, '"')

    return codeString
  }, [code.generated_code])

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(processedCode)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy code:', err)
    }
  }

  return (
    <Card className="mt-4">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <h4 className="text-sm font-semibold">Generated Code</h4>
            {code.confidence_score !== null && code.confidence_score !== undefined && (
              <div className="flex items-center gap-1">
                <span className="text-xs px-2 py-1 rounded bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200">
                  Confidence: {Math.round(code.confidence_score * 100)}%
                </span>
                <button
                  onClick={() => setShowBreakdown(true)}
                  className="p-1 rounded hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
                  aria-label="View confidence score breakdown"
                  title="Why this score?"
                >
                  <Info className="h-3 w-3 text-blue-600 dark:text-blue-400" />
                </button>
              </div>
            )}
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            className="h-8"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4 mr-2" />
                Copied!
              </>
            ) : (
              <>
                <Copy className="h-4 w-4 mr-2" />
                Copy
              </>
            )}
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <SyntaxHighlighter
            language="javascript"
            style={vscDarkPlus}
            customStyle={{
              margin: 0,
              borderRadius: '0 0 0.5rem 0.5rem',
              fontSize: '0.875rem',
            }}
            showLineNumbers
          >
            {processedCode}
          </SyntaxHighlighter>
        </div>
      </CardContent>
      
      <ConfidenceScoreBreakdown
        open={showBreakdown}
        onOpenChange={setShowBreakdown}
        breakdown={code.confidence_breakdown ?? null}
        score={code.confidence_score ?? null}
      />
    </Card>
  )
}

