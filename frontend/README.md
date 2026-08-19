# Frontend — Admin Dashboard

React-based admin dashboard for managing leads, properties, meetings, and analytics. Connected to the backend API via Axios with auth token injection. Built with shadcn/ui components and a blue-themed OKLCH design system with light/dark mode. Currently in foundation phase — component library and design system are complete, pages are being built.

## Stack

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| Framework | React | 19 | Latest concurrent features |
| Bundler | Vite | 8 | Fast HMR, ESM native, sub-second rebuilds |
| Language | TypeScript | 6 | Strict mode, full type safety |
| Styling | Tailwind CSS | 4 | JIT compilation, OKLCH color space |
| UI Library | shadcn/ui + Radix | latest | Accessible headless primitives, customizable |
| Icons | Lucide React | latest | Clean SVG icon set (used in all nav) |
| Font | Geist Variable | 5 | Modern sans-serif by Vercel |
| Routing | React Router | 7 | Lazy-loaded routes, nested layouts |
| Forms | React Hook Form | 7.75 | Performant, minimal re-renders |
| Validation | Zod | 4 | Schema-based, TypeScript inference |
| State | Zustand | 5 | Lightweight hook-based stores, no boilerplate |
| API Client | Axios | 1.16 | Interceptors for auth token and 401 handling |
| Server State | TanStack Query | 5 | Caching, mutations, background refetch |
| Charts | Recharts | 3.8 | Composable React chart components |
| Calendar | react-day-picker | 10 | Accessible date picker with localization |
| Toasts | Sonner | 2 | Clean toast notifications with rich colors |
| Class Utils | clsx + tailwind-merge + CVA | — | Class merging and variant management |
| Linting | ESLint | 10 | Flat config with react-hooks and react-refresh |

## Features

### Design System

- **Full light/dark theme** with OKLCH color space — blue primary (light: 221 83% 53%, dark: 217 91% 60%)
- **Geist font** via @fontsource-variable/geist — modern, readable at all sizes
- **Gold accent** for Dubai real estate branding (used sparingly for highlights)
- **Custom CSS utilities**:
  - `.glass` — Frosted glass effect with backdrop-blur
  - `.glass-card` — Glassmorphism card with semi-transparent border
  - `.text-gradient` — Blue-to-purple gradient text
  - `.scrollbar-thin` — Thin custom scrollbar for all browsers
  - `.shimmer` — Loading shimmer animation
- **Theme persistence** via next-themes with system detection (light/dark/system)

### Component Library (25 shadcn/ui Primitives)

| Component | Purpose | Customizations |
|-----------|---------|----------------|
| Avatar | User avatar with fallback initials | Size variants (sm, md, lg) |
| Badge | Status labels | Color variants matching entity statuses |
| Button | All clickable actions | 6 variants: default, destructive, outline, secondary, ghost, link |
| Calendar | Date picking | Integrated with react-day-picker, disabled dates |
| Card | Content containers | Header, content, footer sub-components, hover lift |
| Command | Searchable command palette | cmdk-based, keyboard navigation |
| Dialog | Modal dialogs | Controlled open/close, nested scroll lock |
| DropdownMenu | Context menus | Sub-menus, checkbox items, separators |
| Input | Text inputs | Error state, disabled, icon slots |
| InputGroup | Labeled input with error | Label + input + error message composite |
| Label | Form labels | Error state styling |
| Popover | Floating overlays | Used for filters and date pickers |
| ScrollArea | Custom scroll containers | Thin styling, auto-hide |
| Select | Dropdown selects | Native select with custom arrow, error state |
| Separator | Visual dividers | Horizontal and vertical |
| Sheet | Slide-out panels | Used for mobile navigation and detail panels |
| Skeleton | Loading placeholders | Multiple shapes: text, card, circle |
| Sonner | Toast notifications | Rich colors, close buttons, position config |
| Switch | Toggle controls | Used for featured toggle, settings |
| Table | Data displays | Sortable, responsive with card fallback on mobile |
| Tabs | Tabbed interfaces | Used in settings, detail pages |
| Textarea | Multi-line input | Auto-resize, character count |
| Tooltip | Hover information | Delay config, positioning |

### Layout Components

| Component | Features |
|-----------|----------|
| AppShell | Responsive shell with sidebar (desktop) / sheet nav (mobile). Breakpoint: lg (1024px). Sidebar collapse/expand with smooth animation. |
| Sidebar | Collapsible sidebar with Lucide icons and labels. Active route highlighting in blue. Collapse to icon-only mode. Company logo at top. |
| Header | Breadcrumbs from route, global search input (placeholder), notifications bell with badge count (placeholder), theme switcher dropdown, user avatar with profile/logout dropdown. |
| MobileNav | Sheet-based drawer with navigation items. Opens via hamburger icon in header. Icons + labels in vertical list. |
| ThemeSwitcher | DropdownMenu with Sun/Moon/System icons. Animated transition on change. Persistent via localStorage. |

### Form Components

| Form | Fields | Validation |
|------|--------|------------|
| LeadForm | name, phone, email, status, source, budget_min, budget_max, property_type (select), bedrooms, location, notes | Zod: phone format, budget range, required name/phone |
| PropertyForm | title, description, price, property_type (select), bedrooms, bathrooms, area_sqft, location, amenities (multi-select), status, featured toggle | Zod: required title/price/location, price > 0 |
| MeetingForm | lead_id (searchable), scheduled_at (date picker), duration_minutes, timezone, notes | Zod: required lead_id + datetime, duration >= 15 |
| LoginForm | email, password | Zod: email format, password min 8 chars |
| SettingsForm | app_name, theme, timezone, currency, language | Zod: required name |

All forms use React Hook Form with Zod resolvers for real-time validation. Loading states during submission. Error messages displayed inline.

### Shared Components

| Component | Props | Behavior |
|-----------|-------|----------|
| DataTable | columns, data, total, page, pageSize, onPageChange, onSort, isLoading, emptyMessage | Generic sortable, paginated table. Responsive: card view on mobile. Skeleton loading. |
| PageHeader | title, description, action (ReactNode) | Page title with optional action button. Used consistently across all pages. |
| LoadingState | variant (spinner/skeleton/dots), text, fullPage | Three loading patterns. Skeleton for data, spinner for actions, dots for streaming. |
| EmptyState | icon, title, description, actionLabel, onAction | Empty data display with optional CTA. Used when filters return no results. |
| ErrorState | message, onRetry | Error display with retry button. Catches API failures. |
| ConfirmDialog | open, onConfirm, onCancel, title, description, confirmText, variant | Confirmation modal for destructive actions. Loading state on confirm. |
| SearchInput | value, onChange, placeholder, debounceMs (default 300) | Debounced search input with clear button. Default 300ms debounce. |
| Pagination | page, totalPages, onPageChange | Previous/next buttons + page numbers. Ellipsis for large page counts. |
| StatCard | label, value, icon, trend, trendValue, variant | Dashboard metric card with trend indicator. Hover lift animation. Variants: default/success/warning/danger. |
| StatusBadge | status, type (lead/property/meeting) | Color-coded badge matching entity status. Consistent color mapping across the app. |

### Color Mapping

**Lead Status Badges:**
- new: blue
- contacted: yellow/amber
- qualified: green
- meeting_scheduled: purple
- converted: emerald
- lost: red
- spam: gray

**Property Status Badges:**
- available: green
- sold: red
- rented: blue
- under_offer: orange
- archived: gray

**Meeting Status Badges:**
- scheduled: blue
- confirmed: green
- completed: slate
- cancelled: red
- no_show: orange

### State Management (Zustand)

| Store | State | Actions |
|-------|-------|---------|
| authStore | user, token, isAuthenticated, isLoading | setAuth(user, token), logout(), hydrate() |
| filterStore | statusFilter, sourceFilter, searchQuery, dateRange (leads); typeFilter, priceRange, bedroomsFilter, locationFilter, searchQuery (properties) | setLeadFilter, setPropertyFilter, resetFilters |
| sidebarStore | isCollapsed (desktop), isMobileOpen | toggleCollapse, setMobileOpen, setCollapsed |

### API Client (Axios)

```typescript
// api.ts
const api = axios.create({
  baseURL: "/api/v1",
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// Request interceptor: injects Authorization: Bearer <token> from localStorage
// Response interceptor: clears auth and redirects to /login on 401
```

Uses localStorage for token (not Zustand) to avoid circular dependencies during store initialization.

### TanStack Query Configuration

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,     // 5 minutes before refetch
      retry: 1,                       // Retry once on failure
    },
  },
});
```

### TypeScript Types

```typescript
// Core entity interfaces
Lead, Property, PropertyImage, Conversation, Message, Meeting, AdminUser

// Analytics
AnalyticsOverview, LeadOverTime, StatusBreakdown, SourceBreakdown

// API
PaginatedResponse<T>, ApiError
```

### Zod Validation Schemas

| Schema | Fields | Validations |
|--------|--------|-------------|
| leadFormSchema | name, phone, email, status, source, budget_min, budget_max, property_type, bedrooms, location, notes | phone: regex, budget: min/max coherence, required: name, phone |
| propertyFormSchema | title, description, price, property_type, bedrooms, bathrooms, area_sqft, location, amenities[], status, featured | required: title, price, location; price > 0 |
| meetingFormSchema | lead_id, scheduled_at, duration_minutes, timezone, notes | required: lead_id, scheduled_at; duration >= 15 |
| loginSchema | email, password | email format, password min 8 |
| signupSchema | name, email, password, confirm_password | password match, min 8 |
| settingsSchema | app_name, theme, timezone, currency, language | required: app_name |

### Constants

```typescript
// Entity statuses and sources
LEAD_STATUSES: string[]
LEAD_SOURCES: string[]
PROPERTY_TYPES: string[]
PROPERTY_STATUSES: string[]
MEETING_STATUSES: string[]

// Dubai areas (20 areas)
DUBAI_AREAS: string[]
// Dubai Marina, Downtown Dubai, Palm Jumeirah, Jumeirah Village Circle (JVC),
// Business Bay, Dubai Hills Estate, Arabian Ranches, Emirates Hills,
// Jumeirah Lakes Towers (JLT), Barsha Heights, City Walk, The Greens,
// Al Furjan, Dubai Silicon Oasis, Motor City, Damac Hills,
// Dubai South, Al Barari, Port de La Mer, Bluewaters

// Navigation items (7 items)
NAV_ITEMS: { icon, label, path, badge? }[]
// Dashboard, Leads, Properties, Meetings, Analytics, Settings
```

## Setup

### Prerequisites

- Node.js 20+
- npm 10+

### Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev
# -> http://localhost:5173

# Type check
npx tsc -b

# Lint
npm run lint

# Build for production
npm run build
# -> Output in dist/

# Preview production build
npm run preview
```

### API Proxy

Vite proxies /api -> http://localhost:8000. Axios uses relative baseURL /api/v1.

```typescript
// vite.config.ts
server: {
  proxy: {
    "/api": {
      target: "http://localhost:8000",
      changeOrigin: true,
    },
  },
}
```

## Future Pages (To Be Built)

| Path | Page | Components Needed |
|------|------|-------------------|
| /login | Login page | LoginForm (done), AuthLayout (done) |
| / | Dashboard | StatCard (done), Recharts, DataTable (done) |
| /leads | Lead list | DataTable (done), SearchInput (done), StatusBadge (done), PageHeader (done) |
| /leads/:id | Lead detail | Conversation log, activity timeline, edit sheet |
| /properties | Property grid/list | DataTable (done), SearchInput (done), PropertyForm (done) |
| /properties/new | Create property | PropertyForm (done) |
| /properties/:id | Property detail | Image gallery, full details, matched leads |
| /meetings | Calendar + list | MeetingForm (done), react-day-picker, list view |
| /analytics | Charts + date range | Recharts, StatCard (done) |
| /settings | Configuration | SettingsForm (done), tabs, integration configs |
