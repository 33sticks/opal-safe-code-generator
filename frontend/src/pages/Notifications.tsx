import { useState } from 'react'
import { useNotifications, useMarkAsRead } from '@/hooks/useApi'
import { Button } from '@/components/ui/button'
import { EmptyState } from '@/components/ui/EmptyState'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { Bell, Check, CheckCircle, XCircle, AlertCircle } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { cn } from '@/lib/utils'
import { useNavigate } from 'react-router-dom'

export function Notifications() {
  const [filter, setFilter] = useState<'all' | 'unread'>('all')
  const { data: notifications = [], isLoading, error } = useNotifications(filter === 'unread')
  const markAsRead = useMarkAsRead()
  const navigate = useNavigate()

  const handleMarkAsRead = async (id: number) => {
    try {
      await markAsRead.mutateAsync(id)
    } catch (error) {
      console.error('Failed to mark notification as read:', error)
    }
  }

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
      try {
        await markAsRead.mutateAsync(notification.id)
      } catch (error) {
        console.error('Failed to mark notification as read:', error)
      }
    }

    // Navigate based on notification type
    if (notification.type === 'code_needs_review') {
      // Admin notification - go to Generated Code page
      navigate('/generated-code');
    } else if (notification.type === 'code_approved' || notification.type === 'code_rejected') {
      // User notification - go to My Requests page
      navigate('/my-requests');
    }
  }

  const unreadNotifications = notifications?.filter(n => !n.read) || []

  if (isLoading) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <div className="space-y-6">
        <h1 className="text-2xl font-bold">Notifications</h1>
        <EmptyState
          icon={<Bell className="h-12 w-12 text-muted-foreground" />}
          title="Error loading notifications"
          description={error instanceof Error ? error.message : 'Failed to load notifications'}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Notifications</h1>
        {unreadNotifications.length > 0 && (
          <Button
            variant="outline"
            onClick={async () => {
              for (const notification of unreadNotifications) {
                await markAsRead.mutateAsync(notification.id)
              }
            }}
          >
            Mark all as read
          </Button>
        )}
      </div>

      <div className="flex gap-2 border-b">
        <button
          onClick={() => setFilter('all')}
          className={cn(
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
            filter === 'all'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          )}
        >
          All
        </button>
        <button
          onClick={() => setFilter('unread')}
          className={cn(
            'px-4 py-2 text-sm font-medium border-b-2 transition-colors',
            filter === 'unread'
              ? 'border-primary text-primary'
              : 'border-transparent text-muted-foreground hover:text-foreground'
          )}
        >
          Unread ({unreadNotifications.length})
        </button>
      </div>

      {!notifications || notifications.length === 0 ? (
        <EmptyState
          icon={<Bell className="h-12 w-12 text-muted-foreground" />}
          title="No notifications"
          description={
            filter === 'unread'
              ? 'You have no unread notifications'
              : 'You have no notifications yet'
          }
        />
      ) : (
        <div className="space-y-2">
          {notifications.map((notification) => {
            if (!notification) return null
            return (
            <div
              key={notification.id}
              className={cn(
                'rounded-lg border p-4 hover:bg-accent transition-colors cursor-pointer',
                !notification.read && 'bg-accent/50'
              )}
              onClick={() => handleNotificationClick(notification)}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getNotificationIcon(notification.type)}
                </div>
                <div className="flex-1">
                  <div className="flex items-start justify-between">
                    <h3 className={cn('text-sm font-medium', !notification.read && 'font-semibold')}>
                      {notification.title}
                    </h3>
                    {!notification.read && (
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleMarkAsRead(notification.id)
                        }}
                        className="h-6 px-2"
                      >
                        <Check className="h-4 w-4" />
                      </Button>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground mt-1">{notification.message}</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                  </p>
                </div>
              </div>
            </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

