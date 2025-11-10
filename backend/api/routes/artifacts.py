"""Artifacts API - 생성된 1p 파일 관리"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import PlainTextResponse, RedirectResponse
from backend.core.database import get_supabase_admin
from supabase import Client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/artifacts/{artifact_id}")
async def get_artifact(
    artifact_id: str,
    supabase: Client = Depends(get_supabase_admin)
):
    """
    Artifact 다운로드
    
    - MD: 직접 반환 (text/plain)
    - PDF: Supabase Storage URL로 리디렉트
    """
    try:
        # Artifact 조회
        artifact_result = supabase.table("artifacts") \
            .select("*") \
            .eq("id", artifact_id) \
            .execute()
        
        if not artifact_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact {artifact_id}를 찾을 수 없습니다"
            )
        
        artifact = artifact_result.data[0]
        format_type = artifact["format"]
        url = artifact["url"]
        
        if format_type == "md":
            # MD 파일: 직접 반환
            # TODO: Phase 2.3에서 Supabase Storage에서 실제 파일 읽기
            logger.warning("[TODO] MD file fetching from Storage not implemented yet")
            return PlainTextResponse(
                content="# Sample 1-Pager\n\nThis is a placeholder. Phase 2.3 will implement actual file fetching.",
                media_type="text/plain"
            )
        
        elif format_type == "pdf":
            # PDF 파일: URL로 리디렉트
            if not url:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="PDF URL이 없습니다"
                )
            return RedirectResponse(url=url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 형식: {format_type}"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Failed to get artifact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Artifact 조회 실패: {str(e)}"
        )

