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
    Artifact 정보 조회 (JSON)
    
    Returns:
        - id, run_id, kind, format, content, created_at
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
        
        # metadata_json에서 content 추출
        metadata = artifact.get("metadata_json", {})
        content = metadata.get("content", "")
        
        if not content:
            logger.warning(f"[ARTIFACT {artifact_id}] No content found in metadata_json")
            content = "# 1-Pager\n\n생성된 내용이 없습니다."
        
        # JSON 응답 반환
        return {
            "id": artifact["id"],
            "run_id": artifact["run_id"],
            "kind": artifact["kind"],
            "format": artifact["format"],
            "content": content,
            "url": artifact.get("url", ""),
            "created_at": artifact["created_at"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Failed to get artifact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Artifact 조회 실패: {str(e)}"
        )


@router.get("/artifacts/{artifact_id}/download")
async def download_artifact(
    artifact_id: str,
    supabase: Client = Depends(get_supabase_admin)
):
    """
    Artifact 다운로드 (text/plain 또는 PDF 리디렉트)
    
    - MD: PlainTextResponse로 직접 반환
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
        
        if format_type == "md":
            # MD 파일: metadata_json에서 content 가져오기
            metadata = artifact.get("metadata_json", {})
            content = metadata.get("content", "")
            
            if not content:
                content = "# 1-Pager\n\n생성된 내용이 없습니다."
            
            return PlainTextResponse(
                content=content,
                media_type="text/plain",
                headers={
                    "Content-Disposition": f'attachment; filename="1p_{artifact_id}.md"'
                }
            )
        
        elif format_type == "pdf":
            # PDF 파일: URL로 리디렉트
            url = artifact.get("url", "")
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
        logger.error(f"[ERROR] Failed to download artifact: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Artifact 다운로드 실패: {str(e)}"
        )

