'use client'

import { useRouter } from 'next/navigation'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { FileText, Calendar, Trash2 } from 'lucide-react'

interface HistoryCardProps {
  id: string
  artifactId: string
  bookTitle: string
  bookAuthor?: string
  onepagerTitle?: string
  cta?: string
  mode: 'synthesis' | 'simple_merge'
  format: 'content' | 'service'
  createdAt: string
  status: 'completed' | 'failed'
  onDelete?: (id: string) => void
}

export function HistoryCard({
  id,
  artifactId,
  bookTitle,
  bookAuthor,
  onepagerTitle,
  cta,
  mode,
  format,
  createdAt,
  status,
  onDelete,
}: HistoryCardProps) {
  const router = useRouter()
  const modeLabel = mode === 'synthesis' ? 'Synthesis' : 'Simple Merge'
  const formatLabel = format === 'content' ? 'Content' : 'Service'

  const handleCardClick = () => {
    router.push(`/preview/${artifactId}`)
  }

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation() // 카드 클릭 이벤트 방지
    if (onDelete && confirm('정말 이 1p를 삭제하시겠습니까?')) {
      onDelete(id)
    }
  }

  return (
    <Card 
      className="hover:shadow-lg transition-shadow cursor-pointer h-full flex flex-col relative group"
      onClick={handleCardClick}
    >
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <FileText className="h-5 w-5 text-primary flex-shrink-0" />
          <div className="flex items-center gap-2">
            <Badge variant={status === 'completed' ? 'default' : 'destructive'}>
              {status === 'completed' ? '완료' : '실패'}
            </Badge>
            {onDelete && (
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                onClick={handleDelete}
              >
                <Trash2 className="h-4 w-4 text-red-500" />
              </Button>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="flex-1 flex flex-col">
        {/* 출발 지식 */}
        <div className="mb-3">
          <p className="text-xs text-gray-500 mb-1">출발 지식</p>
          <h3 className="font-semibold text-sm line-clamp-1">
            {bookTitle || '제목 없음'}
          </h3>
          {bookAuthor && (
            <p className="text-xs text-gray-600 mt-0.5">
              {bookAuthor}
            </p>
          )}
        </div>

        {/* 1p 제안서 제목 */}
        {onepagerTitle && (
          <div className="mb-3">
            <p className="text-xs text-gray-500 mb-1">1p 제목</p>
            <p className="text-sm line-clamp-2 text-gray-700">
              {onepagerTitle}
            </p>
          </div>
        )}

        {/* CTA */}
        {cta && (
          <div className="mb-3 flex-1">
            <p className="text-xs text-gray-500 mb-1">핵심 메시지</p>
            <p className="text-xs line-clamp-2 text-gray-600 italic">
              "{cta}"
            </p>
          </div>
        )}

        {/* 메타 정보 */}
        <div className="mt-auto pt-3 border-t">
          <div className="flex gap-2 mb-2">
            <Badge variant="outline" className="text-xs">
              {modeLabel}
            </Badge>
            <Badge variant="outline" className="text-xs">
              {formatLabel}
            </Badge>
          </div>
          <div className="flex items-center text-xs text-gray-500">
            <Calendar className="h-3 w-3 mr-1" />
            {new Date(createdAt).toLocaleDateString('ko-KR')}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
