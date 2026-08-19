/**
 * Filter store — persists table/list filter state across navigation.
 */

import { create } from "zustand"
import type { LeadStatus, LeadSource } from "@/config/constants"

interface FilterState {
  // Lead filters
  leadStatusFilter: LeadStatus[]
  leadSourceFilter: LeadSource[]
  leadSearchQuery: string
  leadDateRange: { from: string | null; to: string | null }

  // Property filters
  propertyTypeFilter: string[]
  propertyPriceRange: { min: number | null; max: number | null }
  propertyBedroomsFilter: number | null
  propertyLocationFilter: string[]
  propertySearchQuery: string

  // Actions
  setLeadStatusFilter: (statuses: LeadStatus[]) => void
  setLeadSourceFilter: (sources: LeadSource[]) => void
  setLeadSearchQuery: (query: string) => void
  setLeadDateRange: (range: { from: string | null; to: string | null }) => void
  setPropertyTypeFilter: (types: string[]) => void
  setPropertyPriceRange: (range: { min: number | null; max: number | null }) => void
  setPropertyBedroomsFilter: (bedrooms: number | null) => void
  setPropertyLocationFilter: (locations: string[]) => void
  setPropertySearchQuery: (query: string) => void
  resetLeadFilters: () => void
  resetPropertyFilters: () => void
}

export const useFilterStore = create<FilterState>((set) => ({
  // Lead defaults
  leadStatusFilter: [],
  leadSourceFilter: [],
  leadSearchQuery: "",
  leadDateRange: { from: null, to: null },

  // Property defaults
  propertyTypeFilter: [],
  propertyPriceRange: { min: null, max: null },
  propertyBedroomsFilter: null,
  propertyLocationFilter: [],
  propertySearchQuery: "",

  // Lead actions
  setLeadStatusFilter: (leadStatusFilter) => set({ leadStatusFilter }),
  setLeadSourceFilter: (leadSourceFilter) => set({ leadSourceFilter }),
  setLeadSearchQuery: (leadSearchQuery) => set({ leadSearchQuery }),
  setLeadDateRange: (leadDateRange) => set({ leadDateRange }),

  // Property actions
  setPropertyTypeFilter: (propertyTypeFilter) => set({ propertyTypeFilter }),
  setPropertyPriceRange: (propertyPriceRange) => set({ propertyPriceRange }),
  setPropertyBedroomsFilter: (propertyBedroomsFilter) => set({ propertyBedroomsFilter }),
  setPropertyLocationFilter: (propertyLocationFilter) => set({ propertyLocationFilter }),
  setPropertySearchQuery: (propertySearchQuery) => set({ propertySearchQuery }),

  // Reset
  resetLeadFilters: () =>
    set({
      leadStatusFilter: [],
      leadSourceFilter: [],
      leadSearchQuery: "",
      leadDateRange: { from: null, to: null },
    }),
  resetPropertyFilters: () =>
    set({
      propertyTypeFilter: [],
      propertyPriceRange: { min: null, max: null },
      propertyBedroomsFilter: null,
      propertyLocationFilter: [],
      propertySearchQuery: "",
    }),
}))
