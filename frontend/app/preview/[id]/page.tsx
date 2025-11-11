'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useQuery, useMutation } from '@tanstack/react-query'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { useUser } from '@/hooks/useUser'
import { ArrowLeft, Download, Eye, EyeOff, Bell, BellOff } from 'lucide-react'
import { toast } from 'sonner'

export default function PreviewPage() {
  const params = useParams()
  const router = useRouter()
  const { user, loading: userLoading } = useUser()
  const artifactId = params.id as string

  const [showAnchors, setShowAnchors] = useState(false)
  const [remindEnabled, setRemindEnabled] = useState(false)

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/auth')
    }
  }, [user, userLoading, router])

  // Fetch artifact
  const { data: artifact, isLoading } = useQuery({
    queryKey: ['artifact', artifactId],
    queryFn: async () => {
      const { api } = await import('@/lib/api')
      return api.getArtifact(artifactId)
    },
    enabled: !!artifactId && !!user,
  })

  // Toggle reminder
  const reminderMutation = useMutation({
    mutationFn: async (active: boolean) => {
      const { api } = await import('@/lib/api')
      return api.toggleReminder(artifactId, active)
    },
    onSuccess: (_, active) => {
      setRemindEnabled(active)
      toast.success(active ? '리마인드가 설정되었습니다' : '리마인드가 해제되었습니다')
    },
    onError: () => {
      toast.error('리마인드 설정 실패')
    },
  })

  const handleToggleReminder = () => {
    reminderMutation.mutate(!remindEnabled)
  }

  const handleDownload = () => {
    if (!artifact?.content) return

    const blob = new Blob([artifact.content], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `1p_${artifactId}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast.success('다운로드 완료')
  }

  // Highlight anchors in markdown
  const processedContent = artifact?.content
    ? showAnchors
      ? artifact.content.replace(
          /\[([^\]]+)\]/g,
          '<mark style="background-color: #fef3c7; padding: 2px 4px; border-radius: 3px;">[$1]</mark>'
        )
      : artifact.content
    : ''

  if (userLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">로딩 중...</p>
      </div>
    )
  }

  if (!user || !artifact) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b sticky top-0 z-10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button variant="ghost" size="sm" onClick={() => router.back()}>
                <ArrowLeft className="h-4 w-4 mr-2" />
                뒤로
              </Button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">1p 미리보기</h1>
                <div className="flex gap-2 mt-1">
                  <Badge variant="secondary">{artifact.format?.toUpperCase()}</Badge>
                  <Badge variant="outline">{artifact.kind}</Badge>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowAnchors(!showAnchors)}
              >
                {showAnchors ? (
                  <>
                    <EyeOff className="h-4 w-4 mr-2" />
                    앵커 숨기기
                  </>
                ) : (
                  <>
                    <Eye className="h-4 w-4 mr-2" />
                    앵커 보기
                  </>
                )}
              </Button>

              <Button
                variant={remindEnabled ? 'default' : 'outline'}
                size="sm"
                onClick={handleToggleReminder}
                disabled={reminderMutation.isPending}
              >
                {remindEnabled ? (
                  <>
                    <BellOff className="h-4 w-4 mr-2" />
                    리마인드 해제
                  </>
                ) : (
                  <>
                    <Bell className="h-4 w-4 mr-2" />
                    리마인드 설정
                  </>
                )}
              </Button>

              <Button size="sm" onClick={handleDownload}>
                <Download className="h-4 w-4 mr-2" />
                다운로드
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Content */}
      <main className="container mx-auto px-6 py-8">
        <Card className="p-8 max-w-4xl mx-auto">
          <div className="prose prose-sm max-w-none">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({ children }) => (
                  <h1 className="text-3xl font-bold mb-4">{children}</h1>
                ),
                h2: ({ children }) => (
                  <h2 className="text-2xl font-bold mt-6 mb-3">{children}</h2>
                ),
                h3: ({ children }) => (
                  <h3 className="text-xl font-semibold mt-4 mb-2">{children}</h3>
                ),
                p: ({ children }) => <p className="mb-4 leading-7">{children}</p>,
                ul: ({ children }) => (
                  <ul className="list-disc pl-6 mb-4 space-y-2">{children}</ul>
                ),
                ol: ({ children }) => (
                  <ol className="list-decimal pl-6 mb-4 space-y-2">{children}</ol>
                ),
              }}
            >
              {processedContent}
            </ReactMarkdown>
          </div>
        </Card>
      </main>
    </div>
  )
}

