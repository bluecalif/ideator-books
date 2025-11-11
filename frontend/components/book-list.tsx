'use client'

import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Check } from 'lucide-react'

interface Book {
  id: string
  meta_json: {
    title: string
    author: string
    year: number
    domain: string
    topic: string
    summary: string
  }
}

interface BookListProps {
  books: Book[]
  selectedIds: string[]
  onToggle: (bookId: string) => void
}

export function BookList({ books, selectedIds, onToggle }: BookListProps) {
  if (books.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <p>검색 결과가 없습니다</p>
        <p className="text-sm mt-2">필터 조건을 변경해보세요</p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {books.map((book) => {
        const isSelected = selectedIds.includes(book.id)
        const meta = book.meta_json

        return (
          <Card
            key={book.id}
            className={`cursor-pointer transition-all ${
              isSelected
                ? 'border-primary bg-primary/5 shadow-md'
                : 'hover:shadow-md'
            }`}
            onClick={() => onToggle(book.id)}
          >
            <CardContent className="p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-start gap-2 mb-2">
                    <h3 className="font-semibold text-sm flex-1">
                      {meta.title}
                    </h3>
                    {isSelected && (
                      <Check className="h-5 w-5 text-primary flex-shrink-0" />
                    )}
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    {meta.author} · {meta.year}
                  </p>
                  <div className="flex gap-2 mb-2">
                    <Badge variant="secondary" className="text-xs">
                      {meta.domain}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {meta.topic}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-500 line-clamp-2">
                    {meta.summary}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}

