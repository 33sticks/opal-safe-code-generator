import { Link, useLocation } from 'react-router-dom'
import { 
  Building2, 
  FileText, 
  MousePointerClick, 
  Shield, 
  Code,
  MessageSquare,
  Menu,
  X,
  Bell,
  FolderOpen
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/contexts/AuthContext'

const superAdminNavigation = [
  { name: 'Brands', href: '/brands', icon: Building2 },
  { name: 'Templates', href: '/templates', icon: FileText },
  { name: 'Selectors', href: '/selectors', icon: MousePointerClick },
  { name: 'Rules', href: '/rules', icon: Shield },
  { name: 'Generated Code', href: '/generated-code', icon: Code },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'My Requests', href: '/my-requests', icon: FolderOpen },
  { name: 'Notifications', href: '/notifications', icon: Bell },
]

const brandAdminNavigation = [
  { name: 'Templates', href: '/templates', icon: FileText },
  { name: 'Selectors', href: '/selectors', icon: MousePointerClick },
  { name: 'Rules', href: '/rules', icon: Shield },
  { name: 'Generated Code', href: '/generated-code', icon: Code },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'My Requests', href: '/my-requests', icon: FolderOpen },
  { name: 'Notifications', href: '/notifications', icon: Bell },
]

const brandUserNavigation = [
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'My Requests', href: '/my-requests', icon: FolderOpen },
  { name: 'Notifications', href: '/notifications', icon: Bell },
]

export function Sidebar() {
  const location = useLocation()
  const [isMobileOpen, setIsMobileOpen] = useState(false)
  const { isSuperAdmin, isBrandAdmin } = useAuth()
  
  let navigation = brandUserNavigation
  if (isSuperAdmin()) {
    navigation = superAdminNavigation
  } else if (isBrandAdmin()) {
    navigation = brandAdminNavigation
  }

  return (
    <>
      {/* Mobile menu button */}
      <button
        className="fixed left-4 top-4 z-50 lg:hidden"
        onClick={() => setIsMobileOpen(!isMobileOpen)}
        aria-label="Toggle menu"
      >
        {isMobileOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <Menu className="h-6 w-6" />
        )}
      </button>

      {/* Mobile overlay */}
      {isMobileOpen && (
        <div
          className="fixed inset-0 z-40 bg-background/80 backdrop-blur-sm lg:hidden"
          onClick={() => setIsMobileOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 w-64 transform border-r bg-card transition-transform duration-200 ease-in-out lg:relative lg:translate-x-0',
          isMobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        )}
      >
        <div className="flex h-full flex-col">
          <div className="flex h-16 items-center border-b px-6">
            <h1 className="text-lg font-semibold">Opal Safe Code</h1>
          </div>
          <nav className="flex-1 space-y-1 px-3 py-4">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href
              const Icon = item.icon
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setIsMobileOpen(false)}
                  className={cn(
                    'flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                    isActive
                      ? 'bg-primary text-primary-foreground'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  )}
                >
                  <Icon className="h-5 w-5" />
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>
      </aside>
    </>
  )
}

