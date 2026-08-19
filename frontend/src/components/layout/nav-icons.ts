/**
 * Icon map for navigation items.
 *
 * Maps the string icon names in NAV_ITEMS to actual Lucide components.
 * Shared by Sidebar and MobileNav to avoid duplication.
 */

import {
  LayoutDashboardIcon,
  UsersIcon,
  Building2Icon,
  MessageCircleIcon,
  CalendarIcon,
  BarChart3Icon,
  SettingsIcon,
} from "lucide-react"
import type { LucideIcon } from "lucide-react"

export const NAV_ICON_MAP: Record<string, LucideIcon> = {
  "layout-dashboard": LayoutDashboardIcon,
  "users": UsersIcon,
  "building-2": Building2Icon,
  "message-circle": MessageCircleIcon,
  "calendar": CalendarIcon,
  "bar-chart-3": BarChart3Icon,
  "settings": SettingsIcon,
}
