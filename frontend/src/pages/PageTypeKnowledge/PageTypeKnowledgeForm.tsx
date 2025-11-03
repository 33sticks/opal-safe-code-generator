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
import { usePageTypeKnowledgeItem, useCreatePageTypeKnowledge, useUpdatePageTypeKnowledge, useBrands } from '@/hooks/useApi'
import { useToast } from '@/hooks/use-toast'
import { TestType } from '@/types'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { CodeEditor } from '@/components/monaco/CodeEditor'

const knowledgeSchema = z.object({
  brand_id: z.number().min(1, 'Brand is required'),
  test_type: z.nativeEnum(TestType),
  template_code: z.string().min(1, 'Knowledge code is required'),
  description: z.string().optional(),
  version: z.string().max(50).default('1.0'),
  is_active: z.boolean().default(true),
})

type KnowledgeFormValues = z.infer<typeof knowledgeSchema>

interface PageTypeKnowledgeFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  knowledgeId?: number
}

export function PageTypeKnowledgeForm({ open, onOpenChange, knowledgeId }: PageTypeKnowledgeFormProps) {
  const { data: knowledge, isLoading: isLoadingKnowledge } = usePageTypeKnowledgeItem(knowledgeId || 0)
  const { data: brands } = useBrands()
  const createKnowledge = useCreatePageTypeKnowledge()
  const updateKnowledge = useUpdatePageTypeKnowledge()
  const { toast } = useToast()

  const form = useForm<KnowledgeFormValues>({
    resolver: zodResolver(knowledgeSchema),
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
    if (knowledge && knowledgeId) {
      form.reset({
        brand_id: knowledge.brand_id,
        test_type: knowledge.test_type,
        template_code: knowledge.template_code,
        description: knowledge.description || '',
        version: knowledge.version,
        is_active: knowledge.is_active,
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
  }, [knowledge, knowledgeId, form, brands])

  const onSubmit = async (values: KnowledgeFormValues) => {
    try {
      if (knowledgeId) {
        await updateKnowledge.mutateAsync({
          id: knowledgeId,
          ...values,
        })
        toast({
          title: 'Success',
          description: 'Page knowledge updated successfully',
        })
      } else {
        await createKnowledge.mutateAsync(values)
        toast({
          title: 'Success',
          description: 'Page knowledge created successfully',
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

  const isLoading = isLoadingKnowledge || createKnowledge.isPending || updateKnowledge.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{knowledgeId ? 'Edit Page Knowledge' : 'Add Page Knowledge'}</DialogTitle>
          <DialogDescription>
            {knowledgeId ? 'Update page knowledge information' : 'Add a new page knowledge entry to the system'}
          </DialogDescription>
        </DialogHeader>

        {isLoading && !knowledge && knowledgeId ? (
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
                    <FormLabel>Knowledge Code</FormLabel>
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
                      <Input placeholder="Page knowledge description" {...field} />
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
                      {knowledgeId ? 'Updating...' : 'Creating...'}
                    </>
                  ) : (
                    knowledgeId ? 'Update' : 'Create'
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

