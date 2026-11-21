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

  // Product filters
  productCategoryFilter: string[]
  productPriceRange: { min: number | null; max: number | null }
  productTeamSizeFilter: number | null
  productStatusFilter: string[]
  productSearchQuery: string

  // Actions
  setLeadStatusFilter: (statuses: LeadStatus[]) => void
  setLeadSourceFilter: (sources: LeadSource[]) => void
  setLeadSearchQuery: (query: string) => void
  setLeadDateRange: (range: { from: string | null; to: string | null }) => void
  setProductCategoryFilter: (categories: string[]) => void
  setProductPriceRange: (range: { min: number | null; max: number | null }) => void
  setProductTeamSizeFilter: (teamSize: number | null) => void
  setProductStatusFilter: (statuses: string[]) => void
  setProductSearchQuery: (query: string) => void
  resetLeadFilters: () => void
  resetProductFilters: () => void
}

export const useFilterStore = create<FilterState>((set) => ({
  // Lead defaults
  leadStatusFilter: [],
  leadSourceFilter: [],
  leadSearchQuery: "",
  leadDateRange: { from: null, to: null },

  // Product defaults
  productCategoryFilter: [],
  productPriceRange: { min: null, max: null },
  productTeamSizeFilter: null,
  productStatusFilter: [],
  productSearchQuery: "",

  // Lead actions
  setLeadStatusFilter: (leadStatusFilter) => set({ leadStatusFilter }),
  setLeadSourceFilter: (leadSourceFilter) => set({ leadSourceFilter }),
  setLeadSearchQuery: (leadSearchQuery) => set({ leadSearchQuery }),
  setLeadDateRange: (leadDateRange) => set({ leadDateRange }),

  // Product actions
  setProductCategoryFilter: (productCategoryFilter) => set({ productCategoryFilter }),
  setProductPriceRange: (productPriceRange) => set({ productPriceRange }),
  setProductTeamSizeFilter: (productTeamSizeFilter) => set({ productTeamSizeFilter }),
  setProductStatusFilter: (productStatusFilter) => set({ productStatusFilter }),
  setProductSearchQuery: (productSearchQuery) => set({ productSearchQuery }),

  // Reset
  resetLeadFilters: () =>
    set({
      leadStatusFilter: [],
      leadSourceFilter: [],
      leadSearchQuery: "",
      leadDateRange: { from: null, to: null },
    }),
  resetProductFilters: () =>
    set({
      productCategoryFilter: [],
      productPriceRange: { min: null, max: null },
      productTeamSizeFilter: null,
      productStatusFilter: [],
      productSearchQuery: "",
    }),
}))
