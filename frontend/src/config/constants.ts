/**
 * Application-wide constants.
 */

export const APP_NAME = "LeadGen"
export const APP_DESCRIPTION = "Dubai Real Estate Lead Generation & AI Automation"

/**
 * Lead status definitions with labels and colors.
 */
export const LEAD_STATUSES = {
  new: { label: "New", color: "blue" },
  contacted: { label: "Contacted", color: "yellow" },
  qualified: { label: "Qualified", color: "green" },
  meeting_scheduled: { label: "Meeting Scheduled", color: "purple" },
  converted: { label: "Converted", color: "emerald" },
  lost: { label: "Lost", color: "red" },
  spam: { label: "Spam", color: "gray" },
} as const

export type LeadStatus = keyof typeof LEAD_STATUSES

/**
 * Lead source definitions.
 */
export const LEAD_SOURCES = {
  meta_ads: { label: "Meta Ads", icon: "megaphone" },
  manual: { label: "Manual Entry", icon: "pen" },
  referral: { label: "Referral", icon: "users" },
  website: { label: "Website", icon: "globe" },
  other: { label: "Other", icon: "circle-dot" },
} as const

export type LeadSource = keyof typeof LEAD_SOURCES

/**
 * Property type definitions.
 */
export const PROPERTY_TYPES = {
  apartment: { label: "Apartment", icon: "building-2" },
  villa: { label: "Villa", icon: "home" },
  townhouse: { label: "Townhouse", icon: "warehouse" },
  penthouse: { label: "Penthouse", icon: "castle" },
  office: { label: "Office", icon: "briefcase" },
  commercial: { label: "Commercial", icon: "store" },
  land: { label: "Land", icon: "map" },
} as const

export type PropertyType = keyof typeof PROPERTY_TYPES

/**
 * Property status definitions.
 */
export const PROPERTY_STATUSES = {
  available: { label: "Available", color: "green" },
  sold: { label: "Sold", color: "red" },
  under_offer: { label: "Under Offer", color: "yellow" },
  coming_soon: { label: "Coming Soon", color: "blue" },
} as const

export type PropertyStatus = keyof typeof PROPERTY_STATUSES

/**
 * Meeting status definitions.
 */
export const MEETING_STATUSES = {
  scheduled: { label: "Scheduled", color: "blue" },
  completed: { label: "Completed", color: "green" },
  cancelled: { label: "Cancelled", color: "red" },
  rescheduled: { label: "Rescheduled", color: "yellow" },
} as const

export type MeetingStatus = keyof typeof MEETING_STATUSES

/**
 * Dubai areas for property location filtering.
 */
export const DUBAI_AREAS = [
  "Dubai Marina",
  "Downtown Dubai",
  "Palm Jumeirah",
  "JBR",
  "Business Bay",
  "DIFC",
  "Dubai Hills Estate",
  "Emirates Hills",
  "Arabian Ranches",
  "Jumeirah Village Circle (JVC)",
  "Dubai Creek Harbour",
  "Damac Hills",
  "Meydan",
  "Al Barsha",
  "Jumeirah Lakes Towers (JLT)",
  "Dubai Silicon Oasis",
  "Motor City",
  "Sports City",
  "City Walk",
  "Bluewaters Island",
] as const

/**
 * Sidebar navigation items.
 */
export const NAV_ITEMS = [
  { label: "Dashboard", href: "/", icon: "layout-dashboard" },
  { label: "Leads", href: "/leads", icon: "users" },
  { label: "Properties", href: "/properties", icon: "building-2" },
  { label: "Conversations", href: "/conversations", icon: "message-circle" },
  { label: "Meetings", href: "/meetings", icon: "calendar" },
  { label: "Analytics", href: "/analytics", icon: "bar-chart-3" },
  { label: "Settings", href: "/settings", icon: "settings" },
] as const
