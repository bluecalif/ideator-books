"""Runs API - 1p 생성 작업 관리"""
from fastapi import APIRouter, HTTPException, Depends, status, BackgroundTasks
from backend.core.database import get_supabase_admin
from backend.core.auth import require_auth
from backend.models.schemas import RunCreate, RunResponse, RunProgress
from backend.services.run_service import execute_pipeline_async
from supabase import Client
from typing import Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/runs", response_model=RunResponse, status_code=status.HTTP_201_CREATED)
async def create_run(
    run_data: RunCreate,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(require_auth),  # 인증 필수
    supabase: Client = Depends(get_supabase_admin)
):
    """
    1p 생성 작업 생성
    
    - run 레코드 생성 (status=pending)
    - 백그라운드 작업 등록 (Phase 2.3에서 구현)
    
    **참고**: 현재 user_id는 임시 UUID 사용 (Phase 2.4 인증 구현 후 실제 사용자로 변경)
    """
    try:
        # 도서 존재 확인
        books_result = supabase.table("books") \
            .select("id") \
            .in_("id", run_data.book_ids) \
            .execute()
        
        if not books_result.data or len(books_result.data) != len(run_data.book_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="일부 도서를 찾을 수 없습니다"
            )
        
        # user_id는 require_auth Dependency에서 자동 추출
        # Run 생성
        run_params = {
            "book_ids": run_data.book_ids,
            "mode": run_data.mode,
            "format": run_data.format,
            "remind_enabled": run_data.remind_enabled
        }
        
        run_result = supabase.table("runs").insert({
            "user_id": user_id,
            "params_json": run_params,
            "status": "pending",
            "progress_json": {
                "current_node": None,
                "percent": 0.0,
                "timestamp": datetime.now().isoformat()
            }
        }).execute()
        
        if not run_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Run 생성 실패"
            )
        
        run = run_result.data[0]
        
        # 백그라운드 작업 등록
        background_tasks.add_task(
            execute_pipeline_async,
            run["id"],
            run_data.book_ids,
            run_data.mode,
            run_data.format
        )
        
        logger.info(f"[RUN] Created run {run['id']} with {len(run_data.book_ids)} books (mode={run_data.mode})")
        logger.info(f"[RUN] Background task scheduled for run {run['id']}")
        
        return RunResponse(
            id=run["id"],
            user_id=run["user_id"],
            status=run["status"],
            progress_json=RunProgress(**run["progress_json"]),
            params_json=run["params_json"],
            error_message=None,
            created_at=run["created_at"],
            completed_at=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Failed to create run: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Run 생성 실패: {str(e)}"
        )


@router.get("/runs/{run_id}", response_model=RunResponse)
async def get_run_status(
    run_id: str,
    supabase: Client = Depends(get_supabase_admin)
):
    """
    Run 진행 상태 조회
    
    - status: pending, running, completed, failed
    - progress_json: 현재 노드, 진행률
    """
    try:
        # Run 조회
        run_result = supabase.table("runs") \
            .select("*") \
            .eq("id", run_id) \
            .execute()
        
        if not run_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Run {run_id}를 찾을 수 없습니다"
            )
        
        run = run_result.data[0]
        
        return RunResponse(
            id=run["id"],
            user_id=run["user_id"],
            status=run["status"],
            progress_json=RunProgress(**run["progress_json"]),
            params_json=run["params_json"],
            error_message=run.get("error_message"),
            created_at=run["created_at"],
            completed_at=run.get("completed_at")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Failed to get run status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Run 상태 조회 실패: {str(e)}"
        )

