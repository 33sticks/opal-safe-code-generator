import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
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
import { useCreateUser, useBrands } from '@/hooks/useApi'
import { useAuth } from '@/contexts/AuthContext'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

const userCreateSchema = z.object({
  email: z.string().email('Invalid email address'),
  name: z.string().min(1, 'Name is required'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  brand_id: z.number().nullable().optional(),
  brand_role: z.enum(['super_admin', 'brand_admin', 'brand_user']),
})

type UserCreateFormValues = z.infer<typeof userCreateSchema>

interface CreateUserFormProps {
  onSuccess?: () => void
}

export function CreateUserForm({ onSuccess }: CreateUserFormProps) {
  const { user, isSuperAdmin, isBrandAdmin } = useAuth()
  const { data: brands } = useBrands()
  const createUser = useCreateUser()

  const form = useForm<UserCreateFormValues>({
    resolver: zodResolver(userCreateSchema),
    defaultValues: {
      email: '',
      name: '',
      password: '',
      brand_id: isBrandAdmin() ? user?.brand_id ?? undefined : undefined,
      brand_role: 'brand_user',
    },
  })

  useEffect(() => {
    if (isBrandAdmin() && user?.brand_id) {
      form.setValue('brand_id', user.brand_id)
    }
  }, [isBrandAdmin, user, form])

  // Watch brand_role to auto-set brand_id to null for super_admin
  const brandRole = form.watch('brand_role')
  
  useEffect(() => {
    if (brandRole === 'super_admin') {
      form.setValue('brand_id', null)
    }
  }, [brandRole, form])

  const onSubmit = async (values: UserCreateFormValues) => {
    try {
      // For super_admin, brand_id should be null/undefined
      const brandId = values.brand_role === 'super_admin' 
        ? undefined 
        : (values.brand_id ?? undefined)
      
      await createUser.mutateAsync({
        email: values.email,
        password: values.password,
        name: values.name,
        brand_id: brandId,
        brand_role: values.brand_role,
        role: 'user',
      })
      form.reset()
      onSuccess?.()
    } catch (err) {
      // Error handling is done in the hook via toast
      console.error('Failed to create user:', err)
    }
  }

  const availableRoles = isSuperAdmin()
    ? ['super_admin', 'brand_admin', 'brand_user']
    : ['brand_admin', 'brand_user']

  const roleLabels: Record<string, string> = {
    super_admin: 'Super Admin',
    brand_admin: 'Brand Admin',
    brand_user: 'Brand User',
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Email</FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="user@example.com"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input placeholder="John Doe" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Password</FormLabel>
              <FormControl>
                <Input
                  type="password"
                  placeholder="Minimum 8 characters"
                  {...field}
                />
              </FormControl>
              <FormMessage />
              <p className="text-sm text-muted-foreground">
                Minimum 8 characters
              </p>
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="brand_id"
          render={({ field }) => {
            const isSuperAdminRole = brandRole === 'super_admin'
            const isDisabled = isBrandAdmin() || isSuperAdminRole
            
            return (
              <FormItem>
                <FormLabel>Brand</FormLabel>
                <Select
                  disabled={isDisabled}
                  onValueChange={(value) =>
                    field.onChange(value === 'none' ? null : parseInt(value))
                  }
                  value={
                    field.value === null || field.value === undefined
                      ? 'none'
                      : field.value.toString()
                  }
                >
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select brand" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {isSuperAdmin() && (
                      <SelectItem value="none">None (Super Admin)</SelectItem>
                    )}
                    {brands?.map((brand) => (
                      <SelectItem key={brand.id} value={brand.id.toString()}>
                        {brand.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormMessage />
                {isBrandAdmin() && (
                  <p className="text-sm text-muted-foreground">
                    Your brand: {brands?.find((b) => b.id === user?.brand_id)?.name}
                  </p>
                )}
                {isSuperAdminRole && (
                  <p className="text-sm text-muted-foreground">
                    Super Admin users do not have an associated brand
                  </p>
                )}
              </FormItem>
            )
          }}
        />

        <FormField
          control={form.control}
          name="brand_role"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Role</FormLabel>
              <Select onValueChange={field.onChange} value={field.value}>
                <FormControl>
                  <SelectTrigger>
                    <SelectValue placeholder="Select role" />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  {availableRoles.map((role) => (
                    <SelectItem key={role} value={role}>
                      {roleLabels[role]}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="flex justify-end gap-2 pt-4">
          <Button
            type="submit"
            disabled={createUser.isPending}
          >
            {createUser.isPending ? (
              <>
                <LoadingSpinner className="mr-2 h-4 w-4" />
                Creating...
              </>
            ) : (
              'Create User'
            )}
          </Button>
        </div>
      </form>
    </Form>
  )
}

