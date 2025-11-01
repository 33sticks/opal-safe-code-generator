import { useState } from 'react'
import { UserPlus } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { CreateUserDialog } from '@/components/admin/CreateUserDialog'

export function UsersPage() {
  const [createDialogOpen, setCreateDialogOpen] = useState(false)

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">User Management</h1>
          <p className="text-muted-foreground mt-1">
            Manage users and their access
          </p>
        </div>
        <Button onClick={() => setCreateDialogOpen(true)}>
          <UserPlus className="mr-2 h-4 w-4" />
          Create User
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Users</CardTitle>
          <CardDescription>
            Create and manage user accounts for your team
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-12 text-muted-foreground">
            <UserPlus className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>User listing coming soon</p>
            <p className="text-sm mt-2">
              For now, you can create new users using the button above
            </p>
          </div>
        </CardContent>
      </Card>

      <CreateUserDialog
        open={createDialogOpen}
        onOpenChange={setCreateDialogOpen}
      />
    </div>
  )
}

