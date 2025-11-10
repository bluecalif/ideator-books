"""History API - 사용자 생성 이력"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from backend.core.database import get_supabase_admin
from backend.models.schemas import HistoryResponse, ArtifactResponse, ReminderResponse, RunProgress
from supabase import Client
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/history", response_model=List[HistoryResponse])
async def get_history(
    limit: int = Query(20, ge=1, le=100, description="최대 결과 개수"),
    offset: int = Query(0, ge=0, description="결과 오프셋"),
    supabase: Client = Depends(get_supabase_admin)
):
    """
    사용자 생성 이력 조회
    
    - runs + artifacts + reminders 조인
    - status="completed" 필터
    - 최신순 정렬
    
    **참고**: 현재 user_id는 임시 UUID 사용 (Phase 2.4 인증 구현 후 실제 사용자로 변경)
    """
    try:
        # 임시 user_id (TODO: Phase 2.4에서 실제 인증 구현)
        temp_user_id = "00000000-0000-0000-0000-000000000001"
        
        # Runs 조회 (completed만)
        runs_result = supabase.table("runs") \
            .select("*") \
            .eq("user_id", temp_user_id) \
            .eq("status", "completed") \
            .order("created_at", desc=True) \
            .range(offset, offset + limit - 1) \
            .execute()
        
        if not runs_result.data:
            return []
        
        history_list = []
        
        for run in runs_result.data:
            run_id = run["id"]
            
            # Artifacts 조회
            artifacts_result = supabase.table("artifacts") \
                .select("*") \
                .eq("run_id", run_id) \
                .execute()
            
            artifacts = [
                ArtifactResponse(
                    id=artifact["id"],
                    run_id=artifact["run_id"],
                    kind=artifact["kind"],
                    format=artifact["format"],
                    url=artifact["url"],
                    metadata_json=artifact.get("metadata_json", {}),
                    created_at=artifact["created_at"]
                )
                for artifact in artifacts_result.data
            ] if artifacts_result.data else []
            
            # Reminders 조회 (첫 번째 artifact만)
            reminder = None
            if artifacts:
                first_artifact_id = artifacts[0].id
                reminder_result = supabase.table("reminders") \
                    .select("*") \
                    .eq("user_id", temp_user_id) \
                    .eq("artifact_id", first_artifact_id) \
                    .execute()
                
                if reminder_result.data:
                    rem = reminder_result.data[0]
                    reminder = ReminderResponse(
                        id=rem["id"],
                        user_id=rem["user_id"],
                        artifact_id=rem["artifact_id"],
                        schedule=rem.get("schedule"),
                        active=rem["active"],
                        created_at=rem["created_at"]
                    )
            
            # History 항목 생성
            history_item = HistoryResponse(
                run_id=run_id,
                status=run["status"],
                created_at=run["created_at"],
                completed_at=run.get("completed_at"),
                artifacts=artifacts,
                reminder=reminder,
                params=run["params_json"]
            )
            
            history_list.append(history_item)
        
        logger.info(f"[HISTORY] Retrieved {len(history_list)} history items (limit={limit}, offset={offset})")
        
        return history_list
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to get history: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"히스토리 조회 실패: {str(e)}"
        )

