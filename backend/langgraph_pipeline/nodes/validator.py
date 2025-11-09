"""Validator Node - 1p 품질 검증"""
from backend.langgraph_pipeline.state import OnePagerState
from backend.langgraph_pipeline.utils import calculate_anchored_by_percent, extract_anchor_ids
from langchain_core.messages import HumanMessage
from typing import Dict, Any
import re
import logging

logger = logging.getLogger(__name__)

# 외부 프레임워크 키워드 (금지 목록)
EXTERNAL_FRAMEWORKS = [
    "SWOT", "PEST", "5 Forces", "Porter",
    "Blue Ocean", "Lean", "Agile", "PDCA",
    "BCG Matrix", "Ansoff", "4P", "STP"
]


def validator_node(state: OnePagerState) -> Dict[str, Any]:
    """
    Validator 노드
    
    검증 규칙:
    1. anchored_by = 100% (모든 문장이 KB 앵커 포함)
    2. 고유문장 >= 3개
    3. 외부 프레임워크 = 0개
    4. 가짜 앵커 = 0개 (품질 개선)
    
    Args:
        state: OnePagerState
    
    Returns:
        부분 state 업데이트
    """
    logger.info("[START] Validator")
    
    onepager_md = state.get("onepager_md", "")
    unique_sentences = state.get("unique_sentences", [])
    available_anchors = state.get("available_anchors", [])
    
    if not onepager_md:
        logger.error("[FAIL] No 1p to validate")
        return {
            "validation_passed": False,
            "validation_errors": ["No 1-pager content to validate"]
        }
    
    # 검증 실행
    validation_results = validate_onepager(onepager_md, unique_sentences, available_anchors)
    
    # 검증 통과 여부
    passed = validation_results["all_passed"]
    
    if passed:
        logger.info("[PASS] Validation successful")
    else:
        logger.warning(f"[FAIL] Validation failed: {validation_results['errors']}")
    
    # retry_count 증가 (실패 시)
    current_retry = state.get("retry_count", 0)
    new_retry_count = current_retry if passed else current_retry + 1
    
    return {
        "anchored_by_percent": validation_results["anchored_by_percent"],
        "unique_sentence_count": validation_results["unique_sentence_count"],
        "external_frame_count": validation_results["external_frame_count"],
        "validation_passed": passed,
        "validation_errors": validation_results["errors"],
        "retry_count": new_retry_count,
        "messages": [
            HumanMessage(
                content=(
                    f"[Validator] "
                    f"anchored_by: {validation_results['anchored_by_percent']:.1%}, "
                    f"unique: {validation_results['unique_sentence_count']}, "
                    f"external: {validation_results['external_frame_count']} "
                    f"→ {'PASS' if passed else 'FAIL (retry ' + str(new_retry_count) + ')'}"
                ),
                name="Validator"
            )
        ]
    }


def validate_onepager(
    onepager_md: str, 
    unique_sentences: list[str],
    available_anchors: list[str] = None
) -> Dict[str, Any]:
    """
    1p 검증 로직 (품질 개선: 가짜 앵커 검증 추가)
    
    Args:
        onepager_md: 1p Markdown 텍스트
        unique_sentences: State에서 추출한 고유문장
        available_anchors: 사용 가능한 KB 앵커 리스트
    
    Returns:
        검증 결과 딕셔너리
    """
    errors = []
    
    # 1. anchored_by 검증
    anchored_by_percent = calculate_anchored_by_percent(onepager_md)
    
    if anchored_by_percent < 1.0:
        errors.append(
            f"anchored_by: {anchored_by_percent:.1%} (목표: 100%)"
        )
    
    # 2. 고유문장 개수 검증
    unique_sentence_count = len(unique_sentences)
    
    if unique_sentence_count < 3:
        errors.append(
            f"고유문장: {unique_sentence_count}개 (최소: 3개)"
        )
    
    # 3. 외부 프레임워크 검증
    external_frame_count = count_external_frameworks(onepager_md)
    
    if external_frame_count > 0:
        errors.append(
            f"외부 프레임워크: {external_frame_count}개 발견 (허용: 0개)"
        )
    
    # 4. 가짜 앵커 검증 (품질 개선)
    fake_anchor_result = validate_fake_anchors(onepager_md, available_anchors or [])
    fake_anchor_count = fake_anchor_result["fake_anchor_count"]
    
    if fake_anchor_count > 0:
        fake_list = ", ".join(fake_anchor_result["fake_anchors"][:5])
        errors.append(
            f"가짜 앵커: {fake_anchor_count}개 발견 ({fake_list}...)"
        )
        logger.error(f"[FAIL] Fake anchors detected: {fake_anchor_result['fake_anchors']}")
    
    return {
        "anchored_by_percent": anchored_by_percent,
        "unique_sentence_count": unique_sentence_count,
        "external_frame_count": external_frame_count,
        "fake_anchor_count": fake_anchor_count,
        "all_passed": len(errors) == 0,
        "errors": errors
    }


def count_external_frameworks(text: str) -> int:
    """
    외부 프레임워크 키워드 개수 카운트
    
    Args:
        text: 1p 텍스트
    
    Returns:
        외부 프레임워크 언급 횟수
    """
    count = 0
    text_lower = text.lower()
    
    for keyword in EXTERNAL_FRAMEWORKS:
        # 단어 경계 확인 (정확한 매칭)
        pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
        matches = re.findall(pattern, text_lower)
        count += len(matches)
    
    return count


def validate_anchor_ids(anchor_ids: list[str]) -> list[str]:
    """
    앵커 ID 유효성 검증
    
    KB에 실제로 존재하는 앵커인지 확인
    
    Args:
        anchor_ids: 추출된 앵커 ID 리스트
    
    Returns:
        유효하지 않은 앵커 ID 리스트
    """
    invalid = []
    
    for anchor_id in anchor_ids:
        item = kb_service.get_item_by_anchor(anchor_id)
        if not item:
            invalid.append(anchor_id)
    
    return invalid


def validate_fake_anchors(onepager_md: str, available_anchors: list[str]) -> Dict[str, Any]:
    """
    가짜 앵커 검출 (품질 개선 핵심 기능)
    
    Producer가 생성한 앵커 중 실제 KB에 없는 앵커를 찾아냅니다.
    예: "투자전략_최적화_001" 같은 가짜 앵커
    
    Args:
        onepager_md: 1p Markdown 텍스트
        available_anchors: 사용 가능한 KB 앵커 리스트
    
    Returns:
        {
            "fake_anchor_count": int,
            "fake_anchors": list[str],
            "fake_anchor_ok": bool
        }
    """
    # 1p 텍스트에서 사용된 모든 앵커 추출
    used_anchors = extract_anchor_ids(onepager_md)
    
    # available_anchors set으로 변환 (빠른 조회)
    available_set = set(available_anchors)
    
    # 가짜 앵커 찾기
    fake_anchors = [anchor for anchor in used_anchors if anchor not in available_set]
    
    # 중복 제거
    fake_anchors = list(set(fake_anchors))
    
    logger.info(f"[CHECK] Fake anchors: {len(fake_anchors)}/{len(used_anchors)}")
    
    return {
        "fake_anchor_count": len(fake_anchors),
        "fake_anchors": fake_anchors,
        "fake_anchor_ok": len(fake_anchors) == 0
    }


# Import kb_service
from backend.services.kb_service import kb_service

