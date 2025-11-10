"""Books API"""
from fastapi import APIRouter, HTTPException, Depends, status, Query
from backend.core.database import get_supabase_admin
from backend.models.schemas import BookResponse, BookMetadata
from supabase import Client
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/books", response_model=List[BookResponse])
async def get_books(
    domain: Optional[str] = Query(None, description="도메인 필터 (경제경영/과학기술/역사사회/인문자기계발)"),
    topic: Optional[str] = Query(None, description="Topic 필터"),
    year_min: Optional[int] = Query(None, description="최소 연도"),
    year_max: Optional[int] = Query(None, description="최대 연도"),
    library_id: Optional[str] = Query(None, description="Library ID 필터"),
    limit: int = Query(100, ge=1, le=1000, description="최대 결과 개수"),
    offset: int = Query(0, ge=0, description="결과 오프셋"),
    supabase: Client = Depends(get_supabase_admin)
):
    """
    도서 목록 조회 (필터링 지원)
    
    - domain: 도메인 필터
    - topic: Topic 필터
    - year_min/year_max: 연도 범위 필터
    - library_id: 특정 library의 도서만 조회
    - limit/offset: 페이지네이션
    """
    try:
        # 기본 쿼리
        query = supabase.table("books").select("*")
        
        # Library ID 필터
        if library_id:
            query = query.eq("library_id", library_id)
        
        # JSONB 필터들
        if domain:
            query = query.filter("meta_json->>domain", "eq", domain)
        
        if topic:
            query = query.filter("meta_json->>topic", "ilike", f"%{topic}%")
        
        if year_min:
            query = query.filter("meta_json->>year", "gte", str(year_min))
        
        if year_max:
            query = query.filter("meta_json->>year", "lte", str(year_max))
        
        # 페이지네이션
        query = query.range(offset, offset + limit - 1)
        
        # 정렬 (최신순)
        query = query.order("created_at", desc=True)
        
        # 실행
        result = query.execute()
        
        if not result.data:
            return []
        
        # Response 변환
        books = []
        for book in result.data:
            books.append(BookResponse(
                id=book["id"],
                library_id=book["library_id"],
                meta_json=BookMetadata(**book["meta_json"]),
                created_at=book["created_at"]
            ))
        
        logger.info(f"[BOOKS] Retrieved {len(books)} books with filters: domain={domain}, topic={topic}, year_min={year_min}, year_max={year_max}")
        
        return books
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to get books: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"도서 조회 실패: {str(e)}"
        )

