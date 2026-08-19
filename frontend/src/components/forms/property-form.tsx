import { useForm, useWatch, type Resolver, type Control } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { propertyFormSchema, type PropertyFormData } from "@/schemas/validators"
import { Button, Input, Label, Textarea, Switch, Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui"
import { PROPERTY_TYPES, PROPERTY_STATUSES, DUBAI_AREAS } from "@/config/constants"
import { Loader2Icon, XIcon } from "lucide-react"
import { useState } from "react"

const AMENITY_OPTIONS = [
  "Pool", "Gym", "Parking", "Concierge", "Balcony",
  "Sea View", "City View", "Maid's Room", "Study Room",
  "Smart Home", "Central AC", "Built-in Wardrobes",
]

interface PropertyFormProps {
  onSubmit: (data: PropertyFormData) => void
  defaultValues?: Partial<PropertyFormData>
  loading?: boolean
}

export function PropertyForm({ onSubmit, defaultValues, loading }: PropertyFormProps) {
  const [amenities, setAmenities] = useState<string[]>(defaultValues?.amenities ?? [])
  const {
    register,
    handleSubmit,
    setValue,
    control,
    formState: { errors },
  } = useForm<PropertyFormData>({
    resolver: zodResolver(propertyFormSchema) as unknown as Resolver<PropertyFormData>,
    defaultValues: {
      status: "available",
      featured: false,
      amenities: [],
      ...defaultValues,
    },
  })

  const watchedValues = useWatch({ control } as { control: Control<PropertyFormData> })

  const toggleAmenity = (amenity: string) => {
    const next = amenities.includes(amenity)
      ? amenities.filter((a) => a !== amenity)
      : [...amenities, amenity]
    setAmenities(next)
    setValue("amenities", next)
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      {/* Title */}
      <div className="space-y-2">
        <Label htmlFor="title">Title *</Label>
        <Input id="title" placeholder="Luxury 2BR Apartment in Dubai Marina" {...register("title")} />
        {errors.title && <p className="text-xs text-destructive">{errors.title.message}</p>}
      </div>

      {/* Description */}
      <div className="space-y-2">
        <Label htmlFor="description">Description *</Label>
        <Textarea
          id="description"
          placeholder="Describe the property in detail..."
          rows={4}
          {...register("description")}
        />
        {errors.description && <p className="text-xs text-destructive">{errors.description.message}</p>}
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        {/* Price */}
        <div className="space-y-2">
          <Label htmlFor="price">Price (AED) *</Label>
          <Input id="price" type="number" placeholder="2500000" {...register("price")} />
          {errors.price && <p className="text-xs text-destructive">{errors.price.message}</p>}
        </div>

        {/* Type */}
        <div className="space-y-2">
          <Label htmlFor="type">Type *</Label>
          <Select
            defaultValue={watchedValues.type}
            onValueChange={(v) => setValue("type", v as PropertyFormData["type"])}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(PROPERTY_TYPES).map(([key, val]) => (
                <SelectItem key={key} value={key}>{val.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.type && <p className="text-xs text-destructive">{errors.type.message}</p>}
        </div>

        {/* Location */}
        <div className="space-y-2">
          <Label htmlFor="location">Location *</Label>
          <Select
            defaultValue={watchedValues.location}
            onValueChange={(v) => setValue("location", v)}
          >
            <SelectTrigger>
              <SelectValue placeholder="Select location" />
            </SelectTrigger>
            <SelectContent>
              {DUBAI_AREAS.map((area) => (
                <SelectItem key={area} value={area}>{area}</SelectItem>
              ))}
            </SelectContent>
          </Select>
          {errors.location && <p className="text-xs text-destructive">{errors.location.message}</p>}
        </div>

        {/* Status */}
        <div className="space-y-2">
          <Label htmlFor="status">Status</Label>
          <Select
            defaultValue={watchedValues.status}
            onValueChange={(v) => setValue("status", v as PropertyFormData["status"])}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {Object.entries(PROPERTY_STATUSES).map(([key, val]) => (
                <SelectItem key={key} value={key}>{val.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Bedrooms */}
        <div className="space-y-2">
          <Label htmlFor="bedrooms">Bedrooms</Label>
          <Input id="bedrooms" type="number" min={0} max={20} {...register("bedrooms")} />
        </div>

        {/* Bathrooms */}
        <div className="space-y-2">
          <Label htmlFor="bathrooms">Bathrooms</Label>
          <Input id="bathrooms" type="number" min={0} max={20} {...register("bathrooms")} />
        </div>

        {/* Area sqft */}
        <div className="space-y-2">
          <Label htmlFor="area_sqft">Area (sq.ft)</Label>
          <Input id="area_sqft" type="number" placeholder="1450" {...register("area_sqft")} />
        </div>
      </div>

      {/* Amenities */}
      <div className="space-y-2">
        <Label>Amenities</Label>
        <div className="flex flex-wrap gap-1.5">
          {AMENITY_OPTIONS.map((amenity) => {
            const selected = amenities.includes(amenity)
            return (
              <button
                key={amenity}
                type="button"
                onClick={() => toggleAmenity(amenity)}
                className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium transition-colors ${
                  selected
                    ? "bg-primary text-primary-foreground"
                    : "bg-muted text-muted-foreground hover:bg-muted/80"
                }`}
              >
                {amenity}
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
          Featured property
        </Label>
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <Button type="submit" disabled={loading}>
          {loading && <Loader2Icon className="mr-1.5 size-4 animate-spin" />}
          Save Property
        </Button>
      </div>
    </form>
  )
}
