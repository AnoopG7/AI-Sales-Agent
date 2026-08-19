import { useForm, type Resolver } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { meetingFormSchema, type MeetingFormData } from "@/schemas/validators"
import { Button, Input, Label, Textarea } from "@/components/ui"
import { Loader2Icon } from "lucide-react"

interface MeetingFormProps {
  onSubmit: (data: MeetingFormData) => void
  defaultValues?: Partial<MeetingFormData>
  loading?: boolean
}

export function MeetingForm({ onSubmit, defaultValues, loading }: MeetingFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<MeetingFormData>({
    resolver: zodResolver(meetingFormSchema) as unknown as Resolver<MeetingFormData>,
    defaultValues: {
      duration_minutes: 30,
      ...defaultValues,
    },
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Lead ID (hidden — set by parent) */}
      <input type="hidden" {...register("lead_id")} />

      <div className="grid gap-4 sm:grid-cols-2">
        {/* Date & Time */}
        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="scheduled_at">Date & Time *</Label>
          <Input
            id="scheduled_at"
            type="datetime-local"
            {...register("scheduled_at")}
          />
          {errors.scheduled_at && (
            <p className="text-xs text-destructive">{errors.scheduled_at.message}</p>
          )}
        </div>

        {/* Duration */}
        <div className="space-y-2">
          <Label htmlFor="duration_minutes">Duration (minutes)</Label>
          <Input
            id="duration_minutes"
            type="number"
            min={15}
            max={120}
            step={5}
            {...register("duration_minutes")}
          />
          {errors.duration_minutes && (
            <p className="text-xs text-destructive">{errors.duration_minutes.message}</p>
          )}
        </div>
      </div>

      {/* Notes */}
      <div className="space-y-2">
        <Label htmlFor="notes">Notes</Label>
        <Textarea
          id="notes"
          placeholder="Meeting agenda or notes..."
          rows={3}
          {...register("notes")}
        />
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button type="submit" disabled={loading}>
          {loading && <Loader2Icon className="mr-1.5 size-4 animate-spin" />}
          Schedule Meeting
        </Button>
      </div>
    </form>
  )
}
