'use client'

import { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { DOMAINS } from '@/lib/constants'

interface BookFilterProps {
  onFilterChange: (filters: {
    domain?: string
    yearRange?: [number, number]
  }) => void
}

const DOMAIN_OPTIONS = [
  { value: 'all', label: '전체' },
  ...DOMAINS.map(d => ({ value: d, label: d }))
]

export function BookFilter({ onFilterChange }: BookFilterProps) {
  const [domain, setDomain] = useState('all')
  const [yearFrom, setYearFrom] = useState('')
  const [yearTo, setYearTo] = useState('')

  const handleApplyFilter = () => {
    const filters: any = {}

    if (domain !== 'all') {
      filters.domain = domain
    }

    if (yearFrom && yearTo) {
      filters.yearRange = [parseInt(yearFrom), parseInt(yearTo)]
    }

    onFilterChange(filters)
  }

  const handleReset = () => {
    setDomain('all')
    setYearFrom('')
    setYearTo('')
    onFilterChange({})
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">필터</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Domain Filter */}
        <div className="space-y-2">
          <Label>도메인</Label>
          <Select value={domain} onValueChange={setDomain}>
            <SelectTrigger>
              <SelectValue placeholder="도메인 선택" />
            </SelectTrigger>
            <SelectContent>
              {DOMAIN_OPTIONS.map((d) => (
                <SelectItem key={d.value} value={d.value}>
                  {d.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Year Range Filter */}
        <div className="space-y-2">
          <Label>출판 연도</Label>
          <div className="flex gap-2 items-center">
            <Input
              type="number"
              placeholder="시작"
              value={yearFrom}
              onChange={(e) => setYearFrom(e.target.value)}
              min="1900"
              max="2100"
            />
            <span className="text-sm text-gray-500">~</span>
            <Input
              type="number"
              placeholder="끝"
              value={yearTo}
              onChange={(e) => setYearTo(e.target.value)}
              min="1900"
              max="2100"
            />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2 pt-4">
          <Button className="w-full" onClick={handleApplyFilter}>
            필터 적용
          </Button>
          <Button variant="outline" className="w-full" onClick={handleReset}>
            초기화
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

