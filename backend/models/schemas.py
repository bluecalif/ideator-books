"""Data models and Pydantic schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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


# ============================================
# Library Models
# ============================================

class LibraryCreate(BaseModel):
    """Library 생성 요청"""
    name: str = Field(..., min_length=1, max_length=200)


class LibraryResponse(BaseModel):
    """Library 응답"""
    id: str
    user_id: str
    name: str
    uploaded_at: datetime


# ============================================
# Book Models
# ============================================

class BookMetadata(BaseModel):
    """Book 메타데이터 (JSONB)"""
    title: str
    author: str
    year: int
    domain: str
    topic: str
    summary: str


class BookResponse(BaseModel):
    """Book 응답"""
    id: str
    library_id: str
    meta_json: BookMetadata
    created_at: datetime


class BookFilter(BaseModel):
    """Book 필터"""
    domain: Optional[str] = None
    topic: Optional[str] = None
    year_min: Optional[int] = None
    year_max: Optional[int] = None
    library_id: Optional[str] = None


# ============================================
# Run Models
# ============================================

class RunCreate(BaseModel):
    """1p 생성 요청"""
    book_ids: List[str] = Field(..., min_items=1, max_items=10)
    mode: str = Field(..., pattern="^(synthesis|simple_merge)$")
    format: str = Field(..., pattern="^(content|service)$")
    remind_enabled: bool = False


class RunProgress(BaseModel):
    """Run 진행 상태"""
    current_node: Optional[str] = None
    percent: float = Field(0.0, ge=0.0, le=100.0)
    timestamp: Optional[datetime] = None


class RunResponse(BaseModel):
    """Run 응답"""
    id: str
    user_id: str
    status: str  # pending, running, completed, failed
    progress_json: RunProgress
    params_json: Dict[str, Any]
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# ============================================
# Artifact Models
# ============================================

class ArtifactResponse(BaseModel):
    """Artifact 응답"""
    id: str
    run_id: str
    kind: str  # onepager
    format: str  # md, pdf
    url: str
    metadata_json: Dict[str, Any]
    created_at: datetime


# ============================================
# Reminder Models
# ============================================

class ReminderToggle(BaseModel):
    """Reminder on/off 토글"""
    artifact_id: str
    active: bool


class ReminderResponse(BaseModel):
    """Reminder 응답"""
    id: str
    user_id: str
    artifact_id: str
    schedule: Optional[datetime] = None
    active: bool
    created_at: datetime


# ============================================
# History Models
# ============================================

class HistoryResponse(BaseModel):
    """History 응답 (runs + artifacts + reminders 조인)"""
    run_id: str
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    artifacts: List[ArtifactResponse]
    reminder: Optional[ReminderResponse] = None
    params: Dict[str, Any]


# ============================================
# Fusion Helper Models
# ============================================

class FusionPreviewRequest(BaseModel):
    """Fusion Helper 요청"""
    book_ids: List[str] = Field(..., min_items=1, max_items=10)


class FusionModeInfo(BaseModel):
    """Fusion 모드 정보"""
    mode: str  # synthesis, simple_merge
    title: str
    description: str
    samples: List[str]
    recommended: bool = False


class FusionPreviewResponse(BaseModel):
    """Fusion Helper 응답"""
    recommended_mode: FusionModeInfo
    alternative_mode: FusionModeInfo

