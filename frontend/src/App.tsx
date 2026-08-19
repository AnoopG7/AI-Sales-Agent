import { useEffect } from "react"
import { Toaster, TooltipProvider } from "@/components/ui"
import { ThemeProvider } from "@/components/layout"
import { useAuthStore } from "@/stores/authStore"
import { AppRouter } from "@/router"

export default function App() {
  const hydrate = useAuthStore((s) => s.hydrate)

  useEffect(() => {
    hydrate()
  }, [hydrate])

  return (
    <ThemeProvider defaultTheme="system" storageKey="leadgen-theme">
      <TooltipProvider>
        <AppRouter />
        <Toaster richColors position="top-right" />
      </TooltipProvider>
    </ThemeProvider>
  )
}
