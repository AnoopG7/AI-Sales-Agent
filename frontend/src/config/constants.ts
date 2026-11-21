/**
 * Application-wide constants.
 */

export const APP_NAME = "SalesAgent"
export const APP_DESCRIPTION = "AI sales agent for lead qualification and demo booking"

/** Currency the product catalog is priced in (matches backend DEFAULT_CURRENCY). */
export const DEFAULT_CURRENCY = "USD"

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
 * Product category definitions.
 */
export const PRODUCT_CATEGORIES = {
  crm: { label: "CRM", icon: "users" },
  analytics: { label: "Analytics", icon: "bar-chart-3" },
  automation: { label: "Automation", icon: "workflow" },
  support: { label: "Support", icon: "life-buoy" },
  add_on: { label: "Add-on", icon: "puzzle" },
} as const

export type ProductCategory = keyof typeof PRODUCT_CATEGORIES

/**
 * Billing period definitions.
 */
export const BILLING_PERIODS = {
  monthly: { label: "Monthly", suffix: "/seat/mo" },
  annual: { label: "Annual", suffix: "/seat/yr" },
  one_time: { label: "One-time", suffix: " one-time" },
} as const

export type BillingPeriod = keyof typeof BILLING_PERIODS

/**
 * Product status definitions.
 */
export const PRODUCT_STATUSES = {
  active: { label: "Active", color: "green" },
  beta: { label: "Beta", color: "blue" },
  deprecated: { label: "Deprecated", color: "yellow" },
  archived: { label: "Archived", color: "gray" },
} as const

export type ProductStatus = keyof typeof PRODUCT_STATUSES

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
 * Team-size bands for filtering leads and products.
 */
export const TEAM_SIZE_BANDS = [
  { label: "1-10", min: 1, max: 10 },
  { label: "11-50", min: 11, max: 50 },
  { label: "51-200", min: 51, max: 200 },
  { label: "200+", min: 201, max: null },
] as const

/**
 * Sidebar navigation items.
 */
export const NAV_ITEMS = [
  { label: "Dashboard", href: "/", icon: "layout-dashboard" },
  { label: "Leads", href: "/leads", icon: "users" },
  { label: "Products", href: "/products", icon: "package" },
  { label: "Conversations", href: "/conversations", icon: "message-circle" },
  { label: "Meetings", href: "/meetings", icon: "calendar" },
  { label: "Analytics", href: "/analytics", icon: "bar-chart-3" },
  { label: "Settings", href: "/settings", icon: "settings" },
] as const
