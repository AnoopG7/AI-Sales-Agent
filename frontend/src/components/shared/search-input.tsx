import { useState, useRef, useEffect, useCallback } from "react"
import { cn } from "@/lib/utils"
import { Input } from "@/components/ui"
import { SearchIcon, XIcon } from "lucide-react"

interface SearchInputProps {
  value?: string
  onChange: (value: string) => void
  placeholder?: string
  debounceMs?: number
  className?: string
}

export function SearchInput({
  value: externalValue = "",
  onChange,
  placeholder = "Search...",
  debounceMs = 300,
  className,
}: SearchInputProps) {
  const [localValue, setLocalValue] = useState(externalValue)
  const [prevExternalValue, setPrevExternalValue] = useState(externalValue)
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  // Sync with external value changes (React-recommended derived state pattern)
  if (externalValue !== prevExternalValue) {
    setPrevExternalValue(externalValue)
    setLocalValue(externalValue)
  }

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
    }
  }, [])

  const debouncedOnChange = useCallback(
    (next: string) => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      timeoutRef.current = setTimeout(() => onChange(next), debounceMs)
    },
    [onChange, debounceMs],
  )

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const next = e.target.value
    setLocalValue(next)
    debouncedOnChange(next)
  }

  const handleClear = () => {
    setLocalValue("")
    if (timeoutRef.current) clearTimeout(timeoutRef.current)
    onChange("")
  }

  return (
    <div className={cn("relative", className)}>
      <SearchIcon className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
      <Input
        value={localValue}
        onChange={handleChange}
        placeholder={placeholder}
        className="h-8 rounded-lg pl-8 pr-8 text-sm"
      />
      {localValue && (
        <button
          onClick={handleClear}
          className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
          aria-label="Clear search"
        >
          <XIcon className="size-4" />
        </button>
      )}
    </div>
  )
}
