"""LangGraph State Definition for 1-pager Generation"""
from typing import Sequence, Annotated, Optional, List, Dict
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
import operator


class OnePagerState(TypedDict):
    """
    1p 생성을 위한 LangGraph State
    
    Annotated[list, operator.add]를 사용하는 필드는 누적됨
    일반 필드는 최신 값으로 덮어씀
    """
    
    # === 입력 파라미터 ===
    book_ids: List[str]  # 선택된 도서 ID 목록 (1권만 처리)
    book_summary: Optional[str]  # 단일 책 요약
    book_title: Optional[str]  # 책 제목
    book_author: Optional[str]  # 저자
    book_topic: Optional[str]  # 주제
    mode: str  # "synthesis" (긴장축 3개) or "simple_merge" (4개 병치)
    format: str  # "content" or "service"
    remind_enabled: bool  # 리마인드 활성화 여부
    
    # === 메시지 (누적) ===
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # === AnchorMapper 결과 ===
    anchors: Dict[str, str]  # {domain: anchor_id}
    anchor_analysis: Optional[str]  # 합치/상충/누락/경계 분석
    available_anchors: Optional[List[str]]  # 사용 가능한 모든 KB 앵커 리스트 (가짜 앵커 방지)
    
    # === Reviewer 결과 (누적) ===
    reviews: Annotated[List[Dict], operator.add]  # [{domain, advantages, problems, conditions, anchor_id}]
    
    # === Integrator 결과 ===
    tension_axes: Optional[List[str]]  # 긴장축 2-3개 (Reduce 모드)
    integration_result: Optional[str]  # 통합 결과 텍스트
    format_reasoning: Optional[str]  # 형식 분기 사유
    
    # === Producer 결과 ===
    onepager_proposal: Optional[str]  # 1p 제안서 (제목~CTA, Producer 창작)
    onepager_md: Optional[str]  # 최종 조립된 완전한 1p (Markdown)
    onepager_pdf_url: Optional[str]  # PDF URL (생성 후)
    unique_sentences: Annotated[List[str], operator.add]  # 고유문장 (누적)
    
    # === Validator 결과 ===
    anchored_by_percent: Optional[float]  # anchored_by 비율
    unique_sentence_count: Optional[int]  # 고유문장 개수
    external_frame_count: Optional[int]  # 외부 프레임 개수
    validation_passed: Optional[bool]  # 검증 통과 여부
    validation_errors: Annotated[List[str], operator.add]  # 검증 에러 (누적)
    
    # === 메타 정보 ===
    current_node: Optional[str]  # 현재 실행 중인 노드
    error_message: Optional[str]  # 에러 메시지
    retry_count: Optional[int]  # 재시도 횟수


# 초기 State 생성 헬퍼
def create_initial_state(
    book_ids: List[str],
    mode: str,
    format: str,
    remind_enabled: bool = False,
    book_summary: Optional[str] = None,
    book_title: Optional[str] = None,
    book_author: Optional[str] = None,
    book_topic: Optional[str] = None
) -> OnePagerState:
    """초기 State 생성"""
    return OnePagerState(
        # 입력
        book_ids=book_ids,
        book_summary=book_summary,
        book_title=book_title,
        book_author=book_author,
        book_topic=book_topic,
        mode=mode,
        format=format,
        remind_enabled=remind_enabled,
        
        # 누적 필드
        messages=[],
        reviews=[],
        unique_sentences=[],
        validation_errors=[],
        
        # Optional 필드
        anchors={},
        anchor_analysis=None,
        available_anchors=None,
        tension_axes=None,
        integration_result=None,
        format_reasoning=None,
        onepager_md=None,
        onepager_pdf_url=None,
        anchored_by_percent=None,
        unique_sentence_count=None,
        external_frame_count=None,
        validation_passed=None,
        current_node=None,
        error_message=None,
        retry_count=0
    )

