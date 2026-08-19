import { Link, useLocation } from "react-router-dom"
import { NAV_ITEMS } from "@/config/constants"
import { NAV_ICON_MAP } from "./nav-icons"
import { useSidebarStore } from "@/stores/sidebarStore"
import { cn } from "@/lib/utils"
import { Button, Sheet, SheetContent, SheetHeader, SheetTitle } from "@/components/ui"

export function MobileNav() {
  const { isMobileOpen, setMobileOpen } = useSidebarStore()
  const location = useLocation()

  return (
    <Sheet open={isMobileOpen} onOpenChange={setMobileOpen}>
      <SheetContent side="left" className="w-[260px] p-0">
        <SheetHeader className="border-b px-4 py-3">
          <SheetTitle className="flex items-center gap-2">
            <span className="flex size-7 items-center justify-center rounded-lg bg-primary text-sm font-bold text-primary-foreground">
              S
            </span>
            <span className="font-heading font-semibold">LeadGen</span>
          </SheetTitle>
        </SheetHeader>
        <nav className="flex flex-col gap-1 p-2">
          {NAV_ITEMS.map((item) => {
            const Icon = NAV_ICON_MAP[item.icon]
            const isActive = location.pathname === item.href || (
              item.href !== "/" && location.pathname.startsWith(item.href)
            )

            return (
              <Button
                key={item.href}
                variant="ghost"
                asChild
                className={cn(
                  "justify-start gap-3 px-3",
                  isActive && "bg-primary/10 text-primary hover:bg-primary/15",
                )}
                onClick={() => setMobileOpen(false)}
              >
                <Link to={item.href}>
                  {Icon && <Icon className="size-5 shrink-0" />}
                  <span>{item.label}</span>
                </Link>
              </Button>
            )
          })}
        </nav>
      </SheetContent>
    </Sheet>
  )
}
