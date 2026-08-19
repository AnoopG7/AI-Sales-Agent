/**
 * Axios API client with interceptors.
 *
 * - Automatically injects auth token from Zustand store
 * - Handles 401 responses by clearing auth state
 * - Provides typed request helpers
 */

import axios, { type AxiosError, type AxiosResponse } from "axios"
import type { ApiError } from "@/types"

const api = axios.create({
  baseURL: "/api/v1",
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
})

// --- Request Interceptor: Inject Auth Token ---
api.interceptors.request.use(
  (config) => {
    // Token will be set from Zustand auth store
    const token = localStorage.getItem("access_token")
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

// --- Response Interceptor: Handle Errors ---
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error: AxiosError<ApiError>) => {
    if (error.response?.status === 401) {
      // Clear auth and redirect to login
      localStorage.removeItem("access_token")
      window.location.href = "/login"
    }
    return Promise.reject(error)
  },
)

export default api
