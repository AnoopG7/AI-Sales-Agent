import { useForm, useWatch, type Resolver, type Control } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { leadFormSchema, type LeadFormData } from "@/schemas/validators"
import { Button, Input, Label, Textarea, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui"
import { LEAD_STATUSES, LEAD_SOURCES, DEFAULT_CURRENCY } from "@/config/constants"
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
          <Input id="phone" placeholder="+1 415 555 0132" {...register("phone")} />
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
          <Label htmlFor="budget_min">Budget Min ({DEFAULT_CURRENCY})</Label>
          <Input id="budget_min" type="number" placeholder="500" {...register("budget_min")} />
        </div>

        {/* Budget Max */}
        <div className="space-y-2">
          <Label htmlFor="budget_max">Budget Max ({DEFAULT_CURRENCY})</Label>
          <Input id="budget_max" type="number" placeholder="1,500" {...register("budget_max")} />
        </div>

        {/* Company */}
        <div className="space-y-2">
          <Label htmlFor="company">Company</Label>
          <Input id="company" placeholder="Brightline Logistics" {...register("company")} />
        </div>

        {/* Team size */}
        <div className="space-y-2">
          <Label htmlFor="team_size">Team size (seats)</Label>
          <Input id="team_size" type="number" min={1} placeholder="25" {...register("team_size")} />
          {errors.team_size && <p className="text-xs text-destructive">{errors.team_size.message}</p>}
        </div>

        {/* Product interest */}
        <div className="space-y-2">
          <Label htmlFor="product_interest">Product interest</Label>
          <Input id="product_interest" placeholder="Pipeline tracking and forecasting" {...register("product_interest")} />
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
