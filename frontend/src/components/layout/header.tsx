import { useLocation } from "react-router-dom"
import { NAV_ITEMS } from "@/config/constants"
import { useSidebarStore } from "@/stores/sidebarStore"
import { ThemeSwitcher } from "@/components/layout"
import { useAuthStore } from "@/stores/authStore"
import { Avatar, AvatarFallback, Button, Badge, Input, DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger } from "@/components/ui"
import { getInitials } from "@/utils"
import {
  MenuIcon,
  SearchIcon,
  BellIcon,
  LogOutIcon,
  UserIcon,
  SettingsIcon,
} from "lucide-react"

export function Header() {
  const location = useLocation()
  const { isMobileOpen, setMobileOpen } = useSidebarStore()
  const { user, logout } = useAuthStore()

  const currentPage = NAV_ITEMS.find(
    (item) => location.pathname === item.href || (
      item.href !== "/" && location.pathname.startsWith(item.href)
    ),
  )

  return (
    <header className="no-print flex h-14 items-center gap-4 border-b bg-background px-4 lg:px-6">
      {/* Mobile menu trigger */}
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={() => setMobileOpen(!isMobileOpen)}
        aria-label="Toggle navigation"
      >
        <MenuIcon className="size-5" />
      </Button>

      {/* Page title / breadcrumb */}
      <div className="flex items-center gap-2">
        <h1 className="font-heading text-base font-semibold text-foreground">
          {currentPage?.label ?? "Dashboard"}
        </h1>
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Search */}
      <div className="relative hidden md:block">
        <SearchIcon className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
        <Input
          placeholder="Search leads, products..."
          className="h-8 w-56 rounded-lg pl-8 text-sm lg:w-72"
        />
      </div>

      {/* Notifications */}
      <Button variant="ghost" size="icon" className="relative" aria-label="Notifications">
        <BellIcon className="size-4" />
        <Badge className="absolute -top-1 -right-1 flex size-4 items-center justify-center rounded-full p-0 text-[10px]">
          3
        </Badge>
      </Button>

      {/* Theme switcher */}
      <ThemeSwitcher />

      {/* User avatar */}
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="rounded-full" aria-label="User menu">
            <Avatar className="size-8">
              <AvatarFallback className="bg-primary/10 text-primary text-xs">
                {user ? getInitials(user.name) : "AD"}
              </AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-56">
          <DropdownMenuLabel>
            <div className="flex flex-col">
              <span className="text-sm font-medium">{user?.name ?? "Admin User"}</span>
              <span className="text-xs font-normal text-muted-foreground">{user?.email ?? "admin@example.com"}</span>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>
            <UserIcon className="mr-2 size-4" />
            Profile
          </DropdownMenuItem>
          <DropdownMenuItem>
            <SettingsIcon className="mr-2 size-4" />
            Settings
          </DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem onClick={logout} className="text-destructive">
            <LogOutIcon className="mr-2 size-4" />
            Log out
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  )
}
