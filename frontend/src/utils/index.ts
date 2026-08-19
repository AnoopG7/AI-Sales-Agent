/**
 * Utils barrel — single import point for all utilities.
 *
 * Usage: import { cn, getInitials, formatPriceAED } from "@/utils"
 *
 * Note: cn() lives in @/lib/utils (required by shadcn).
 * We re-export it here for convenience so you can import everything from one place.
 */
export { cn } from "@/lib/utils"
export {
  formatPriceAED,
  formatRelativeTime,
  formatDateDubai,
  formatDateTimeDubai,
  truncate,
  getInitials,
} from "./format"
