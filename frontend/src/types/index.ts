/**
 * Core TypeScript interfaces for the application.
 *
 * These mirror the Supabase database schema and are used
 * throughout the frontend for type safety.
 */

// --- Lead ---

export interface Lead {
  id: string
  phone: string
  name: string | null
  email: string | null
  whatsapp_id: string | null
  status: "new" | "contacted" | "qualified" | "meeting_scheduled" | "converted" | "lost" | "spam"
  source: "meta_ads" | "manual" | "referral" | "website" | "other"
  budget_min: number | null
  budget_max: number | null
  preferred_type: string | null
  preferred_location: string | null
  preferred_bedrooms: number | null
  conversation_stage: string | null
  notes: string | null
  metadata: Record<string, unknown>
  assigned_to: string | null
  last_contacted_at: string | null
  created_at: string
  updated_at: string
}

// --- Property ---

export interface Property {
  id: string
  title: string
  description: string | null
  type: "apartment" | "villa" | "townhouse" | "penthouse" | "office" | "commercial" | "land"
  location: string
  price: number
  bedrooms: number
  bathrooms: number
  area_sqft: number | null
  amenities: string[]
  images: PropertyImage[]
  status: "available" | "sold" | "under_offer" | "coming_soon"
  featured: boolean
  metadata: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface PropertyImage {
  url: string
  alt: string
  order: number
}

// --- Conversation & Messages ---

export interface Conversation {
  id: string
  lead_id: string
  status: "active" | "closed"
  started_at: string
  ended_at: string | null
  summary: string | null
  lead?: Lead
}

export interface Message {
  id: string
  conversation_id: string
  role: "user" | "assistant" | "system"
  content: string
  message_type: "text" | "image" | "interactive" | "template"
  whatsapp_message_id: string | null
  metadata: Record<string, unknown>
  created_at: string
}

// --- Meeting ---

export interface Meeting {
  id: string
  lead_id: string
  scheduled_at: string
  duration_minutes: number
  timezone: string
  google_event_id: string | null
  meet_link: string | null
  status: "scheduled" | "completed" | "cancelled" | "rescheduled"
  notes: string | null
  created_at: string
  updated_at: string
  lead?: Lead
}

// --- Admin User ---

export interface AdminUser {
  id: string
  email: string
  name: string
  role: "admin" | "agent" | "viewer"
  created_at: string
}

// --- Analytics ---

export interface AnalyticsOverview {
  total_leads: number
  total_leads_today: number
  qualified_leads: number
  meetings_scheduled: number
  meetings_this_week: number
  conversion_rate: number
  avg_response_time_minutes: number
}

export interface LeadOverTime {
  date: string
  count: number
}

export interface StatusBreakdown {
  status: string
  count: number
  percentage: number
}

export interface SourceBreakdown {
  source: string
  count: number
  percentage: number
}

// --- API Response ---

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ApiError {
  error: true
  message: string
  detail: Record<string, unknown>
}
