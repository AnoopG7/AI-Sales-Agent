import { useForm, useWatch, type Resolver, type Control } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { leadFormSchema, type LeadFormData } from "@/schemas/validators"
import { Button, Input, Label, Textarea, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui"
import { LEAD_STATUSES, LEAD_SOURCES, PROPERTY_TYPES, DUBAI_AREAS } from "@/config/constants"
import { Loader2Icon } from "lucide-react"

interface LeadFormProps {
  onSubmit: (data: LeadFormData) => void
  defaultValues?: Partial<LeadFormData>
  loading?: boolean
}

export function LeadForm({ onSubmit, defaultValues, loading }: LeadFormProps) {
  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { errors },
  } = useForm<LeadFormData>({
    resolver: zodResolver(leadFormSchema) as unknown as Resolver<LeadFormData>,
    defaultValues: {
      status: "new",
      source: "manual",
      ...defaultValues,
    },
  })

  const watchedValues = useWatch({ control } as { control: Control<LeadFormData> })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        {/* Name */}
        <div className="space-y-2">
          <Label htmlFor="name">Full Name *</Label>
          <Input id="name" placeholder="Ahmed Al Maktoum" {...register("name")} />
          {errors.name && <p className="text-xs text-destructive">{errors.name.message}</p>}
        </div>

        {/* Phone */}
        <div className="space-y-2">
          <Label htmlFor="phone">Phone *</Label>
          <Input id="phone" placeholder="+971 50 123 4567" {...register("phone")} />
          {errors.phone && <p className="text-xs text-destructive">{errors.phone.message}</p>}
        </div>

        {/* Email */}
        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" placeholder="ahmed@example.com" {...register("email")} />
          {errors.email && <p className="text-xs text-destructive">{errors.email.message}</p>}
        </div>

        {/* Source */}
        <div className="space-y-2">
          <Label htmlFor="source">Source</Label>
          <Select
            defaultValue={watchedValues.source}
            onValueChange={(v) => setValue("source", v as LeadFormData["source"])}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select source" />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(LEAD_SOURCES).map(([key, val]) => (
                <SelectItem key={key} value={key}>{val.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Budget Min */}
        <div className="space-y-2">
          <Label htmlFor="budget_min">Budget Min (AED)</Label>
          <Input id="budget_min" type="number" placeholder="1,000,000" {...register("budget_min")} />
        </div>

        {/* Budget Max */}
        <div className="space-y-2">
          <Label htmlFor="budget_max">Budget Max (AED)</Label>
          <Input id="budget_max" type="number" placeholder="3,000,000" {...register("budget_max")} />
        </div>

        {/* Property Type */}
        <div className="space-y-2">
          <Label htmlFor="preferred_type">Property Type</Label>
          <Select
            defaultValue={watchedValues.preferred_type ?? ""}
            onValueChange={(v) => setValue("preferred_type", v as LeadFormData["preferred_type"] ?? undefined)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Any type" />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(PROPERTY_TYPES).map(([key, val]) => (
                <SelectItem key={key} value={key}>{val.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Location */}
        <div className="space-y-2">
          <Label htmlFor="preferred_location">Preferred Location</Label>
          <Select
            defaultValue={watchedValues.preferred_location ?? ""}
            onValueChange={(v) => setValue("preferred_location", v || undefined)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Any area" />
            </SelectTrigger>
            <SelectContent>
              {DUBAI_AREAS.map((area) => (
                <SelectItem key={area} value={area}>{area}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Bedrooms */}
        <div className="space-y-2">
          <Label htmlFor="preferred_bedrooms">Bedrooms</Label>
          <Input id="preferred_bedrooms" type="number" min={0} max={20} placeholder="Any" {...register("preferred_bedrooms")} />
        </div>

        {/* Status */}
        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <Select
            defaultValue={watchedValues.status}
            onValueChange={(v) => setValue("status", v as LeadFormData["status"])}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(LEAD_STATUSES).map(([key, val]) => (
                <SelectItem key={key} value={key}>{val.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Notes */}
      <div className="space-y-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          placeholder="Any additional information about this lead..."
          rows={3}
          {...register("notes")}
        />
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button type="submit" disabled={loading}>
          {loading && <Loader2Icon className="mr-1.5 size-4 animate-spin" />}
          Save Lead
        </Button>
      </div>
    </form>
  )
}
