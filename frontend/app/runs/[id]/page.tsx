'use client'

import { useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import { useRunProgress } from '@/hooks/useRunProgress'
import { ProgressBar } from '@/components/progress-bar'
import { useUser } from '@/hooks/useUser'
import { Button } from '@/components/ui/button'
import { Card } from '@/components/ui/card'
import { AlertCircle } from 'lucide-react'

export default function RunProgressPage() {
  const params = useParams()
  const router = useRouter()
  const { user, loading: userLoading } = useUser()
  const runId = params.id as string

  useEffect(() => {
    if (!userLoading && !user) {
      router.push('/auth')
    }
  }, [user, userLoading, router])

  const { data: run, isLoading } = useRunProgress(runId)

  // Auto-redirect when completed
  useEffect(() => {
    console.log('[RunProgress] Checking redirect:', {
      status: run?.status,
      hasArtifacts: !!run?.artifacts,
      artifactCount: run?.artifacts?.length,
      firstArtifactId: run?.artifacts?.[0]?.id
    })
    
    if (run?.status === 'completed' && run?.artifacts?.[0]?.id) {
      console.log('[RunProgress] Redirecting to preview in 1 second...')
      // Wait 1 second before redirecting
      const timer = setTimeout(() => {
        console.log('[RunProgress] Navigating to /preview/' + run.artifacts[0].id)
        router.push(`/preview/${run.artifacts[0].id}`)
      }, 1000)

      return () => clearTimeout(timer)
    }
  }, [run, router])

  if (userLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">로딩 중...</p>
      </div>
    )
  }

  if (!user || !run) {
    return null
  }

  const currentNode = run.progress_json?.current_node
  const status = run.status

  console.log('[RunProgress] Rendering with:', { currentNode, status, percent: run.progress_json?.percent })

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="container mx-auto px-6 py-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">1p 생성 중</h1>
            <p className="text-sm text-gray-600">
              잠시만 기다려주세요. 1p를 생성하고 있습니다.
            </p>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-6 py-8">
        <div className="max-w-3xl mx-auto">
          {/* Status Card */}
          <Card className="p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">생성 진행 상황</h2>
              {status === 'completed' && (
                <span className="text-sm text-green-600 font-medium">
                  완료
                </span>
              )}
              {status === 'failed' && (
                <span className="text-sm text-red-600 font-medium">
                  실패
                </span>
              )}
              {status === 'running' && (
                <span className="text-sm text-blue-600 font-medium">
                  진행 중...
                </span>
              )}
            </div>

            <ProgressBar currentNode={currentNode} status={status} />
          </Card>

          {/* Error Message */}
          {status === 'failed' && run.error_message && (
            <Card className="p-6 bg-red-50 border-red-200">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-900 mb-1">
                    생성 실패
                  </h3>
                  <p className="text-sm text-red-700">{run.error_message}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    className="mt-4"
                    onClick={() => router.push('/books/select')}
                  >
                    다시 시도
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Completion Message */}
          {status === 'completed' && (
            <Card className="p-6 bg-green-50 border-green-200">
              <div className="text-center">
                <h3 className="font-semibold text-green-900 mb-2">
                  1p 생성 완료!
                </h3>
                <p className="text-sm text-green-700 mb-4">
                  곧 미리보기 페이지로 이동합니다...
                </p>
                {run.artifacts?.[0]?.id && (
                  <Button
                    onClick={() => router.push(`/preview/${run.artifacts[0].id}`)}
                  >
                    지금 보기
                  </Button>
                )}
              </div>
            </Card>
          )}
        </div>
      </main>
    </div>
  )
}

