'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { CSVUpload } from '@/components/csv-upload'
import { HistoryCard } from '@/components/history-card'
import { useUser } from '@/hooks/useUser'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { LogOut, ChevronDown, ChevronUp, Trash2 } from 'lucide-react'
import { toast } from 'sonner'

// 출발 지식 제목 파싱 (새 형식: **제목**: 개인주의자 선언)
function parseSourceBookTitle(content: string): string {
  const titleMatch = content.match(/\*\*제목\*\*:\s*(.+?)(?:\n|$)/);
  return titleMatch ? titleMatch[1].trim() : '';
}

// 출발 지식 저자 파싱 (새 형식: **저자**: 문유석)
function parseSourceBookAuthor(content: string): string {
  const authorMatch = content.match(/\*\*저자\*\*:\s*(.+?)(?:\n|$)/);
  return authorMatch ? authorMatch[1].trim() : '';
}

// 1p 제목 파싱 헬퍼 함수
function parseOnepagerTitle(content: string): string {
  const titleMatch = content.match(/##\s*제목\s*\n\*\*(.+?)\*\*/);
  return titleMatch ? titleMatch[1] : '';
}

// CTA 파싱 헬퍼 함수
function parseCTA(content: string): string {
  const ctaMatch = content.match(/##\s*CTA\s*\n"?(.+?)"?\s*\[/);
  return ctaMatch ? ctaMatch[1] : '';
}

export default function LibraryPage() {
  const router = useRouter()
  const { user, signOut, loading } = useUser()
  const queryClient = useQueryClient()
  const [isLibrariesOpen, setIsLibrariesOpen] = useState(false)

  useEffect(() => {
    if (!loading && !user) {
      router.push('/auth')
    }
  }, [user, loading, router])

  const { data: libraries, refetch: refetchLibraries } = useQuery({
    queryKey: ['libraries'],
    queryFn: async () => {
      const { api } = await import('@/lib/api')
      return api.getLibraries()
    },
    enabled: !!user,
  })

  const { data: recentResults, refetch: refetchHistory } = useQuery({
    queryKey: ['history', { limit: 6 }],
    queryFn: async () => {
      const { api } = await import('@/lib/api')
      return api.getHistory({ limit: 6 })
    },
    enabled: !!user,
  })

  const handleUploadSuccess = () => {
    refetchLibraries()
    refetchHistory()
  }

  const deleteLibraryMutation = useMutation({
    mutationFn: async (libraryId: string) => {
      const { api } = await import('@/lib/api')
      return api.deleteLibrary(libraryId)
    },
    onSuccess: () => {
      toast.success('라이브러리가 삭제되었습니다')
      refetchLibraries()
    },
    onError: () => {
      toast.error('라이브러리 삭제 실패')
    },
  })

  const deleteRunMutation = useMutation({
    mutationFn: async (runId: string) => {
      const { api } = await import('@/lib/api')
      return api.deleteRun(runId)
    },
    onSuccess: () => {
      toast.success('1p가 삭제되었습니다')
      refetchHistory()
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '삭제 중 오류가 발생했습니다')
    }
  })

  const handleDeleteLibrary = (e: React.MouseEvent, libraryId: string) => {
    e.stopPropagation()
    if (confirm('라이브러리를 삭제하시겠습니까? (관련 도서도 함께 삭제됩니다)')) {
      deleteLibraryMutation.mutate(libraryId)
    }
  }

  const handleDeleteRun = (runId: string) => {
    deleteRunMutation.mutate(runId)
  }

  if (loading) {
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
        <div className="container mx-auto px-6 py-4 flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Ideator Books</h1>
            <p className="text-sm text-gray-600">KB-based 1p Generation</p>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600">{user?.email}</span>
            <Button variant="outline" size="sm" onClick={signOut}>
              <LogOut className="h-4 w-4 mr-2" />
              로그아웃
            </Button>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* CSV Upload Section */}
        <section className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">도서 라이브러리 업로드</h2>
            <Button asChild>
              <a href="/books/select">도서 선택하기</a>
            </Button>
          </div>
          <CSVUpload onUploadSuccess={handleUploadSuccess} />
        </section>

        {/* Libraries List Section */}
        {libraries && libraries.length > 0 && (
          <section className="mb-12">
            <Collapsible open={isLibrariesOpen} onOpenChange={setIsLibrariesOpen}>
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">업로드된 라이브러리</h2>
                <CollapsibleTrigger asChild>
                  <Button variant="outline" size="sm">
                    {isLibrariesOpen ? (
                      <>
                        <ChevronUp className="h-4 w-4 mr-2" />
                        접기
                      </>
                    ) : (
                      <>
                        <ChevronDown className="h-4 w-4 mr-2" />
                        펼치기 ({libraries.length}개)
                      </>
                    )}
                  </Button>
                </CollapsibleTrigger>
              </div>
              
              <CollapsibleContent>
                <div className="bg-white rounded-lg border divide-y">
                  {libraries.map((library: any) => (
                    <div key={library.id} className="p-4 flex justify-between items-center hover:bg-gray-50">
                      <div className="flex-1">
                        <p className="font-medium">{library.name}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(library.uploaded_at).toLocaleString('ko-KR')}
                        </p>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">ID: {library.id.slice(0, 8)}</Badge>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={(e) => handleDeleteLibrary(e, library.id)}
                          disabled={deleteLibraryMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CollapsibleContent>
            </Collapsible>
          </section>
        )}

        {/* Recent Results Section */}
        <section>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">최근 생성 결과물</h2>
            {recentResults && recentResults.length > 0 && (
              <Button variant="link" asChild>
                <a href="/history">전체보기</a>
              </Button>
            )}
          </div>

          {recentResults && recentResults.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {recentResults.map((result: any, index: number) => {
                const artifactId = result.artifacts?.[0]?.id || result.id
                const artifactContent = result.artifacts?.[0]?.metadata_json?.content || '';
                return (
                  <HistoryCard
                    key={`library-recent-${result.id}-${artifactId || index}`}
                    id={result.id}
                    artifactId={artifactId}
                    bookTitle={parseSourceBookTitle(artifactContent) || result.params_json?.book_titles?.[0] || '제목 없음'}
                    bookAuthor={parseSourceBookAuthor(artifactContent)}
                    onepagerTitle={parseOnepagerTitle(artifactContent)}
                    cta={parseCTA(artifactContent)}
                    mode={result.params_json?.mode || 'synthesis'}
                    format={result.params_json?.format || 'content'}
                    createdAt={result.created_at}
                    status={result.status}
                    onDelete={handleDeleteRun}
                  />
                )
              })}
            </div>
          ) : (
            <div className="text-center py-12 bg-white rounded-lg border-2 border-dashed">
              <p className="text-gray-500">아직 생성된 결과물이 없습니다</p>
              <p className="text-sm text-gray-400 mt-2">
                CSV를 업로드하고 도서를 선택하여 1p를 생성하세요
              </p>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

