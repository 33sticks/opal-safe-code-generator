import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '@/components/ui/form'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { useTemplate, useCreateTemplate, useUpdateTemplate, useBrands } from '@/hooks/useApi'
import { useToast } from '@/hooks/use-toast'
import { TestType } from '@/types'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { CodeEditor } from '@/components/monaco/CodeEditor'

const templateSchema = z.object({
  brand_id: z.number().min(1, 'Brand is required'),
  test_type: z.nativeEnum(TestType),
  template_code: z.string().min(1, 'Template code is required'),
  description: z.string().optional(),
  version: z.string().max(50).default('1.0'),
  is_active: z.boolean().default(true),
})

type TemplateFormValues = z.infer<typeof templateSchema>

interface TemplatesFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  templateId?: number
}

export function TemplatesForm({ open, onOpenChange, templateId }: TemplatesFormProps) {
  const { data: template, isLoading: isLoadingTemplate } = useTemplate(templateId || 0)
  const { data: brands } = useBrands()
  const createTemplate = useCreateTemplate()
  const updateTemplate = useUpdateTemplate()
  const { toast } = useToast()

  const form = useForm<TemplateFormValues>({
    resolver: zodResolver(templateSchema),
    defaultValues: {
      brand_id: 0,
      test_type: TestType.PDP,
      template_code: '',
      description: '',
      version: '1.0',
      is_active: true,
    },
  })

  useEffect(() => {
    if (template && templateId) {
      form.reset({
        brand_id: template.brand_id,
        test_type: template.test_type,
        template_code: template.template_code,
        description: template.description || '',
        version: template.version,
        is_active: template.is_active,
      })
    } else {
      form.reset({
        brand_id: brands?.[0]?.id || 0,
        test_type: TestType.PDP,
        template_code: '',
        description: '',
        version: '1.0',
        is_active: true,
      })
    }
  }, [template, templateId, form, brands])

  const onSubmit = async (values: TemplateFormValues) => {
    try {
      if (templateId) {
        await updateTemplate.mutateAsync({
          id: templateId,
          ...values,
        })
        toast({
          title: 'Success',
          description: 'Template updated successfully',
        })
      } else {
        await createTemplate.mutateAsync(values)
        toast({
          title: 'Success',
          description: 'Template created successfully',
        })
      }
      onOpenChange(false)
      form.reset()
    } catch (err) {
      toast({
        title: 'Error',
        description: err instanceof Error ? err.message : 'Operation failed',
        variant: 'destructive',
      })
    }
  }

  const isLoading = isLoadingTemplate || createTemplate.isPending || updateTemplate.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{templateId ? 'Edit Template' : 'Create Template'}</DialogTitle>
          <DialogDescription>
            {templateId ? 'Update template information' : 'Add a new template to the system'}
          </DialogDescription>
        </DialogHeader>

        {isLoading && !template && templateId ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="brand_id"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Brand</FormLabel>
                    <Select
                      onValueChange={(value) => field.onChange(parseInt(value))}
                      value={field.value.toString()}
                    >
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select brand" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        {brands?.map((brand) => (
                          <SelectItem key={brand.id} value={brand.id.toString()}>
                            {brand.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="test_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Test Type</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select test type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value={TestType.PDP}>PDP</SelectItem>
                        <SelectItem value={TestType.CART}>Cart</SelectItem>
                        <SelectItem value={TestType.CHECKOUT}>Checkout</SelectItem>
                        <SelectItem value={TestType.HOME}>Home</SelectItem>
                        <SelectItem value={TestType.CATEGORY}>Category</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="template_code"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Template Code</FormLabel>
                    <FormControl>
                      <CodeEditor
                        value={field.value}
                        onChange={field.onChange}
                        language="javascript"
                        height="300px"
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="description"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Description</FormLabel>
                    <FormControl>
                      <Input placeholder="Template description" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="grid grid-cols-2 gap-4">
                <FormField
                  control={form.control}
                  name="version"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Version</FormLabel>
                      <FormControl>
                        <Input placeholder="1.0" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="is_active"
                  render={({ field }) => (
                    <FormItem className="flex flex-row items-start space-x-3 space-y-0 rounded-md border p-4">
                      <FormControl>
                        <Checkbox
                          checked={field.value}
                          onCheckedChange={field.onChange}
                        />
                      </FormControl>
                      <div className="space-y-1 leading-none">
                        <FormLabel>Active</FormLabel>
                      </div>
                    </FormItem>
                  )}
                />
              </div>

              <DialogFooter>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => onOpenChange(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" disabled={isLoading}>
                  {isLoading ? (
                    <>
                      <LoadingSpinner className="mr-2 h-4 w-4" />
                      {templateId ? 'Updating...' : 'Creating...'}
                    </>
                  ) : (
                    templateId ? 'Update' : 'Create'
                  )}
                </Button>
              </DialogFooter>
            </form>
          </Form>
        )}
      </DialogContent>
    </Dialog>
  )
}

