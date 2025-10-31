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
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { useSelector, useCreateSelector, useUpdateSelector, useBrands } from '@/hooks/useApi'
import { useToast } from '@/hooks/use-toast'
import { PageType, SelectorStatus } from '@/types'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

const selectorSchema = z.object({
  brand_id: z.number().min(1, 'Brand is required'),
  page_type: z.nativeEnum(PageType),
  selector: z.string().min(1, 'Selector is required'),
  description: z.string().optional(),
  status: z.nativeEnum(SelectorStatus),
})

type SelectorFormValues = z.infer<typeof selectorSchema>

interface SelectorsFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  selectorId?: number
}

export function SelectorsForm({ open, onOpenChange, selectorId }: SelectorsFormProps) {
  const { data: selector, isLoading: isLoadingSelector } = useSelector(selectorId || 0)
  const { data: brands } = useBrands()
  const createSelector = useCreateSelector()
  const updateSelector = useUpdateSelector()
  const { toast } = useToast()

  const form = useForm<SelectorFormValues>({
    resolver: zodResolver(selectorSchema),
    defaultValues: {
      brand_id: 0,
      page_type: PageType.PDP,
      selector: '',
      description: '',
      status: SelectorStatus.ACTIVE,
    },
  })

  useEffect(() => {
    if (selector && selectorId) {
      form.reset({
        brand_id: selector.brand_id,
        page_type: selector.page_type,
        selector: selector.selector,
        description: selector.description || '',
        status: selector.status,
      })
    } else {
      form.reset({
        brand_id: brands?.[0]?.id || 0,
        page_type: PageType.PDP,
        selector: '',
        description: '',
        status: SelectorStatus.ACTIVE,
      })
    }
  }, [selector, selectorId, form, brands])

  const onSubmit = async (values: SelectorFormValues) => {
    try {
      if (selectorId) {
        await updateSelector.mutateAsync({
          id: selectorId,
          ...values,
        })
        toast({
          title: 'Success',
          description: 'Selector updated successfully',
        })
      } else {
        await createSelector.mutateAsync(values)
        toast({
          title: 'Success',
          description: 'Selector created successfully',
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

  const isLoading = isLoadingSelector || createSelector.isPending || updateSelector.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{selectorId ? 'Edit Selector' : 'Create Selector'}</DialogTitle>
          <DialogDescription>
            {selectorId ? 'Update selector information' : 'Add a new selector to the system'}
          </DialogDescription>
        </DialogHeader>

        {isLoading && !selector && selectorId ? (
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
                name="page_type"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Page Type</FormLabel>
                    <Select onValueChange={field.onChange} value={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select page type" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value={PageType.PDP}>PDP</SelectItem>
                        <SelectItem value={PageType.CART}>Cart</SelectItem>
                        <SelectItem value={PageType.CHECKOUT}>Checkout</SelectItem>
                        <SelectItem value={PageType.HOME}>Home</SelectItem>
                        <SelectItem value={PageType.CATEGORY}>Category</SelectItem>
                        <SelectItem value={PageType.SEARCH}>Search</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="selector"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Selector</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder=".product-title or #main-content"
                        className="font-mono text-sm"
                        rows={3}
                        {...field}
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
                      <Input placeholder="Selector description" {...field} />
                    </FormControl>
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
                        <SelectItem value={SelectorStatus.ACTIVE}>Active</SelectItem>
                        <SelectItem value={SelectorStatus.INACTIVE}>Inactive</SelectItem>
                        <SelectItem value={SelectorStatus.DEPRECATED}>Deprecated</SelectItem>
                      </SelectContent>
                    </Select>
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
                      {selectorId ? 'Updating...' : 'Creating...'}
                    </>
                  ) : (
                    selectorId ? 'Update' : 'Create'
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

