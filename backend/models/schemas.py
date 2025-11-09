"""Data models and Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class KBItem(BaseModel):
    """Knowledge Base Item - 단일 인사이트"""
    kb_id: str = Field(..., description="Unique identifier")
    domain: str = Field(..., description="도메인 (경제경영/과학기술/역사사회/인문자기계발)")
    subcategory: str = Field(..., description="소분류")
    anchor_id: str = Field(..., description="Anchor ID for referencing")
    content: str = Field(..., description="인사이트 내용")
    is_fusion: bool = Field(default=False, description="융합형 인사이트 여부")
    is_integrated_knowledge: bool = Field(default=False, description="통합지식 여부")
    reference_books: List[str] = Field(default_factory=list, description="참고 도서 목록")
    
    class Config:
        json_schema_extra = {
            "example": {
                "kb_id": "kb_001",
                "domain": "경제경영",
                "subcategory": "경제예측/금융투자",
                "anchor_id": "경제경영_경제예측_001",
                "content": "성공적인 투자의 핵심은 시대적 변수를 파악하되...",
                "is_fusion": False,
                "reference_books": ["100년 투자 가문의 비밀"]
            }
        }


class KBSearchResult(BaseModel):
    """KB 검색 결과"""
    item: KBItem
    similarity_score: float = Field(..., ge=0.0, le=1.0)


class KBStats(BaseModel):
    """KB 통계"""
    total_items: int
    fusion_items: int
    items_by_domain: dict[str, int]
    items_by_subcategory: dict[str, int]


# Run and Artifact models (for future use)
class RunCreate(BaseModel):
    """1p 생성 요청"""
    book_ids: List[str] = Field(..., min_length=1, max_length=10)
    mode: str = Field(..., pattern="^(reduce|simple_merge)$")
    format: str = Field(..., pattern="^(content|service)$")
    remind_enabled: bool = False


class RunResponse(BaseModel):
    """1p 생성 응답"""
    id: str
    user_id: str
    status: str  # pending, running, completed, failed
    progress: dict
    params: dict
    created_at: datetime
    completed_at: Optional[datetime] = None

