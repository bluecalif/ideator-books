'use client'

import { useQuery } from '@tanstack/react-query'
import { api } from '@/lib/api'

export function useRunProgress(runId: string) {
  return useQuery({
    queryKey: ['run', runId],
    queryFn: async () => {
      const result = await api.getRunStatus(runId)
      console.log('[Progress] Poll result:', {
        status: result.status,
        currentNode: result.progress_json?.current_node,
        percent: result.progress_json?.percent,
        hasArtifacts: !!result.artifacts?.length
      })
      return result
    },
    refetchInterval: (query) => {
      const data = query.state.data
      // Stop polling when completed or failed
      if (data?.status === 'completed' || data?.status === 'failed') {
        console.log('[Progress] Stopping poll, status:', data.status)
        return false
      }
      return 2000 // Poll every 2 seconds
    },
    enabled: !!runId,
  })
}

