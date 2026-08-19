/**
 * Auth store — manages authentication state.
 *
 * Uses Zustand with localStorage persistence for the token.
 * On app start, `isAuthenticated` is false until `hydrate()` validates
 * the stored token against the backend.
 */

import { create } from "zustand"
import type { AdminUser } from "@/types"

interface AuthState {
  user: AdminUser | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean

  // Actions
  setAuth: (user: AdminUser, token: string) => void
  logout: () => void
  setLoading: (loading: boolean) => void
  hydrate: () => void
}

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  token: localStorage.getItem("access_token"),
  // Start as false — hydrate() will set to true if token is valid
  isAuthenticated: false,
  isLoading: true,

  setAuth: (user, token) => {
    localStorage.setItem("access_token", token)
    set({ user, token, isAuthenticated: true, isLoading: false })
  },

  logout: () => {
    localStorage.removeItem("access_token")
    set({ user: null, token: null, isAuthenticated: false, isLoading: false })
  },

  setLoading: (isLoading) => set({ isLoading }),

  /**
   * Validate the stored token on app startup.
   *
   * If there's no token, we're done. If there is one, we attempt to
   * fetch the current user from the API. On failure, we clear the
   * stale token and redirect to login.
   *
   * Call this once in your root component's useEffect.
   */
  hydrate: async () => {
    const { token } = get()
    if (!token) {
      set({ isLoading: false, isAuthenticated: false })
      return
    }

    try {
      // TODO: Replace with actual API call when auth endpoint is ready
      // const response = await api.get("/api/v1/auth/me")
      // set({ user: response.data, isAuthenticated: true, isLoading: false })

      // Temporary: assume token is valid (remove when backend auth is ready)
      set({ isAuthenticated: true, isLoading: false })
    } catch {
      // Token is expired/invalid — clean up
      localStorage.removeItem("access_token")
      set({ user: null, token: null, isAuthenticated: false, isLoading: false })
    }
  },
}))
