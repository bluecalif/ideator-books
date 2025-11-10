"""Fusion Helper API"""
from fastapi import APIRouter, HTTPException, Depends, status
from backend.core.database import get_supabase_admin
from backend.models.schemas import FusionPreviewRequest, FusionPreviewResponse, FusionModeInfo
from supabase import Client
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/fusion/preview", response_model=FusionPreviewResponse)
async def fusion_preview(
    request: FusionPreviewRequest,
    supabase: Client = Depends(get_supabase_admin)
):
    """
    Fusion Helper - 추천 모드 제공
    
    - 도서 수 기반 추천:
      * 1~2권: simple_merge (빠른 병치)
      * 3권+: synthesis (긴장축 추출)
    - 샘플 출력 제공
    """
    try:
        book_count = len(request.book_ids)
        
        # 도서 존재 확인
        books_result = supabase.table("books") \
            .select("id, meta_json") \
            .in_("id", request.book_ids) \
            .execute()
        
        if not books_result.data or len(books_result.data) != book_count:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="일부 도서를 찾을 수 없습니다"
            )
        
        # 추천 로직 (도서 수 기반)
        if book_count <= 2:
            recommended_mode = "simple_merge"
            alternative_mode = "synthesis"
        else:
            recommended_mode = "synthesis"
            alternative_mode = "simple_merge"
        
        # Synthesis 모드 정보
        synthesis_info = FusionModeInfo(
            mode="synthesis",
            title="Synthesis (통합 긴장축)",
            description="4개 도메인 리뷰를 2~3개의 핵심 긴장축으로 통합하여 체계적인 1p를 생성합니다.",
            samples=[
                "[긴장축 1] 개인의 성장 vs 사회적 책임",
                "[긴장축 2] 단기 성과 vs 장기 가치",
                "[결론] 균형있는 접근으로 지속가능한 성과 창출"
            ],
            recommended=(recommended_mode == "synthesis")
        )
        
        # Simple Merge 모드 정보
        simple_merge_info = FusionModeInfo(
            mode="simple_merge",
            title="Simple Merge (도메인별 병치)",
            description="4개 도메인 리뷰를 병치하여 빠르게 초안을 생성합니다.",
            samples=[
                "[경제경영] 시장 변화에 대응하는 투자 전략",
                "[과학기술] 기술 혁신이 가져온 새로운 기회",
                "[역사사회] 과거 사례로 본 변화의 패턴",
                "[인문자기계발] 개인 성장을 위한 실천 방법"
            ],
            recommended=(recommended_mode == "simple_merge")
        )
        
        # 응답 구성
        if recommended_mode == "synthesis":
            response = FusionPreviewResponse(
                recommended_mode=synthesis_info,
                alternative_mode=simple_merge_info
            )
        else:
            response = FusionPreviewResponse(
                recommended_mode=simple_merge_info,
                alternative_mode=synthesis_info
            )
        
        logger.info(f"[FUSION] Preview for {book_count} books, recommended: {recommended_mode}")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Fusion preview failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fusion preview 실패: {str(e)}"
        )

