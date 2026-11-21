import { Link, useLocation } from "react-router-dom"
import { cn } from "@/lib/utils"
import { NAV_ITEMS } from "@/config/constants"
import { NAV_ICON_MAP } from "./nav-icons"
import { useSidebarStore } from "@/stores/sidebarStore"
import { ChevronLeftIcon, ChevronRightIcon } from "lucide-react"

export function Sidebar() {
  const { isCollapsed, toggle } = useSidebarStore()
  const location = useLocation()

  return (
    <aside
      data-state={isCollapsed ? "collapsed" : "expanded"}
      className={cn(
        "no-print flex flex-col border-r bg-sidebar text-sidebar-foreground transition-all duration-200 ease-in-out",
        isCollapsed ? "w-16" : "w-60",
      )}
    >
      {/* Logo */}
      <div className={cn(
        "flex h-14 items-center border-b px-4",
        isCollapsed && "justify-center px-0",
      )}>
        {isCollapsed ? (
          <span className="text-lg font-bold text-sidebar-primary">S</span>
        ) : (
          <Link to="/" className="flex items-center gap-2">
            <span className="flex size-7 items-center justify-center rounded-lg bg-sidebar-primary text-sm font-bold text-sidebar-primary-foreground">
              S
            </span>
            <span className="font-heading text-base font-semibold">SalesAgent</span>
          </Link>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 overflow-y-auto p-2 scrollbar-thin">
        {NAV_ITEMS.map((item) => {
          const Icon = NAV_ICON_MAP[item.icon]
          const isActive = location.pathname === item.href || (
            item.href !== "/" && location.pathname.startsWith(item.href)
          )

          return (
            <Link
              key={item.href}
              to={item.href}
              data-active={isActive}
              className={cn(
                "group flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                "hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
                "data-[active=true]:bg-sidebar-primary data-[active=true]:text-sidebar-primary-foreground",
                isCollapsed && "justify-center px-2",
              )}
              title={isCollapsed ? item.label : undefined}
            >
              {Icon && <Icon className="size-5 shrink-0" />}
              {!isCollapsed && <span>{item.label}</span>}
            </Link>
          )
        })}
      </nav>

      {/* Collapse toggle */}
      <div className="border-t p-2">
        <button
          onClick={toggle}
          className={cn(
            "flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium text-muted-foreground transition-colors hover:bg-sidebar-accent hover:text-sidebar-accent-foreground",
            isCollapsed && "justify-center px-2",
          )}
          title={isCollapsed ? "Expand" : "Collapse"}
        >
          {isCollapsed ? (
            <ChevronRightIcon className="size-5 shrink-0" />
          ) : (
            <>
              <ChevronLeftIcon className="size-5 shrink-0" />
              <span>Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  )
}
