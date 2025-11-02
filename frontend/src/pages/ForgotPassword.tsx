import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'

export function ForgotPassword() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="space-y-1">
          <CardTitle className="text-2xl font-bold">Forgot Password</CardTitle>
          <CardDescription>
            Password reset functionality is not yet available
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">
              If you've forgotten your password, please contact your administrator
              to request a password reset. They will be able to assist you with
              recovering access to your account.
            </p>
            <p className="text-sm text-muted-foreground">
              Once password reset functionality is implemented, you'll be able to
              request a password reset link via email.
            </p>
          </div>
          
          <Button asChild className="w-full">
            <Link to="/login">Back to Login</Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}

