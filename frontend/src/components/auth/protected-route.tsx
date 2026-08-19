import { Navigate, Outlet, useLocation } from "react-router-dom"
import { useAuthStore } from "@/stores/authStore"
import { LoadingState } from "@/components/shared"

export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuthStore()
  const location = useLocation()

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <LoadingState variant="spinner" text="Authenticating..." />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  return <Outlet />
}
