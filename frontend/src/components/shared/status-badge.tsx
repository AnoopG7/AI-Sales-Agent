import { cn } from "@/lib/utils"
import {
  LEAD_STATUSES,
  PROPERTY_STATUSES,
  MEETING_STATUSES,
} from "@/config/constants"
import type { LeadStatus, PropertyStatus, MeetingStatus } from "@/config/constants"

type StatusType = "lead" | "property" | "meeting"

const colorMap: Record<string, string> = {
  blue: "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
  yellow: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
  green: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
  purple: "bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-400",
  emerald: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400",
  red: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
  gray: "bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-400",
}

interface StatusBadgeProps {
  type: StatusType
  status: LeadStatus | PropertyStatus | MeetingStatus
  dot?: boolean
  className?: string
}

export function StatusBadge({ type, status, dot = true, className }: StatusBadgeProps) {
  let label: string
  let color: string

  if (type === "lead") {
    const config = LEAD_STATUSES[status as LeadStatus]
    label = config?.label ?? status
    color = colorMap[config?.color] ?? colorMap.gray
  } else if (type === "property") {
    const config = PROPERTY_STATUSES[status as PropertyStatus]
    label = config?.label ?? status
    color = colorMap[config?.color] ?? colorMap.gray
  } else {
    const config = MEETING_STATUSES[status as MeetingStatus]
    label = config?.label ?? status
    color = colorMap[config?.color] ?? colorMap.gray
  }

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium",
        color,
        className,
      )}
    >
      {dot && (
        <span className="size-1.5 rounded-full bg-current" aria-hidden="true" />
      )}
      {label}
    </span>
  )
}
