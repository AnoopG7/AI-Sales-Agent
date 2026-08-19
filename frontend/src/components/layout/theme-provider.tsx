/**
 * Theme provider component.
 *
 * Manages light/dark/system theme preference with localStorage persistence
 * and applies the appropriate class to the document root.
 */

import { useEffect, useState, type ReactNode } from "react"
import { ThemeProviderContext, type Theme } from "./theme-context"

interface ThemeProviderProps {
  children: ReactNode
  defaultTheme?: Theme
  storageKey?: string
}

function getSystemTheme(): "dark" | "light" {
  if (typeof window === "undefined") return "light"
  return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
}

export function ThemeProvider({
  children,
  defaultTheme = "system",
  storageKey = "leadgen-theme",
}: ThemeProviderProps) {
  const [theme, setThemeState] = useState<Theme>(
    () => (localStorage.getItem(storageKey) as Theme) || defaultTheme,
  )

  const resolvedTheme = theme === "system" ? getSystemTheme() : theme

  useEffect(() => {
    const root = window.document.documentElement

    // Add transition class for smooth theme switch
    root.classList.add("transitioning")

    root.classList.remove("light", "dark")
    root.classList.add(resolvedTheme)

    // Remove transition class after animation completes
    const timeout = setTimeout(() => {
      root.classList.remove("transitioning")
    }, 350)

    return () => clearTimeout(timeout)
  }, [resolvedTheme])

  // Listen for system theme changes
  useEffect(() => {
    if (theme !== "system") return

    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")
    const handler = () => {
      const root = window.document.documentElement
      root.classList.remove("light", "dark")
      root.classList.add(getSystemTheme())
    }

    mediaQuery.addEventListener("change", handler)
    return () => mediaQuery.removeEventListener("change", handler)
  }, [theme])

  const setTheme = (newTheme: Theme) => {
    localStorage.setItem(storageKey, newTheme)
    setThemeState(newTheme)
  }

  return (
    <ThemeProviderContext.Provider value={{ theme, resolvedTheme, setTheme }}>
      {children}
    </ThemeProviderContext.Provider>
  )
}


