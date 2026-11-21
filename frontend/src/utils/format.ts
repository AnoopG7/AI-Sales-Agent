/**
 * Formatting & helper utilities.
 *
 * Application-specific helpers that are NOT tied to shadcn/ui.
 * Import from "@/utils/format" or via the "@/utils" barrel.
 */

import { DEFAULT_CURRENCY } from "@/config/constants"

/**
 * Format a number as a price with its currency code.
 * e.g. 2500000 → "USD 2.5M", 39 → "USD 39"
 */
export function formatPrice(amount: number, currency: string = DEFAULT_CURRENCY): string {
  if (amount >= 1_000_000) {
    const millions = amount / 1_000_000
    return `${currency} ${millions % 1 === 0 ? millions.toFixed(0) : millions.toFixed(1)}M`
  }
  return `${currency} ${amount.toLocaleString()}`
}

/**
 * Format a date as relative time (e.g. "2 hours ago").
 */
export function formatRelativeTime(date: Date | string): string {
  const now = new Date()
  const target = typeof date === "string" ? new Date(date) : date
  const diffMs = now.getTime() - target.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  const diffHours = Math.floor(diffMs / 3600000)
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffMins < 1) return "Just now"
  if (diffMins < 60) return `${diffMins}m ago`
  if (diffHours < 24) return `${diffHours}h ago`
  if (diffDays < 7) return `${diffDays}d ago`
  return target.toLocaleDateString()
}

/**
 * Truncate a string with ellipsis.
 */
export function truncate(str: string, maxLength: number = 100): string {
  if (str.length <= maxLength) return str
  return str.slice(0, maxLength - 3) + "..."
}

/**
 * Generate initials from a name (e.g. "Jordan Lee" → "JL").
 */
export function getInitials(name: string): string {
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}

/**
 * Format a date in the user's locale and timezone.
 */
export function formatDate(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date
  return d.toLocaleDateString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
  })
}

/**
 * Format a date and time in the user's locale and timezone.
 */
export function formatDateTime(date: Date | string): string {
  const d = typeof date === "string" ? new Date(date) : date
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}
