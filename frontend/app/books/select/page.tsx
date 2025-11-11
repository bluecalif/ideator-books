'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { BookFilter } from '@/components/book-filter'
import { BookList } from '@/components/book-list'
import { BookSelectionPanel } from '@/components/book-selection-panel'
import { useBookSelection } from '@/lib/store'
import { useUser } from '@/hooks/useUser'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'

export default function BooksSelectPage() {
  const router = useRouter()
  const { user, loading: userLoading } = useUser()
  const [filters, setFilters] = useState<{
    domain?: string
    yearRange?: [number, number]
  }>({})

  const {
    selectedBooks: selectedIds,
    format,
    remindEnabled,
    toggleBook,
    setFormat,
    setRemindEnabled,
    reset,
  } = useBookSelection()

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/auth')
    }
  }, [user, userLoading, router])

  const { data: books, isLoading } = useQuery({
    queryKey: ['books', filters],
    queryFn: async () => {
      const { api } = await import('@/lib/api')
      const result = await api.getBooks(filters)
      console.log('[Books] API response:', result)
      console.log('[Books] Filters applied:', filters)
      return result
    },
    enabled: !!user,
  })

  // Get full book objects for selected IDs
  const selectedBookObjects = books?.filter((book: any) =>
    selectedIds.includes(book.id)
  ) || []

  if (userLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">로딩 중...</p>
      </div>
    )
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Button variant="ghost" size="sm" onClick={() => router.back()}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              뒤로
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">도서 선택</h1>
              <p className="text-sm text-gray-600">
                1p 생성을 위한 도서를 선택하세요 (최대 10권)
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Left: Filter Panel */}
          <div className="col-span-12 lg:col-span-3">
            <BookFilter onFilterChange={setFilters} />
          </div>

          {/* Center: Book List */}
          <div className="col-span-12 lg:col-span-6">
            {isLoading ? (
              <div className="text-center py-12">
                <p className="text-gray-500">로딩 중...</p>
              </div>
            ) : (
              <BookList
                books={books || []}
                selectedIds={selectedIds}
                onToggle={toggleBook}
              />
            )}
          </div>

          {/* Right: Selection Panel */}
          <div className="col-span-12 lg:col-span-3">
            <BookSelectionPanel
              selectedBooks={selectedBookObjects}
              format={format}
              remindEnabled={remindEnabled}
              onFormatChange={setFormat}
              onRemindToggle={setRemindEnabled}
              onRemoveBook={toggleBook}
              onReset={reset}
            />
          </div>
        </div>
      </main>
    </div>
  )
}

