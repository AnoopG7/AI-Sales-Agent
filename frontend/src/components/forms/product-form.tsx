import { useForm, useWatch, type Resolver, type Control } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { productFormSchema, type ProductFormData } from "@/schemas/validators"
import { Button, Input, Label, Textarea, Switch, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui"
import { PRODUCT_CATEGORIES, PRODUCT_STATUSES, BILLING_PERIODS, DEFAULT_CURRENCY } from "@/config/constants"
import { Loader2Icon, XIcon } from "lucide-react"
import { useState } from "react"

const FEATURE_OPTIONS = [
  "Deal pipeline", "Sales forecasting", "Email sync", "Email sequences",
  "Workflow automation", "Lead routing", "API access", "Webhooks",
  "SSO / SAML", "Audit logs", "Live chat", "Knowledge base",
]

interface ProductFormProps {
  onSubmit: (data: ProductFormData) => void
  defaultValues?: Partial<ProductFormData>
  loading?: boolean
}

export function ProductForm({ onSubmit, defaultValues, loading }: ProductFormProps) {
  const [features, setFeatures] = useState<string[]>(defaultValues?.features ?? [])
  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { errors },
  } = useForm<ProductFormData>({
    resolver: zodResolver(productFormSchema) as unknown as Resolver<ProductFormData>,
    defaultValues: {
      status: "active",
      billing_period: "monthly",
      min_seats: 1,
      featured: false,
      features: [],
      ...defaultValues,
    },
  })

  const watchedValues = useWatch({ control } as { control: Control<ProductFormData> })

  const toggleFeature = (feature: string) => {
    const next = features.includes(feature)
      ? features.filter((f) => f !== feature)
      : [...features, feature]
    setFeatures(next)
    setValue("features", next)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Name */}
      <div className="space-y-2">
        <Label htmlFor="name">Name *</Label>
        <Input id="name" placeholder="CRM Growth" {...register("name")} />
        {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
      </div>

      {/* Description */}
      <div className="space-y-2">
        <Label htmlFor="description">Description *</Label>
        <Textarea
          id="description"
          placeholder="Who this plan is for and what it includes..."
          rows={4}
          {...register("description")}
        />
        {errors.description && <p className="text-xs text-destructive">{errors.description.message}</p>}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {/* Price */}
        <div className="space-y-2">
          <Label htmlFor="price">Price ({DEFAULT_CURRENCY}) *</Label>
          <Input id="price" type="number" step="0.01" placeholder="39" {...register("price")} />
          {errors.price && <p className="text-xs text-destructive">{errors.price.message}</p>}
        </div>

        {/* Billing period */}
        <div className="space-y-2">
          <Label htmlFor="billing_period">Billing period</Label>
          <Select
            defaultValue={watchedValues.billing_period}
            onValueChange={(v) => setValue("billing_period", v as ProductFormData["billing_period"])}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(BILLING_PERIODS).map(([key, val]) => (
                <SelectItem key={key} value={key}>{val.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Category */}
        <div className="space-y-2">
          <Label htmlFor="category">Category *</Label>
          <Select
            defaultValue={watchedValues.category}
            onValueChange={(v) => setValue("category", v as ProductFormData["category"])}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select category" />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(PRODUCT_CATEGORIES).map(([key, val]) => (
                <SelectItem key={key} value={key}>{val.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.category && <p className="text-xs text-destructive">{errors.category.message}</p>}
        </div>

        {/* Status */}
        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <Select
            defaultValue={watchedValues.status}
            onValueChange={(v) => setValue("status", v as ProductFormData["status"])}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(PRODUCT_STATUSES).map(([key, val]) => (
                <SelectItem key={key} value={key}>{val.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Min seats */}
        <div className="space-y-2">
          <Label htmlFor="min_seats">Min seats</Label>
          <Input id="min_seats" type="number" min={1} {...register("min_seats")} />
        </div>

        {/* Max seats */}
        <div className="space-y-2">
          <Label htmlFor="max_seats">Max seats</Label>
          <Input id="max_seats" type="number" min={1} placeholder="Unlimited" {...register("max_seats")} />
          {errors.max_seats && <p className="text-xs text-destructive">{errors.max_seats.message}</p>}
        </div>
      </div>

      {/* Features */}
      <div className="space-y-2">
        <Label>Features</Label>
        <div className="flex flex-wrap gap-1.5">
          {FEATURE_OPTIONS.map((feature) => {
            const selected = features.includes(feature)
            return (
              <button
                key={feature}
                type="button"
                onClick={() => toggleFeature(feature)}
                className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-colors ${
                  selected
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
              >
                {feature}
                {selected && <XIcon className="size-3" />}
              </button>
            )
          })}
        </div>
      </div>

      {/* Featured toggle */}
      <div className="flex items-center gap-2">
        <Switch
          id="featured"
          checked={watchedValues.featured}
          onCheckedChange={(v) => setValue("featured", v)}
        />
        <Label htmlFor="featured" className="text-sm font-normal">
          Featured plan
        </Label>
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button type="submit" disabled={loading}>
          {loading && <Loader2Icon className="mr-1.5 size-4 animate-spin" />}
          Save Product
        </Button>
      </div>
    </form>
  )
}
