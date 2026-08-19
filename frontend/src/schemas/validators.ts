/**
 * Zod validation schemas.
 *
 * These are the single source of truth for form validation
 * and API request/response shapes. Used with React Hook Form.
 */

import { z } from "zod"

// --- Lead Schemas ---

export const leadFormSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  phone: z
    .string()
    .min(10, "Phone number must be at least 10 digits")
    .regex(/^\+?[0-9\s-]+$/, "Invalid phone number format"),
  email: z.string().email("Invalid email address").optional().or(z.literal("")),
  status: z.enum(["new", "contacted", "qualified", "meeting_scheduled", "converted", "lost", "spam"]).default("new"),
  source: z.enum(["meta_ads", "manual", "referral", "website", "other"]).default("manual"),
  budget_min: z.coerce.number().min(0).optional(),
  budget_max: z.coerce.number().min(0).optional(),
  preferred_type: z.enum(["apartment", "villa", "townhouse", "penthouse", "office", "commercial", "land"]).optional(),
  preferred_location: z.string().optional(),
  preferred_bedrooms: z.coerce.number().min(0).max(20).optional(),
  notes: z.string().optional(),
})

export type LeadFormData = z.infer<typeof leadFormSchema>

// --- Property Schemas ---

export const propertyFormSchema = z.object({
  title: z.string().min(5, "Title must be at least 5 characters"),
  description: z.string().min(20, "Description must be at least 20 characters"),
  price: z.coerce.number().positive("Price must be positive"),
  type: z.enum(["apartment", "villa", "townhouse", "penthouse", "office", "commercial", "land"]),
  location: z.string().min(2, "Location is required"),
  bedrooms: z.coerce.number().min(0).max(20).default(0),
  bathrooms: z.coerce.number().min(0).max(20).default(0),
  area_sqft: z.coerce.number().positive("Area must be positive"),
  amenities: z.array(z.string()).default([]),
  status: z.enum(["available", "sold", "under_offer", "coming_soon"]).default("available"),
  featured: z.boolean().default(false),
})

export type PropertyFormData = z.infer<typeof propertyFormSchema>

// --- Meeting Schemas ---

export const meetingFormSchema = z.object({
  lead_id: z.string().uuid("Invalid lead ID"),
  scheduled_at: z.string().min(1, "Date and time are required"),
  duration_minutes: z.coerce.number().min(15).max(120).default(30),
  notes: z.string().optional(),
})

export type MeetingFormData = z.infer<typeof meetingFormSchema>

// --- Auth Schemas ---

export const loginSchema = z.object({
  email: z.string().email("Invalid email address"),
  password: z.string().min(8, "Password must be at least 8 characters"),
})

export type LoginFormData = z.infer<typeof loginSchema>

export const signupSchema = loginSchema.extend({
  name: z.string().min(2, "Name must be at least 2 characters"),
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: "Passwords don't match",
  path: ["confirmPassword"],
})

export type SignupFormData = z.infer<typeof signupSchema>

// --- Settings Schemas ---

export const settingsSchema = z.object({
  company_name: z.string().min(2),
  admin_email: z.string().email(),
  admin_whatsapp: z.string().min(10),
  ai_model: z.string().default("gpt-4o-mini"),
  ai_temperature: z.coerce.number().min(0).max(2).default(0.7),
  business_hours_start: z.string().default("09:00"),
  business_hours_end: z.string().default("19:00"),
  timezone: z.string().default("Asia/Dubai"),
})

export type SettingsFormData = z.infer<typeof settingsSchema>
