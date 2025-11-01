import { useState, useEffect } from 'react'
import { CalendarDays } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { subDays, format, startOfDay, endOfDay } from 'date-fns'

interface DateRange {
  start: Date
  end: Date
}

interface DateRangePickerProps {
  onRangeChange: (range: DateRange) => void
  defaultRange?: DateRange
}

export function DateRangePicker({ onRangeChange, defaultRange }: DateRangePickerProps) {
  const defaultStart = defaultRange?.start || subDays(new Date(), 30)
  const defaultEnd = defaultRange?.end || new Date()
  
  const [startDate, setStartDate] = useState<string>(format(defaultStart, 'yyyy-MM-dd'))
  const [endDate, setEndDate] = useState<string>(format(defaultEnd, 'yyyy-MM-dd'))
  
  // Initialize on mount
  useEffect(() => {
    const start = startOfDay(defaultStart)
    const end = endOfDay(defaultEnd)
    onRangeChange({ start, end })
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const applyRange = () => {
    const start = startOfDay(new Date(startDate))
    const end = endOfDay(new Date(endDate))
    onRangeChange({ start, end })
  }

  const setPreset = (days: number | null) => {
    const end = new Date()
    const start = days ? subDays(end, days) : new Date(0) // All time
    setStartDate(format(start, 'yyyy-MM-dd'))
    setEndDate(format(end, 'yyyy-MM-dd'))
    onRangeChange({ start: startOfDay(start), end: endOfDay(end) })
  }

  return (
    <div className="flex flex-col sm:flex-row gap-2 items-start sm:items-center">
      <div className="flex gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPreset(7)}
          className="text-xs"
        >
          Last 7 days
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPreset(30)}
          className="text-xs"
        >
          Last 30 days
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPreset(90)}
          className="text-xs"
        >
          Last 90 days
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setPreset(null)}
          className="text-xs"
        >
          All time
        </Button>
      </div>
      <div className="flex gap-2 items-center">
        <div className="flex items-center gap-2">
          <CalendarDays className="h-4 w-4 text-muted-foreground" />
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="border rounded px-2 py-1 text-sm"
          />
          <span className="text-muted-foreground">to</span>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="border rounded px-2 py-1 text-sm"
          />
          <Button size="sm" onClick={applyRange}>
            Apply
          </Button>
        </div>
      </div>
    </div>
  )
}

