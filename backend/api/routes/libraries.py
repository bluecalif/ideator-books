"""Libraries API"""
from fastapi import APIRouter, HTTPException, Depends, status, Response
from backend.core.database import get_supabase_admin
from backend.core.auth import require_auth
from backend.models.schemas import LibraryResponse
from supabase import Client
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/libraries", response_model=List[LibraryResponse])
async def get_libraries(
    user_id: str = Depends(require_auth),
    supabase: Client = Depends(get_supabase_admin)
):
    """
    사용자의 library 목록 조회
    """
    try:
        result = supabase.table("libraries") \
            .select("*") \
            .eq("user_id", user_id) \
            .order("uploaded_at", desc=True) \
            .execute()
        
        libraries = []
        for lib in result.data:
            libraries.append(LibraryResponse(
                id=lib["id"],
                user_id=lib["user_id"],
                name=lib["name"],
                uploaded_at=lib["uploaded_at"]
            ))
        
        logger.info(f"[LIBRARIES] Retrieved {len(libraries)} libraries for user {user_id}")
        
        return libraries
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to get libraries: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"라이브러리 조회 실패: {str(e)}"
        )


@router.delete("/libraries/{library_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library(
    library_id: str,
    user_id: str = Depends(require_auth),
    supabase: Client = Depends(get_supabase_admin)
):
    """
    라이브러리 삭제 (CASCADE로 books도 함께 삭제됨)
    """
    try:
        # 본인 소유 확인
        check = supabase.table("libraries") \
            .select("id") \
            .eq("id", library_id) \
            .eq("user_id", user_id) \
            .execute()
        
        if not check.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="라이브러리를 찾을 수 없거나 권한이 없습니다"
            )
        
        # 삭제 (books는 ON DELETE CASCADE로 자동 삭제)
        supabase.table("libraries").delete().eq("id", library_id).execute()
        
        logger.info(f"[LIBRARIES] Deleted library {library_id}")
        
        return Response(status_code=status.HTTP_204_NO_CONTENT)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Failed to delete library: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"라이브러리 삭제 실패: {str(e)}"
        )

