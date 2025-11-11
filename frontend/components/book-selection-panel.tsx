'use client'

import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Badge } from '@/components/ui/badge'
import { X } from 'lucide-react'

interface Book {
  id: string
  meta_json: {
    title: string
    author: string
  }
}

interface BookSelectionPanelProps {
  selectedBooks: Book[]
  format: 'content' | 'service'
  remindEnabled: boolean
  onFormatChange: (format: 'content' | 'service') => void
  onRemindToggle: (enabled: boolean) => void
  onRemoveBook: (bookId: string) => void
  onReset: () => void
}

export function BookSelectionPanel({
  selectedBooks,
  format,
  remindEnabled,
  onFormatChange,
  onRemindToggle,
  onRemoveBook,
  onReset,
}: BookSelectionPanelProps) {
  const router = useRouter()

  const handleNext = () => {
    console.log('[BookSelection] Next button clicked, selectedBooks:', selectedBooks.length)
    if (selectedBooks.length === 0) {
      console.log('[BookSelection] No books selected, aborting')
      return
    }
    console.log('[BookSelection] Navigating to /fusion')
    router.push('/fusion')
  }

  return (
    <Card className="sticky top-4">
      <CardHeader>
        <div className="flex justify-between items-center">
          <CardTitle className="text-lg">선택된 도서</CardTitle>
          <Badge variant="secondary">
            {selectedBooks.length} / 10
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Selected Books List */}
        {selectedBooks.length > 0 ? (
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {selectedBooks.map((book) => (
              <div
                key={book.id}
                className="flex items-start justify-between gap-2 p-2 bg-gray-50 rounded text-sm"
              >
                <div className="flex-1 min-w-0">
                  <p className="font-medium truncate">
                    {book.meta_json.title}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {book.meta_json.author}
                  </p>
                </div>
                <button
                  onClick={() => onRemoveBook(book.id)}
                  className="flex-shrink-0 text-gray-400 hover:text-gray-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-sm text-gray-500">
            도서를 선택해주세요
          </div>
        )}

        {/* Format Selection */}
        <div className="space-y-2">
          <Label>1p 형식</Label>
          <Select value={format} onValueChange={onFormatChange}>
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="content">Content (콘텐츠형)</SelectItem>
              <SelectItem value="service">Service (서비스형)</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Remind Toggle */}
        <div className="flex items-center justify-between">
          <Label htmlFor="remind-toggle">리마인드 설정</Label>
          <button
            id="remind-toggle"
            onClick={() => onRemindToggle(!remindEnabled)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
              remindEnabled ? 'bg-primary' : 'bg-gray-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                remindEnabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Action Buttons */}
        <div className="space-y-2 pt-4 border-t">
          <Button
            className="w-full"
            onClick={handleNext}
            disabled={selectedBooks.length === 0}
          >
            다음 단계
          </Button>
          <Button
            variant="outline"
            className="w-full"
            onClick={onReset}
            disabled={selectedBooks.length === 0}
          >
            초기화
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}

