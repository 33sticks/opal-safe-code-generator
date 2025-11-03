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
  FormDescription,
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
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { useBrand, useCreateBrand, useUpdateBrand } from '@/hooks/useApi'
import { useToast } from '@/hooks/use-toast'
import { BrandStatus } from '@/types'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

const brandSchema = z.object({
  name: z.string().min(1, 'Name is required').max(255),
  domain: z.string().min(1, 'Domain is required').max(255),
  status: z.nativeEnum(BrandStatus),
  code_template: z.string().optional(),
})

type BrandFormValues = z.infer<typeof brandSchema>

interface BrandFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  brandId?: number
}

export function BrandForm({ open, onOpenChange, brandId }: BrandFormProps) {
  const { data: brand, isLoading: isLoadingBrand } = useBrand(brandId || 0)
  const createBrand = useCreateBrand()
  const updateBrand = useUpdateBrand()
  const { toast } = useToast()

  const form = useForm<BrandFormValues>({
    resolver: zodResolver(brandSchema),
    defaultValues: {
      name: '',
      domain: '',
      status: BrandStatus.ACTIVE,
      code_template: '',
    },
  })

  useEffect(() => {
    if (brand && brandId) {
      form.reset({
        name: brand.name,
        domain: brand.domain,
        status: brand.status,
        code_template: JSON.stringify(brand.code_template || {}, null, 2),
      })
    } else {
      form.reset({
        name: '',
        domain: '',
        status: BrandStatus.ACTIVE,
        code_template: '',
      })
    }
  }, [brand, brandId, form])

  const onSubmit = async (values: BrandFormValues) => {
    try {
      let codeTemplateObj = {}
      if (values.code_template) {
        try {
          codeTemplateObj = JSON.parse(values.code_template)
        } catch {
          toast({
            title: 'Invalid JSON',
            description: 'Code template must be valid JSON',
            variant: 'destructive',
          })
          return
        }
      }

      if (brandId) {
        await updateBrand.mutateAsync({
          id: brandId,
          name: values.name,
          domain: values.domain,
          status: values.status,
          code_template: codeTemplateObj,
        })
        toast({
          title: 'Success',
          description: 'Brand updated successfully',
        })
      } else {
        await createBrand.mutateAsync({
          name: values.name,
          domain: values.domain,
          status: values.status,
          code_template: codeTemplateObj,
        })
        toast({
          title: 'Success',
          description: 'Brand created successfully',
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

  const isLoading = isLoadingBrand || createBrand.isPending || updateBrand.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{brandId ? 'Edit Brand' : 'Create Brand'}</DialogTitle>
          <DialogDescription>
            {brandId ? 'Update brand information' : 'Add a new brand to the system'}
          </DialogDescription>
        </DialogHeader>

        {isLoading && !brand && brandId ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <FormField
                control={form.control}
                name="name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Name</FormLabel>
                    <FormControl>
                      <Input placeholder="Brand name" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="domain"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Domain</FormLabel>
                    <FormControl>
                      <Input placeholder="vans.com" {...field} />
                    </FormControl>
                    <p className="text-xs text-gray-500 mt-1">
                      Primary website domain for this brand
                    </p>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value={BrandStatus.ACTIVE}>Active</SelectItem>
                        <SelectItem value={BrandStatus.INACTIVE}>Inactive</SelectItem>
                        <SelectItem value={BrandStatus.ARCHIVED}>Archived</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="code_template"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Code Template (JSON)</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder='{"key": "value"}'
                        className="font-mono text-sm"
                        rows={6}
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Controls code structure, logging, and style for all generated code. Options: leave empty for default behavior, or provide custom JSON. Starter templates coming soon.
                    </FormDescription>
                    <p className="text-xs text-gray-500 mt-1">
                      Optional - Leave empty for default behavior
                    </p>
                    <FormMessage />
                  </FormItem>
                )}
              />

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
                      {brandId ? 'Updating...' : 'Creating...'}
                    </>
                  ) : (
                    brandId ? 'Update' : 'Create'
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

