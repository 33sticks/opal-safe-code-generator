import { useAuth } from '@/contexts/AuthContext'
import { Button } from '@/components/ui/button'
import { LogOut } from 'lucide-react'
import { NotificationBell } from '@/components/NotificationBell'

export function Header() {
  const { user, logout, isSuperAdmin } = useAuth()

  return (
    <header className="flex h-16 items-center justify-between border-b bg-background px-6">
      <h2 className="text-xl font-semibold">Opal Safe Code Generator</h2>
      {user && (
        <div className="flex items-center gap-4">
          {!isSuperAdmin() && user.brand_name && (
            <div className="text-sm text-muted-foreground">
              {user.brand_name}
            </div>
          )}
          <NotificationBell />
          <div className="text-right">
            <p className="text-sm font-medium">{user.name || user.email}</p>
            <p className="text-xs text-muted-foreground capitalize">
              {user.brand_role?.replace('_', ' ') || user.role}
            </p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={logout}
            className="gap-2"
          >
            <LogOut className="h-4 w-4" />
            Logout
          </Button>
        </div>
      )}
    </header>
  )
}

