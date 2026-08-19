import type { ReactNode } from "react"
import { cn } from "@/lib/utils"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow, Skeleton } from "@/components/ui"
import { EmptyState } from "@/components/shared/empty-state"
import { ArrowUpDownIcon, ArrowUpIcon, ArrowDownIcon } from "lucide-react"

export interface Column<T> {
  key: string
  header: string
  sortable?: boolean
  render?: (item: T) => ReactNode
  className?: string
  headerClassName?: string
}

interface DataTableProps<T> {
  columns: Column<T>[]
  data: T[]
  loading?: boolean
  sortKey?: string
  sortOrder?: "asc" | "desc"
  onSort?: (key: string) => void
  onRowClick?: (item: T) => void
  emptyTitle?: string
  emptyDescription?: string
  emptyAction?: ReactNode
  rowKey?: (item: T) => string
  className?: string
}

export function DataTable<T>({
  columns,
  data,
  loading,
  sortKey,
  sortOrder,
  onSort,
  onRowClick,
  emptyTitle = "No data found",
  emptyDescription = "There are no items to display.",
  emptyAction,
  rowKey,
  className,
}: DataTableProps<T>) {
  const renderSortIcon = (key: string) => {
    if (sortKey !== key) return <ArrowUpDownIcon className="ml-1 size-3 text-muted-foreground/50" />
    if (sortOrder === "asc") return <ArrowUpIcon className="ml-1 size-3 text-primary" />
    return <ArrowDownIcon className="ml-1 size-3 text-primary" />
  }

  if (loading) {
    return (
      <div className={cn("rounded-xl border", className)}>
        <Table>
          <TableHeader>
            <TableRow>
              {columns.map((col) => (
                <TableHead key={col.key} className={col.headerClassName}>
                  {col.header}
                </TableHead>
              ))}
            </TableRow>
          </TableHeader>
          <TableBody>
            {Array.from({ length: 5 }).map((_, rowIdx) => (
              <TableRow key={rowIdx}>
                {columns.map((col) => (
                  <TableCell key={col.key}>
                    <Skeleton className="h-4 w-full" />
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className={cn("rounded-xl border", className)}>
        <EmptyState
          title={emptyTitle}
          description={emptyDescription}
          action={emptyAction}
          className="border-0"
        />
      </div>
    )
  }

  return (
    <div className={cn("rounded-xl border", className)}>
      <Table>
        <TableHeader>
          <TableRow>
            {columns.map((col) => (
              <TableHead
                key={col.key}
                className={cn(
                  col.sortable && "cursor-pointer select-none hover:text-foreground",
                  col.headerClassName,
                )}
                onClick={col.sortable && onSort ? () => onSort(col.key) : undefined}
              >
                <span className="inline-flex items-center">
                  {col.header}
                  {col.sortable && renderSortIcon(col.key)}
                </span>
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {data.map((item, index) => (
            <TableRow
              key={rowKey?.(item) ?? index}
              className={cn(onRowClick && "cursor-pointer")}
              onClick={onRowClick ? () => onRowClick(item) : undefined}
            >
              {columns.map((col) => (
                <TableCell key={col.key} className={col.className}>
                  {col.render
                    ? col.render(item)
                    : String((item as Record<string, unknown>)[col.key] ?? "—")}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
