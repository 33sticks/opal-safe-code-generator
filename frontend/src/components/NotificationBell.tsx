import { useState, useRef, useEffect } from 'react'
import { Bell, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { Link, useNavigate } from 'react-router-dom'
import { useUnreadCount, useNotifications, useMarkAsRead } from '@/hooks/useApi'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { formatDistanceToNow } from 'date-fns'

export function NotificationBell() {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)
  const navigate = useNavigate()
  const { data: unreadCount = { count: 0 } } = useUnreadCount()
  const { data: notifications = [] } = useNotifications(false)
  const markAsRead = useMarkAsRead()

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const recentNotifications = notifications.slice(0, 5)

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'code_approved':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'code_rejected':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'code_needs_review':
        return <AlertCircle className="h-4 w-4 text-blue-500" />;
      default:
        return <Bell className="h-4 w-4" />;
    }
  };

  const handleNotificationClick = async (notification: { id: number; type: string; generated_code_id?: number | null; read: boolean }) => {
    // Mark as read
    if (!notification.read) {
      await markAsRead.mutateAsync(notification.id)
    }

    // Navigate based on notification type
    if (notification.type === 'code_needs_review') {
      // Admin notification - go to Generated Code page
      navigate('/generated-code');
    } else if (notification.type === 'code_approved' || notification.type === 'code_rejected') {
      // User notification - go to My Requests page
      navigate('/my-requests');
    }

    // Close dropdown
    setIsOpen(false);
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-muted-foreground hover:text-foreground transition-colors"
        aria-label="Notifications"
      >
        <Bell className="h-5 w-5" />
        {unreadCount.count > 0 && (
          <span className="absolute top-0 right-0 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-xs font-semibold text-white">
            {unreadCount.count > 9 ? '9+' : unreadCount.count}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 top-12 z-50 w-80 rounded-lg border bg-popover shadow-lg">
          <div className="p-4 border-b">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold">Notifications</h3>
              {unreadCount.count > 0 && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={async () => {
                    for (const notification of recentNotifications.filter(n => !n.read)) {
                      await markAsRead.mutateAsync(notification.id)
                    }
                  }}
                >
                  Mark all read
                </Button>
              )}
            </div>
          </div>
          <div className="max-h-96 overflow-y-auto">
            {recentNotifications.length === 0 ? (
              <div className="p-4 text-center text-sm text-muted-foreground">
                No notifications
              </div>
            ) : (
              <div className="divide-y">
                {recentNotifications.map((notification) => (
                  <button
                    key={notification.id}
                    onClick={() => handleNotificationClick(notification)}
                    className={cn(
                      'w-full p-4 text-left hover:bg-accent transition-colors',
                      !notification.read && 'bg-accent/50'
                    )}
                  >
                    <div className="flex items-start gap-2">
                      <div className="flex-shrink-0 mt-0.5">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1">
                        <p className={cn('text-sm font-medium', !notification.read && 'font-semibold')}>
                          {notification.title}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">{notification.message}</p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                        </p>
                      </div>
                      {!notification.read && (
                        <div className="h-2 w-2 rounded-full bg-primary mt-1 flex-shrink-0" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
          <div className="p-2 border-t">
            <Link
              to="/notifications"
              onClick={() => setIsOpen(false)}
              className="block w-full text-center text-sm text-primary hover:underline py-2"
            >
              View all notifications
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

