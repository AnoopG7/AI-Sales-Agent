/**
 * Tailwind class merge utility.
 *
 * This file exists because shadcn/ui components import from "@/lib/utils".
 * See components.json → aliases.utils. App-specific helpers go in @/utils/.
 */

import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
