'use client'

import { cn } from '@/lib/utils'
import { Check, X, Loader2 } from 'lucide-react'

interface ProgressBarProps {
  currentNode?: string
  status: 'pending' | 'running' | 'completed' | 'failed'
}

const NODE_NAMES = [
  'anchor_mapper',
  'review_domain',
  'integrator',
  'producer',
  'assemble',
  'validator',
]

const NODE_LABELS: Record<string, string> = {
  'anchor_mapper': 'AnchorMapper',
  'review_domain': 'Reviewers (4개)',
  'integrator': 'Integrator',
  'producer': 'Producer',
  'assemble': 'Assemble',
  'validator': 'Validator',
}

export function ProgressBar({ currentNode, status }: ProgressBarProps) {
  const getNodeStatus = (nodeName: string) => {
    if (status === 'failed') {
      const currentIndex = NODE_NAMES.indexOf(currentNode || '')
      const nodeIndex = NODE_NAMES.indexOf(nodeName)
      if (nodeIndex < currentIndex) return 'completed'
      if (nodeIndex === currentIndex) return 'failed'
      return 'pending'
    }

    if (status === 'completed') return 'completed'

    const currentIndex = NODE_NAMES.indexOf(currentNode || '')
    const nodeIndex = NODE_NAMES.indexOf(nodeName)

    if (currentIndex === -1) return 'pending'
    if (nodeIndex < currentIndex) return 'completed'
    if (nodeIndex === currentIndex) return 'running'
    return 'pending'
  }

  const getProgressPercent = () => {
    if (status === 'completed') return 100
    if (status === 'failed') return 0

    const currentIndex = NODE_NAMES.indexOf(currentNode || '')
    if (currentIndex === -1) return 0

    return Math.round(((currentIndex + 1) / NODE_NAMES.length) * 100)
  }

  return (
    <div className="space-y-6">
      {/* Overall Progress Bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm">
          <span className="font-medium">진행 상황</span>
          <span className="text-muted-foreground">{getProgressPercent()}%</span>
        </div>
        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={cn(
              'h-full transition-all duration-500',
              status === 'completed' && 'bg-green-500',
              status === 'failed' && 'bg-red-500',
              status === 'running' && 'bg-blue-500'
            )}
            style={{ width: `${getProgressPercent()}%` }}
          />
        </div>
      </div>

      {/* Node Status List */}
      <div className="space-y-3">
        {NODE_NAMES.map((nodeName, index) => {
          const nodeStatus = getNodeStatus(nodeName)

          return (
            <div
              key={nodeName}
              className={cn(
                'flex items-center gap-3 p-3 rounded-lg border transition-all',
                nodeStatus === 'completed' && 'bg-green-50 border-green-200',
                nodeStatus === 'running' && 'bg-blue-50 border-blue-200',
                nodeStatus === 'failed' && 'bg-red-50 border-red-200',
                nodeStatus === 'pending' && 'bg-gray-50 border-gray-200'
              )}
            >
              {/* Status Icon */}
              <div
                className={cn(
                  'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center',
                  nodeStatus === 'completed' && 'bg-green-500',
                  nodeStatus === 'running' && 'bg-blue-500',
                  nodeStatus === 'failed' && 'bg-red-500',
                  nodeStatus === 'pending' && 'bg-gray-300'
                )}
              >
                {nodeStatus === 'completed' && (
                  <Check className="h-5 w-5 text-white" />
                )}
                {nodeStatus === 'running' && (
                  <Loader2 className="h-5 w-5 text-white animate-spin" />
                )}
                {nodeStatus === 'failed' && <X className="h-5 w-5 text-white" />}
                {nodeStatus === 'pending' && (
                  <span className="text-xs text-white font-medium">
                    {index + 1}
                  </span>
                )}
              </div>

              {/* Node Name */}
              <div className="flex-1">
                <p
                  className={cn(
                    'text-sm font-medium',
                    nodeStatus === 'completed' && 'text-green-900',
                    nodeStatus === 'running' && 'text-blue-900',
                    nodeStatus === 'failed' && 'text-red-900',
                    nodeStatus === 'pending' && 'text-gray-600'
                  )}
                >
                  {NODE_LABELS[nodeName] || nodeName}
                </p>
              </div>

              {/* Status Label */}
              <div className="flex-shrink-0">
                {nodeStatus === 'completed' && (
                  <span className="text-xs text-green-700">완료</span>
                )}
                {nodeStatus === 'running' && (
                  <span className="text-xs text-blue-700">진행 중</span>
                )}
                {nodeStatus === 'failed' && (
                  <span className="text-xs text-red-700">실패</span>
                )}
                {nodeStatus === 'pending' && (
                  <span className="text-xs text-gray-500">대기 중</span>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

