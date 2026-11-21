import { Outlet } from "react-router-dom"
import { ThemeSwitcher } from "@/components/layout"

export function AuthLayout() {
  return (
    <div className="relative flex min-h-screen items-center justify-center bg-gradient-to-br from-background via-muted/30 to-background p-4">
      {/* Theme switcher */}
      <div className="fixed top-4 right-4">
        <ThemeSwitcher />
      </div>

      {/* Card */}
      <div className="w-full max-w-sm">
        <div className="mb-8 text-center">
          <div className="mx-auto mb-4 flex size-12 items-center justify-center rounded-xl bg-primary">
            <span className="text-lg font-bold text-primary-foreground">S</span>
          </div>
          <h1 className="font-heading text-xl font-bold text-foreground">SalesAgent</h1>
          <p className="mt-1 text-sm text-muted-foreground">
            Lead Generation Dashboard
          </p>
        </div>

        <div className="rounded-xl border bg-card p-6 shadow-sm">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
