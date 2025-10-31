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
import { useRule, useCreateRule, useUpdateRule, useBrands } from '@/hooks/useApi'
import { useToast } from '@/hooks/use-toast'
import { RuleType } from '@/types'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { CodeEditor } from '@/components/monaco/CodeEditor'

const ruleSchema = z.object({
  brand_id: z.number().min(1, 'Brand is required'),
  rule_type: z.nativeEnum(RuleType),
  rule_content: z.string().min(1, 'Rule content is required'),
  priority: z.number().min(1).max(10).default(1),
})

type RuleFormValues = z.infer<typeof ruleSchema>

interface RulesFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  ruleId?: number
}

export function RulesForm({ open, onOpenChange, ruleId }: RulesFormProps) {
  const { data: rule, isLoading: isLoadingRule } = useRule(ruleId || 0)
  const { data: brands } = useBrands()
  const createRule = useCreateRule()
  const updateRule = useUpdateRule()
  const { toast } = useToast()

  const form = useForm<RuleFormValues>({
    resolver: zodResolver(ruleSchema),
    defaultValues: {
      brand_id: 0,
      rule_type: RuleType.FORBIDDEN_PATTERN,
      rule_content: '',
      priority: 1,
    },
  })

  useEffect(() => {
    if (rule && ruleId) {
      form.reset({
        brand_id: rule.brand_id,
        rule_type: rule.rule_type,
        rule_content: rule.rule_content,
        priority: rule.priority,
      })
    } else {
      form.reset({
        brand_id: brands?.[0]?.id || 0,
        rule_type: RuleType.FORBIDDEN_PATTERN,
        rule_content: '',
        priority: 1,
      })
    }
  }, [rule, ruleId, form, brands])

  const onSubmit = async (values: RuleFormValues) => {
    try {
      if (ruleId) {
        await updateRule.mutateAsync({
          id: ruleId,
          ...values,
        })
        toast({
          title: 'Success',
          description: 'Rule updated successfully',
        })
      } else {
        await createRule.mutateAsync(values)
        toast({
          title: 'Success',
          description: 'Rule created successfully',
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

  const isLoading = isLoadingRule || createRule.isPending || updateRule.isPending

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>{ruleId ? 'Edit Rule' : 'Create Rule'}</DialogTitle>
          <DialogDescription>
            {ruleId ? 'Update rule information' : 'Add a new rule to the system'}
          </DialogDescription>
        </DialogHeader>

        {isLoading && !rule && ruleId ? (
          <div className="flex justify-center py-8">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
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
                  name="rule_type"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Rule Type</FormLabel>
                      <Select onValueChange={field.onChange} value={field.value}>
                        <FormControl>
                          <SelectTrigger>
                            <SelectValue placeholder="Select rule type" />
                          </SelectTrigger>
                        </FormControl>
                        <SelectContent>
                          <SelectItem value={RuleType.FORBIDDEN_PATTERN}>Forbidden Pattern</SelectItem>
                          <SelectItem value={RuleType.REQUIRED_PATTERN}>Required Pattern</SelectItem>
                          <SelectItem value={RuleType.MAX_LENGTH}>Max Length</SelectItem>
                          <SelectItem value={RuleType.MIN_LENGTH}>Min Length</SelectItem>
                        </SelectContent>
                      </Select>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              </div>

              <FormField
                control={form.control}
                name="rule_content"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Rule Content</FormLabel>
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
                name="priority"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Priority (1-10)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min={1}
                        max={10}
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 1)}
                      />
                    </FormControl>
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
                      {ruleId ? 'Updating...' : 'Creating...'}
                    </>
                  ) : (
                    ruleId ? 'Update' : 'Create'
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

