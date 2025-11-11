'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation } from '@tanstack/react-query'
import { FusionCard } from '@/components/fusion-card'
import { useBookSelection } from '@/lib/store'
import { useUser } from '@/hooks/useUser'
import { Button } from '@/components/ui/button'
import { ArrowLeft } from 'lucide-react'
import { toast } from 'sonner'

export default function FusionPage() {
  const router = useRouter()
  const { user, loading: userLoading } = useUser()
  const { selectedBooks, format, remindEnabled, reset } = useBookSelection()
  const [selectedMode, setSelectedMode] = useState<'synthesis' | 'simple_merge' | null>(null)

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/auth')
    }
  }, [user, userLoading, router])

  // Fetch fusion preview
  const { data: preview, isLoading } = useQuery({
    queryKey: ['fusion-preview', selectedBooks],
    queryFn: async () => {
      const { api } = await import('@/lib/api')
      return api.getFusionPreview(selectedBooks)
    },
    enabled: selectedBooks.length > 0 && !!user,
  })

  // Create run mutation
  const createRunMutation = useMutation({
    mutationFn: async (mode: 'synthesis' | 'simple_merge') => {
      const { api } = await import('@/lib/api')
      return api.createRun({
        book_ids: selectedBooks,
        mode,
        format,
        remind_enabled: remindEnabled,
      })
    },
    onSuccess: (data) => {
      // Navigate first, then reset (to prevent redirect loop)
      router.push(`/runs/${data.id}`)
      // Reset after navigation completes
      setTimeout(() => {
        reset()
      }, 100)
    },
    onError: (error) => {
      console.error('Run creation failed:', error)
      toast.error('1p 생성 요청 실패')
    },
  })

  const handleModeSelect = (mode: 'synthesis' | 'simple_merge') => {
    setSelectedMode(mode)
    createRunMutation.mutate(mode)
  }

  // Redirect if no books selected (check after mutation is defined)
  useEffect(() => {
    if (!userLoading && user && selectedBooks.length === 0 && !createRunMutation.isPending && !selectedMode) {
      toast.error('선택된 도서가 없습니다')
      router.push('/books/select')
    }
  }, [selectedBooks, user, userLoading, router, createRunMutation.isPending, selectedMode])

  if (userLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">로딩 중...</p>
      </div>
    )
  }

  if (!user) {
    return null
  }

  const recommendedMode = preview?.recommended_mode || 'synthesis'
  const synthesisExamples = [
    '도메인 간 긴장축을 발견하여 통합',
    '경제경영 vs 인문자기계발 관점 대조',
    '창의적 통찰과 실용적 제안 융합',
  ]
  const simpleMergeExamples = [
    '4개 도메인 리뷰를 순서대로 병치',
    '각 도메인의 독립적 분석 유지',
    '명확한 구조와 빠른 생성',
  ]

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
              <h1 className="text-2xl font-bold text-gray-900">Fusion Mode 선택</h1>
              <p className="text-sm text-gray-600">
                선택한 {selectedBooks.length}권의 도서로 1p를 생성합니다
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-5xl mx-auto">
          <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <p className="text-sm text-blue-900">
              <strong>Fusion Helper:</strong> 선택한 도서 수({selectedBooks.length}권)에 따라{' '}
              <strong>{recommendedMode === 'synthesis' ? 'Synthesis' : 'Simple Merge'}</strong>{' '}
              모드를 추천합니다.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Synthesis Card */}
            <FusionCard
              mode="synthesis"
              title="Synthesis Mode"
              description="도메인 간 긴장축을 발견하여 통합적 관점을 제시합니다. 창의적이고 깊이 있는 통찰을 원할 때 선택하세요."
              samples={synthesisExamples}
              isRecommended={recommendedMode === 'synthesis'}
              onSelect={() => handleModeSelect('synthesis')}
              loading={selectedMode === 'synthesis' && createRunMutation.isPending}
            />

            {/* Simple Merge Card */}
            <FusionCard
              mode="simple_merge"
              title="Simple Merge Mode"
              description="4개 도메인 리뷰를 순서대로 병치합니다. 명확한 구조와 빠른 결과를 원할 때 선택하세요."
              samples={simpleMergeExamples}
              isRecommended={recommendedMode === 'simple_merge'}
              onSelect={() => handleModeSelect('simple_merge')}
              loading={selectedMode === 'simple_merge' && createRunMutation.isPending}
            />
          </div>
        </div>
      </main>
    </div>
  )
}

