import { useForm, type Resolver } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { settingsSchema, type SettingsFormData } from "@/schemas/validators"
import { Button, Input, Label } from "@/components/ui"
import { Loader2Icon } from "lucide-react"

interface SettingsFormProps {
  onSubmit: (data: SettingsFormData) => void
  defaultValues?: Partial<SettingsFormData>
  loading?: boolean
}

export function SettingsForm({ onSubmit, defaultValues, loading }: SettingsFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SettingsFormData>({
    resolver: zodResolver(settingsSchema) as unknown as Resolver<SettingsFormData>,
    defaultValues: {
      ai_model: "gpt-4o-mini",
      ai_temperature: 0.7,
      business_hours_start: "09:00",
      business_hours_end: "19:00",
      timezone: "Asia/Dubai",
      ...defaultValues,
    },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* Company Info */}
      <fieldset className="space-y-4">
        <legend className="font-heading text-sm font-semibold text-foreground">Company Information</legend>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="company_name">Company Name</Label>
            <Input id="company_name" placeholder="LeadGen Real Estate" {...register("company_name")} />
            {errors.company_name && <p className="text-xs text-destructive">{errors.company_name.message}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="admin_email">Admin Email</Label>
            <Input id="admin_email" type="email" placeholder="admin@example.com" {...register("admin_email")} />
            {errors.admin_email && <p className="text-xs text-destructive">{errors.admin_email.message}</p>}
          </div>
          <div className="space-y-2">
            <Label htmlFor="admin_whatsapp">Admin WhatsApp</Label>
            <Input id="admin_whatsapp" placeholder="971501234567" {...register("admin_whatsapp")} />
            {errors.admin_whatsapp && <p className="text-xs text-destructive">{errors.admin_whatsapp.message}</p>}
          </div>
        </div>
      </fieldset>

      {/* AI Agent Config */}
      <fieldset className="space-y-4">
        <legend className="font-heading text-sm font-semibold text-foreground">AI Agent Configuration</legend>
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="ai_model">Model</Label>
            <Input id="ai_model" placeholder="gpt-4o-mini" {...register("ai_model")} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="ai_temperature">Temperature (0–2)</Label>
            <Input id="ai_temperature" type="number" min={0} max={2} step={0.1} {...register("ai_temperature")} />
          </div>
        </div>
      </fieldset>

      {/* Business Hours */}
      <fieldset className="space-y-4">
        <legend className="font-heading text-sm font-semibold text-foreground">Business Hours</legend>
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="business_hours_start">Start Time</Label>
            <Input id="business_hours_start" type="time" {...register("business_hours_start")} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="business_hours_end">End Time</Label>
            <Input id="business_hours_end" type="time" {...register("business_hours_end")} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="timezone">Timezone</Label>
            <Input id="timezone" {...register("timezone")} />
          </div>
        </div>
      </fieldset>

      <div className="flex justify-end gap-2">
        <Button type="submit" disabled={loading}>
          {loading && <Loader2Icon className="mr-1.5 size-4 animate-spin" />}
          Save Settings
        </Button>
      </div>
    </form>
  )
}
