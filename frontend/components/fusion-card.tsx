'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

interface FusionCardProps {
  mode: 'synthesis' | 'simple_merge'
  title: string
  description: string
  samples: string[]
  isRecommended?: boolean
  onSelect: () => void
  loading?: boolean
}

export function FusionCard({
  mode,
  title,
  description,
  samples,
  isRecommended,
  onSelect,
  loading,
}: FusionCardProps) {
  return (
    <Card className={isRecommended ? 'border-primary shadow-md' : ''}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg">{title}</CardTitle>
          {isRecommended && (
            <Badge variant="default">추천</Badge>
          )}
        </div>
        <p className="text-sm text-muted-foreground mt-2">{description}</p>
      </CardHeader>

      <CardContent>
        <div className="space-y-3 mb-6">
          <p className="text-sm font-medium">예시 출력:</p>
          {samples.map((sample, i) => (
            <div key={i} className="flex gap-2">
              <span className="text-sm text-muted-foreground">{i + 1}.</span>
              <p className="text-sm text-muted-foreground flex-1">{sample}</p>
            </div>
          ))}
        </div>

        <Button
          onClick={onSelect}
          className="w-full"
          variant={isRecommended ? 'default' : 'outline'}
          disabled={loading}
        >
          {loading
            ? '생성 중...'
            : `${mode === 'synthesis' ? 'Synthesis' : 'Simple Merge'} 모드 선택`}
        </Button>
      </CardContent>
    </Card>
  )
}

