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
  company: z.string().optional(),
  team_size: z.coerce.number().int().min(1).max(100000).optional(),
  product_interest: z.string().optional(),
  notes: z.string().optional(),
})

export type LeadFormData = z.infer<typeof leadFormSchema>

// --- Product Schemas ---

export const productFormSchema = z
  .object({
    name: z.string().min(2, "Name must be at least 2 characters"),
    description: z.string().min(10, "Description must be at least 10 characters"),
    category: z.enum(["crm", "analytics", "automation", "support", "add_on"]),
    price: z.coerce.number().min(0, "Price can't be negative"),
    billing_period: z.enum(["monthly", "annual", "one_time"]).default("monthly"),
    min_seats: z.coerce.number().int().min(1).default(1),
    max_seats: z.coerce.number().int().min(1).optional(),
    features: z.array(z.string()).default([]),
    status: z.enum(["active", "beta", "deprecated", "archived"]).default("active"),
    featured: z.boolean().default(false),
  })
  .refine((d) => d.max_seats === undefined || d.max_seats >= d.min_seats, {
    message: "Max seats must be at least min seats",
    path: ["max_seats"],
  })

export type ProductFormData = z.infer<typeof productFormSchema>

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
  timezone: z.string().default("UTC"),
})

export type SettingsFormData = z.infer<typeof settingsSchema>
