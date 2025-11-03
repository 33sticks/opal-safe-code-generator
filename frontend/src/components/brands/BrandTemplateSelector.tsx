import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { useBrandTemplates, useBrandTemplate } from '@/hooks/useApi'
import { useToast } from '@/hooks/use-toast'

interface BrandTemplateSelectorProps {
  onTemplateSelect: (template: object | null) => void
  currentTemplate?: object | null
}

export function BrandTemplateSelector({
  onTemplateSelect,
  currentTemplate,
}: BrandTemplateSelectorProps) {
  const [selectedTemplateName, setSelectedTemplateName] = useState<string | null>(null)
  const { data: templates, isLoading: isLoadingTemplates, error: templatesError } = useBrandTemplates()
  const { data: selectedTemplateData, isLoading: isLoadingTemplate } = useBrandTemplate(selectedTemplateName || '')
  const { toast } = useToast()

  useEffect(() => {
    if (templatesError) {
      toast({
        title: 'Error',
        description: 'Failed to load templates. Please try again.',
        variant: 'destructive',
      })
    }
  }, [templatesError, toast])

  // Pre-select template if currentTemplate matches an available template
  useEffect(() => {
    if (currentTemplate && templates && templates.length > 0 && !selectedTemplateName) {
      const templateName = (currentTemplate as { name?: string })?.name
      if (templateName) {
        const matchingTemplate = templates.find(
          (t) => t.name.toLowerCase() === templateName.toLowerCase()
        )
        if (matchingTemplate) {
          setSelectedTemplateName(matchingTemplate.name)
        }
      }
    }
  }, [currentTemplate, templates, selectedTemplateName])

  const handleTemplateChange = (templateName: string) => {
    if (templateName === 'custom') {
      setSelectedTemplateName(null)
      onTemplateSelect(null)
    } else {
      setSelectedTemplateName(templateName)
    }
  }

  const handleUseTemplate = () => {
    if (selectedTemplateData) {
      onTemplateSelect(selectedTemplateData)
      toast({
        title: 'Template selected',
        description: 'Template has been applied to the form.',
      })
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Select a Code Template</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {isLoadingTemplates ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner size="lg" />
          </div>
        ) : templates && templates.length > 0 ? (
          <>
            <div className="space-y-3">
              {templates.map((template) => (
                <label
                  key={template.name}
                  className="flex items-start space-x-3 cursor-pointer p-3 rounded-md border hover:bg-accent transition-colors"
                >
                  <input
                    type="radio"
                    name="template"
                    value={template.name}
                    checked={selectedTemplateName === template.name}
                    onChange={() => handleTemplateChange(template.name)}
                    className="w-4 h-4 mt-1"
                  />
                  <div className="flex-1">
                    <div className="font-medium">{template.name}</div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {template.description}
                    </div>
                  </div>
                </label>
              ))}
              <label
                className="flex items-start space-x-3 cursor-pointer p-3 rounded-md border hover:bg-accent transition-colors"
              >
                <input
                  type="radio"
                  name="template"
                  value="custom"
                  checked={selectedTemplateName === null && !selectedTemplateData}
                  onChange={() => handleTemplateChange('custom')}
                  className="w-4 h-4 mt-1"
                />
                <div className="flex-1">
                  <div className="font-medium">Custom (Advanced)</div>
                  <div className="text-sm text-muted-foreground mt-1">
                    Write your own JSON configuration
                  </div>
                </div>
              </label>
            </div>

            {selectedTemplateName && selectedTemplateName !== 'custom' && (
              <div className="space-y-3 pt-4 border-t">
                <Label>Template Preview</Label>
                {isLoadingTemplate ? (
                  <div className="flex justify-center py-4">
                    <LoadingSpinner />
                  </div>
                ) : selectedTemplateData ? (
                  <Textarea
                    value={JSON.stringify(selectedTemplateData, null, 2)}
                    readOnly
                    className="font-mono text-sm"
                    rows={12}
                  />
                ) : null}
                <Button
                  onClick={handleUseTemplate}
                  disabled={!selectedTemplateData || isLoadingTemplate}
                  className="w-full"
                >
                  Use This Template
                </Button>
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-8 text-muted-foreground">
            No templates available
          </div>
        )}
      </CardContent>
    </Card>
  )
}

