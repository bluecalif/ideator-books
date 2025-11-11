'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { HistoryCard } from '@/components/history-card'
import { useUser } from '@/hooks/useUser'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { ArrowLeft, Bell, ChevronDown, ChevronUp } from 'lucide-react'
import { toast } from 'sonner'
import { DOMAINS } from '@/lib/constants'

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

export default function HistoryPage() {
  const router = useRouter()
  const { user, loading: userLoading } = useUser()
  const [limit] = useState(20)
  const [offset, setOffset] = useState(0)
  const queryClient = useQueryClient()

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/auth')
    }
  }, [user, userLoading, router])

  const { data: history, isLoading } = useQuery({
    queryKey: ['history', { limit, offset }],
    queryFn: async () => {
      const { api } = await import('@/lib/api')
      return api.getHistory({ limit, offset })
    },
    enabled: !!user,
  })

  // Delete mutation
  const deleteRunMutation = useMutation({
    mutationFn: async (runId: string) => {
      const { api } = await import('@/lib/api')
      return api.deleteRun(runId)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['history'] })
      toast.success('1p가 삭제되었습니다')
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || '삭제 중 오류가 발생했습니다')
    }
  })

  const handleDelete = (runId: string) => {
    deleteRunMutation.mutate(runId)
  }

  // Filter reminder cards (remind_enabled = true)
  const reminderCards = history?.filter(
    (item: any) => item.reminders && item.reminders.length > 0 && item.reminders[0].active
  ) || []

  // 분야별 그룹핑
  const groupByDomain = (items: any[]) => {
    const grouped: Record<string, any[]> = {}
    
    DOMAINS.forEach(domain => {
      grouped[domain] = []
    })
    grouped['기타'] = []
    
    items.forEach(item => {
      const domain = item.domain || '기타'
      if (grouped[domain]) {
        grouped[domain].push(item)
      } else {
        grouped['기타'].push(item)
      }
    })
    
    return grouped
  }

  const handleLoadMore = () => {
    setOffset((prev) => prev + limit)
  }

  if (userLoading || (isLoading && offset === 0)) {
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
            <Button variant="ghost" size="sm" onClick={() => router.push('/library')}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              라이브러리로
            </Button>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">생성 히스토리</h1>
              <p className="text-sm text-gray-600">
                지금까지 생성한 1p를 확인하세요
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        {/* Reminder Cards Section */}
        {reminderCards.length > 0 && (
          <section className="mb-12">
            <div className="flex items-center gap-2 mb-4">
              <Bell className="h-5 w-5 text-primary" />
              <h2 className="text-xl font-semibold">복습 카드</h2>
              <Badge variant="secondary">{reminderCards.length}</Badge>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {reminderCards.map((item: any, index: number) => {
                const artifactContent = item.artifacts?.[0]?.metadata_json?.content || '';
                return (
                  <HistoryCard
                    key={`reminder-${item.id}-${item.artifacts?.[0]?.id || index}`}
                    id={item.id}
                    artifactId={item.artifacts?.[0]?.id || item.id}
                    bookTitle={parseSourceBookTitle(artifactContent) || item.params_json?.book_titles?.[0] || '제목 없음'}
                    bookAuthor={parseSourceBookAuthor(artifactContent)}
                    onepagerTitle={parseOnepagerTitle(artifactContent)}
                    cta={parseCTA(artifactContent)}
                    mode={item.params_json?.mode || 'synthesis'}
                    format={item.params_json?.format || 'content'}
                    createdAt={item.created_at}
                    status={item.status}
                    onDelete={handleDelete}
                  />
                );
              })}
            </div>
          </section>
        )}

        {/* All History Section */}
        <section>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">전체 히스토리</h2>
            {history && history.length > 0 && (
              <span className="text-sm text-gray-500">
                총 {history.length}개
              </span>
            )}
          </div>

          {history && history.length > 0 ? (
            <Tabs defaultValue="date" className="w-full">
              <TabsList className="mb-4">
                <TabsTrigger value="date">날짜별</TabsTrigger>
                <TabsTrigger value="domain">분야별</TabsTrigger>
              </TabsList>

              {/* 날짜별 보기 */}
              <TabsContent value="date">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {history.map((item: any, index: number) => {
                    const artifactContent = item.artifacts?.[0]?.metadata_json?.content || '';
                    return (
                      <HistoryCard
                        key={`history-${item.id}-${item.artifacts?.[0]?.id || index}`}
                        id={item.id}
                        artifactId={item.artifacts?.[0]?.id || item.id}
                        bookTitle={parseSourceBookTitle(artifactContent) || item.params_json?.book_titles?.[0] || '제목 없음'}
                        bookAuthor={parseSourceBookAuthor(artifactContent)}
                        onepagerTitle={parseOnepagerTitle(artifactContent)}
                        cta={parseCTA(artifactContent)}
                        mode={item.params_json?.mode || 'synthesis'}
                        format={item.params_json?.format || 'content'}
                        createdAt={item.created_at}
                        status={item.status}
                        onDelete={handleDelete}
                      />
                    );
                  })}
                </div>

                {history.length === limit && (
                  <div className="mt-6 text-center">
                    <Button
                      variant="outline"
                      onClick={handleLoadMore}
                      disabled={isLoading}
                    >
                      {isLoading ? '로딩 중...' : '더 보기'}
                    </Button>
                  </div>
                )}
              </TabsContent>

              {/* 분야별 보기 */}
              <TabsContent value="domain">
                {Object.entries(groupByDomain(history)).map(([domain, items]) => {
                  if (items.length === 0) return null;
                  
                  return (
                    <Collapsible key={domain} defaultOpen={items.length > 0} className="mb-6">
                      <div className="flex justify-between items-center mb-3">
                        <div className="flex items-center gap-3">
                          <h3 className="text-lg font-semibold">{domain}</h3>
                          <Badge variant="secondary">{items.length}개</Badge>
                        </div>
                        <CollapsibleTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <ChevronDown className="h-4 w-4" />
                          </Button>
                        </CollapsibleTrigger>
                      </div>
                      
                      <CollapsibleContent>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {items.map((item: any, index: number) => {
                            const artifactContent = item.artifacts?.[0]?.metadata_json?.content || '';
                            return (
                              <HistoryCard
                                key={`domain-${domain}-${item.id}-${index}`}
                                id={item.id}
                                artifactId={item.artifacts?.[0]?.id || item.id}
                                bookTitle={parseSourceBookTitle(artifactContent) || item.params_json?.book_titles?.[0] || '제목 없음'}
                                bookAuthor={parseSourceBookAuthor(artifactContent)}
                                onepagerTitle={parseOnepagerTitle(artifactContent)}
                                cta={parseCTA(artifactContent)}
                                mode={item.params_json?.mode || 'synthesis'}
                                format={item.params_json?.format || 'content'}
                                createdAt={item.created_at}
                                status={item.status}
                                onDelete={handleDelete}
                              />
                            );
                          })}
                        </div>
                      </CollapsibleContent>
                    </Collapsible>
                  );
                })}
              </TabsContent>
            </Tabs>
          ) : (
            <Card className="p-12 text-center">
              <p className="text-gray-500 mb-2">생성된 1p가 없습니다</p>
              <p className="text-sm text-gray-400 mb-4">
                도서를 선택하여 첫 1p를 생성해보세요
              </p>
              <Button onClick={() => router.push('/books/select')}>
                도서 선택하기
              </Button>
            </Card>
          )}
        </section>
      </main>
    </div>
  )
}

