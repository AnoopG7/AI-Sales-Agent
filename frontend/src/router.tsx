import { lazy, Suspense } from "react"
import { Routes, Route } from "react-router-dom"
import { LoadingState } from "@/components/shared"
import { DashboardLayout } from "@/layouts"

const Homepage = lazy(() => import("@/pages/homepage"))

function PageLoader() {
  return (
    <div className="flex min-h-[60vh] items-center justify-center">
      <LoadingState variant="spinner" text="Loading..." />
    </div>
  )
}

export function AppRouter() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Homepage />} />
        </Route>
      </Routes>
    </Suspense>
  )
}
