"""CSV Upload API"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, status
from backend.core.database import get_supabase_admin
from backend.models.schemas import LibraryResponse
from supabase import Client
import pandas as pd
import io
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/upload", response_model=LibraryResponse, status_code=status.HTTP_201_CREATED)
async def upload_csv(
    file: UploadFile = File(...),
    supabase: Client = Depends(get_supabase_admin)
):
    """
    CSV 파일 업로드 및 library/books 생성
    
    - CSV 형식: Title, 저자, 연도, 구분(domain), Topic, 요약(summary)
    - library 생성 (파일명 기반)
    - books 테이블에 각 도서 레코드 생성
    
    **참고**: 현재 user_id는 임시 UUID 사용 (Phase 2.4 인증 구현 후 실제 사용자로 변경)
    """
    # CSV 파일 확인
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV 파일만 업로드 가능합니다"
        )
    
    try:
        # CSV 읽기
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents))
        
        # 필수 컬럼 확인
        required_columns = ['Title', '저자', '연도', '구분', 'Topic', '요약']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"필수 컬럼 누락: {', '.join(missing_columns)}"
            )
        
        # 임시 user_id (TODO: Phase 2.4에서 실제 인증 구현)
        temp_user_id = "00000000-0000-0000-0000-000000000001"
        
        # Library 생성
        library_name = file.filename.replace('.csv', '')
        
        library_result = supabase.table("libraries").insert({
            "user_id": temp_user_id,
            "name": library_name,
            "uploaded_at": datetime.now().isoformat()
        }).execute()
        
        if not library_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Library 생성 실패"
            )
        
        library = library_result.data[0]
        library_id = library["id"]
        
        # Books 생성
        books_data = []
        for _, row in df.iterrows():
            book_meta = {
                "title": str(row['Title']),
                "author": str(row['저자']),
                "year": int(row['연도']),
                "domain": str(row['구분']),
                "topic": str(row['Topic']),
                "summary": str(row['요약'])
            }
            
            books_data.append({
                "library_id": library_id,
                "meta_json": book_meta
            })
        
        # Bulk insert
        books_result = supabase.table("books").insert(books_data).execute()
        
        if not books_result.data:
            # Rollback: library 삭제
            supabase.table("libraries").delete().eq("id", library_id).execute()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Books 생성 실패"
            )
        
        logger.info(f"[UPLOAD] Library '{library_name}' created with {len(books_data)} books")
        
        return LibraryResponse(
            id=library["id"],
            user_id=library["user_id"],
            name=library["name"],
            uploaded_at=library["uploaded_at"]
        )
        
    except pd.errors.ParserError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CSV 파싱 오류: {str(e)}"
        )
    except KeyError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"필수 컬럼 오류: {str(e)}"
        )
    except Exception as e:
        logger.error(f"[ERROR] Upload failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"업로드 실패: {str(e)}"
        )

