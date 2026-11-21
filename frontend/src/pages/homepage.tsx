import { useState } from "react"
import {
  PageHeader, StatCard, StatusBadge, DataTable,
  EmptyState, ErrorState, LoadingState, SearchInput,
  Pagination, ConfirmDialog,
} from "@/components/shared"
import type { Column } from "@/components/shared"
import {
  Button, Badge, Card, CardContent, CardDescription,
  CardHeader, CardTitle, Tabs, TabsContent, TabsList,
  TabsTrigger, Separator,
} from "@/components/ui"
import { LoginForm, LeadForm, ProductForm, MeetingForm, SettingsForm } from "@/components/forms"
import {
  UsersIcon,
  PackageIcon,
  CalendarIcon,
  TrendingUpIcon,
  PlusIcon,
  DownloadIcon,
  InboxIcon,
  SearchIcon,
} from "lucide-react"
import { toast } from "sonner"

/* ─── Sample Data ─── */
interface SampleLead {
  id: string
  name: string
  phone: string
  status: "new" | "contacted" | "qualified" | "meeting_scheduled" | "converted" | "lost" | "spam"
  source: "meta_ads" | "manual" | "referral" | "website" | "other"
  budget: string
  created: string
}

const sampleLeads: SampleLead[] = [
  { id: "1", name: "Jordan Lee", phone: "+1 415 555 0132", status: "qualified", source: "meta_ads", budget: "USD 1,000-1,500/mo", created: "2h ago" },
  { id: "2", name: "Priya Nair", phone: "+44 20 7946 0958", status: "new", source: "website", budget: "USD 500/mo", created: "30m ago" },
  { id: "3", name: "Marcus Chen", phone: "+65 6123 4567", status: "meeting_scheduled", source: "referral", budget: "USD 3-5K/mo", created: "1d ago" },
  { id: "4", name: "Sofia Alvarez", phone: "+34 912 345 678", status: "converted", source: "meta_ads", budget: "USD 2,000/mo", created: "3d ago" },
  { id: "5", name: "Daniel Okafor", phone: "+234 1 234 5678", status: "lost", source: "manual", budget: "USD 10K+/mo", created: "5d ago" },
]

const leadColumns: Column<SampleLead>[] = [
  { key: "name", header: "Name", sortable: true },
  { key: "phone", header: "Phone" },
  {
    key: "status",
    header: "Status",
    render: (lead) => <StatusBadge type="lead" status={lead.status} />,
  },
  {
    key: "source",
    header: "Source",
    render: (lead) => <Badge variant="secondary" className="text-xs">{lead.source}</Badge>,
  },
  { key: "budget", header: "Budget" },
  { key: "created", header: "Created" },
]

export default function Homepage() {
  const [searchValue, setSearchValue] = useState("")
  const [confirmOpen, setConfirmOpen] = useState(false)
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)

  return (
    <div className="space-y-8">
      {/* ─── Page Header ─── */}
      <PageHeader
        title="UI Component Showcase"
        description="A comprehensive overview of all available components."
        actions={
          <>
            <Button variant="outline" size="sm">
              <DownloadIcon className="mr-1.5 size-3.5" />
              Export
            </Button>
            <Button size="sm">
              <PlusIcon className="mr-1.5 size-3.5" />
              Add New
            </Button>
          </>
        }
      />

      <Separator />

      {/* ─── Stat Cards ─── */}
      <section className="space-y-3">
        <h2 className="font-heading text-lg font-semibold">Stat Cards</h2>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Total Leads"
            value="1,247"
            description="+12% from last month"
            icon={<UsersIcon className="size-5" />}
            trend="up"
            trendValue="12%"
          />
          <StatCard
            title="Products"
            value="11"
            description="10 active"
            icon={<PackageIcon className="size-5" />}
            trend="neutral"
            trendValue="Same"
          />
          <StatCard
            title="Meetings"
            value="23"
            description="8 this week"
            icon={<CalendarIcon className="size-5" />}
            trend="up"
            trendValue="+5"
          />
          <StatCard
            title="Conversion"
            value="18.5%"
            description="+2.3% improvement"
            icon={<TrendingUpIcon className="size-5" />}
            trend="up"
            trendValue="2.3%"
            variant="gradient"
          />
        </div>
      </section>

      {/* ─── Status Badges ─── */}
      <section className="space-y-3">
        <h2 className="font-heading text-lg font-semibold">Status Badges</h2>
        <div className="flex flex-wrap items-center gap-2">
          <StatusBadge type="lead" status="new" />
          <StatusBadge type="lead" status="contacted" />
          <StatusBadge type="lead" status="qualified" />
          <StatusBadge type="lead" status="meeting_scheduled" />
          <StatusBadge type="lead" status="converted" />
          <StatusBadge type="lead" status="lost" />
          <StatusBadge type="lead" status="spam" />
          <Separator orientation="vertical" className="h-5" />
          <StatusBadge type="product" status="active" />
          <StatusBadge type="product" status="beta" />
          <StatusBadge type="product" status="deprecated" />
          <StatusBadge type="product" status="archived" />
          <Separator orientation="vertical" className="h-5" />
          <StatusBadge type="meeting" status="scheduled" />
          <StatusBadge type="meeting" status="completed" />
          <StatusBadge type="meeting" status="cancelled" />
          <StatusBadge type="meeting" status="rescheduled" />
          {/* Dotless variant */}
          <StatusBadge type="lead" status="qualified" dot={false} />
        </div>
      </section>

      {/* ─── Badges ─── */}
      <section className="space-y-3">
        <h2 className="font-heading text-lg font-semibold">Badges</h2>
        <div className="flex flex-wrap items-center gap-2">
          <Badge>Default</Badge>
          <Badge variant="secondary">Secondary</Badge>
          <Badge variant="destructive">Destructive</Badge>
          <Badge variant="outline">Outline</Badge>
          <Badge variant="ghost">Ghost</Badge>
          <Badge variant="link">Link</Badge>
        </div>
      </section>

      {/* ─── Buttons ─── */}
      <section className="space-y-3">
        <h2 className="font-heading text-lg font-semibold">Buttons</h2>
        <div className="flex flex-wrap items-center gap-2">
          <Button variant="default">Default</Button>
          <Button variant="outline">Outline</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="destructive">Destructive</Button>
          <Button variant="link">Link</Button>
          <Button disabled>Disabled</Button>
          <Button size="xs">XS</Button>
          <Button size="sm">SM</Button>
          <Button size="lg">LG</Button>
          <Button size="icon" aria-label="Search"><SearchIcon className="size-4" /></Button>
        </div>
      </section>

      {/* ─── Data Table ─── */}
      <section className="space-y-3">
        <h2 className="font-heading text-lg font-semibold">Data Table</h2>
        <DataTable
          columns={leadColumns}
          data={sampleLeads}
          rowKey={(row) => row.id}
          onRowClick={(row) => toast(`Clicked lead: ${row.name}`)}
        />
      </section>

      {/* ─── Empty / Error / Loading States ─── */}
      <section className="space-y-3">
        <h2 className="font-heading text-lg font-semibold">States</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <EmptyState
            icon={<InboxIcon className="size-8" />}
            title="No leads yet"
            description="Leads from WhatsApp will appear here automatically."
            action={<Button size="sm"><PlusIcon className="mr-1.5 size-3.5" />Add Lead</Button>}
          />
          <ErrorState onRetry={() => toast("Retrying...")} />
          <LoadingState variant="card" />
        </div>
        <div className="space-y-2">
          <LoadingState variant="spinner" text="Loading leads..." />
          <LoadingState variant="skeleton" />
        </div>
      </section>

      {/* ─── Search + Pagination ─── */}
      <section className="space-y-3">
        <h2 className="font-heading text-lg font-semibold">Search & Pagination</h2>
        <div className="flex gap-4">
          <SearchInput
            value={searchValue}
            onChange={setSearchValue}
            placeholder="Search leads..."
            className="w-72"
          />
          <SearchInput
            value=""
            onChange={() => {}}
            placeholder="Disabled state shown in header..."
            className="w-72"
          />
        </div>
        <Pagination
          page={page}
          pageSize={pageSize}
          total={247}
          totalPages={25}
          onPageChange={setPage}
          onPageSizeChange={setPageSize}
        />
      </section>

      {/* ─── Dialog ─── */}
      <section className="space-y-3">
        <h2 className="font-heading text-lg font-semibold">Dialogs</h2>
        <div className="flex gap-2">
          <Button onClick={() => setConfirmOpen(true)} variant="outline">
            Open Confirm Dialog
          </Button>
          <Button onClick={() => toast.success("This is a success toast!")} variant="outline">
            Success Toast
          </Button>
          <Button onClick={() => toast.error("This is an error toast!")} variant="outline">
            Error Toast
          </Button>
          <Button onClick={() => toast("This is a default toast", { description: "With description" })} variant="outline">
            Info Toast
          </Button>
        </div>
        <ConfirmDialog
          open={confirmOpen}
          onOpenChange={setConfirmOpen}
          title="Delete Lead"
          description="Are you sure you want to delete this lead? This action cannot be undone."
          confirmLabel="Delete"
          variant="destructive"
          onConfirm={() => {
            toast("Lead deleted")
            setConfirmOpen(false)
          }}
        />
      </section>

      {/* ─── Forms ─── */}
      <section className="space-y-3">
        <h2 className="font-heading text-lg font-semibold">Forms</h2>
        <Tabs defaultValue="login" className="w-full">
          <TabsList>
            <TabsTrigger value="login">Login</TabsTrigger>
            <TabsTrigger value="lead">Lead</TabsTrigger>
            <TabsTrigger value="product">Product</TabsTrigger>
            <TabsTrigger value="meeting">Meeting</TabsTrigger>
            <TabsTrigger value="settings">Settings</TabsTrigger>
          </TabsList>
          <TabsContent value="login">
            <Card>
              <CardHeader>
                <CardTitle>Login Form</CardTitle>
                <CardDescription>Sign in to your account</CardDescription>
              </CardHeader>
              <CardContent className="max-w-sm">
                <LoginForm
                  onSubmit={(data) => toast(`Login attempted: ${data.email}`)}
                />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="lead">
            <Card>
              <CardHeader>
                <CardTitle>Lead Form</CardTitle>
                <CardDescription>Add a new lead or edit existing</CardDescription>
              </CardHeader>
              <CardContent className="max-w-2xl">
                <LeadForm
                  onSubmit={(data) => toast(`Lead saved: ${data.name}`)}
                  defaultValues={{
                    name: "Jordan Lee",
                    phone: "+1 415 555 0132",
                    source: "meta_ads",
                    status: "new",
                  }}
                />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="product">
            <Card>
              <CardHeader>
                <CardTitle>Product Form</CardTitle>
                <CardDescription>Add a plan or product to the catalog</CardDescription>
              </CardHeader>
              <CardContent className="max-w-2xl">
                <ProductForm
                  onSubmit={(data) => toast(`Product saved: ${data.name}`)}
                  defaultValues={{
                    name: "CRM Growth",
                    category: "crm",
                    billing_period: "monthly",
                    status: "active",
                  }}
                />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="meeting">
            <Card>
              <CardHeader>
                <CardTitle>Meeting Form</CardTitle>
                <CardDescription>Schedule a Google Meet with a lead</CardDescription>
              </CardHeader>
              <CardContent className="max-w-md">
                <MeetingForm
                  onSubmit={(data) => toast(`Meeting scheduled: ${data.scheduled_at}`)}
                  defaultValues={{ lead_id: "00000000-0000-0000-0000-000000000001" }}
                />
              </CardContent>
            </Card>
          </TabsContent>
          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Settings Form</CardTitle>
                <CardDescription>Configure your application</CardDescription>
              </CardHeader>
              <CardContent className="max-w-2xl">
                <SettingsForm
                  onSubmit={(data) => toast(`Settings saved: ${data.company_name}`)}
                  defaultValues={{
                    company_name: "Acme Cloud",
                    admin_email: "admin@example.com",
                    admin_whatsapp: "14155550132",
                  }}
                />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </section>
    </div>
  )
}
