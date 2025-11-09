"""Producer Node - 1-pager 생성"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend.langgraph_pipeline.state import OnePagerState
from typing import Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


def producer_node(state: OnePagerState) -> Dict[str, Any]:
    """
    Producer 노드

    역할:
    1. 통합 결과를 바탕으로 1p 생성
    2. 머리말, 도메인 리뷰 카드, 통합 기록, 아이디어, 고유문장 포함
    3. 모든 문장에 [anchor_id] 태그 포함

    Args:
        state: OnePagerState

    Returns:
        부분 state 업데이트
    """
    logger.info("[START] Producer")

    mode = state.get("mode", "reduce")
    format_type = state.get("format", "content")
    reviews = state.get("reviews", [])
    integration_result = state.get("integration_result", "")
    tension_axes = state.get("tension_axes", [])

    if not reviews or not integration_result:
        logger.error("[FAIL] Missing reviews or integration result")
        return {"error_message": "Producer requires reviews and integration result"}

    # 1p 생성
    onepager_md = generate_onepager_md(
        reviews=reviews,
        integration_result=integration_result,
        tension_axes=tension_axes,
        mode=mode,
        format_type=format_type,
    )

    # 고유문장 추출
    unique_sentences = extract_unique_sentences(onepager_md)

    logger.info(
        f"[DONE] Producer (MD generated, {len(unique_sentences)} unique sentences)"
    )

    return {
        "onepager_md": onepager_md,
        "unique_sentences": unique_sentences,
        "messages": [
            HumanMessage(
                content=f"[Producer] 1p generated ({len(onepager_md)} chars, {len(unique_sentences)} unique sentences)",
                name="Producer",
            )
        ],
    }


def generate_onepager_md(
    reviews: list[Dict],
    integration_result: str,
    tension_axes: Optional[list[str]],
    mode: str,
    format_type: str,
) -> str:
    """
    1p Markdown 생성

    Args:
        reviews: 4개 도메인 리뷰
        integration_result: 통합 결과
        tension_axes: 긴장축 (Reduce 모드)
        mode: reduce or simple_merge
        format_type: content or service

    Returns:
        Markdown 텍스트
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

    system_prompt = f"""당신은 전문가 수준의 1-pager를 작성하는 전문가입니다.

**중요 규칙:**
1. 모든 문장에 반드시 [anchor_id]를 포함하세요
2. 최소 3개의 고유문장(새롭고 독창적인 통찰)을 포함하세요
3. 외부 프레임워크 언급 금지 (KB 기반만 사용)
4. 형식: {format_type} (콘텐츠형 vs 서비스형)

**구조:**
1. 머리말 (형식 분기 사유 1줄)
2. 4개 도메인 리뷰 카드
3. 통합 기록 ({mode} 모드)
4. 아이디어 2-3개
5. 고유문장 3개 (독창적 통찰)

**출력 형식:** Markdown"""

    # 리뷰 요약
    review_summary = "\n\n".join(
        [
            f"**{r['domain']}**\n"
            f"- 장점: {r.get('advantages', 'N/A')}\n"
            f"- 문제: {r.get('problems', 'N/A')}\n"
            f"- 조건: {r.get('conditions', 'N/A')}"
            for r in reviews
        ]
    )

    user_prompt = f"""4개 도메인 리뷰:
{review_summary}

통합 결과:
{integration_result}

위 내용을 바탕으로 {format_type} 형식의 1-pager를 작성하세요.
모든 문장에 [anchor_id]를 포함하고, 최소 3개의 고유문장을 만드세요."""

    try:
        response = llm.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        )

        return response.content

    except Exception as e:
        logger.error(f"[FAIL] 1p generation error: {e}")
        return f"# 1-pager 생성 실패\n\nError: {str(e)}"


def extract_unique_sentences(onepager_md: str) -> list[str]:
    """
    1p에서 고유문장 추출

    고유문장 기준:
    - "고유문장" 섹션에 명시적으로 포함된 문장들
    - 또는 특별히 표시된 독창적 통찰

    Args:
        onepager_md: 1p Markdown 텍스트

    Returns:
        고유문장 리스트
    """
    # "고유문장" 섹션 찾기
    pattern = r"##?\s*고유문장.*?\n(.*?)(?=##|$)"
    match = re.search(pattern, onepager_md, re.DOTALL | re.IGNORECASE)

    if match:
        section_text = match.group(1)
        # 번호 목록 파싱 (1. 2. 3. 또는 - )
        sentences = re.findall(
            r"(?:^|\n)\s*(?:\d+\.|[-*])\s*(.+?)(?=\n\s*(?:\d+\.|[-*])|\n\n|$)",
            section_text,
            re.DOTALL,
        )
        return [s.strip() for s in sentences if s.strip()]

    logger.warning("[WARN] No '고유문장' section found in 1p")
    return []


def generate_pdf(onepager_md: str, output_path: str) -> str:
    """
    Markdown → PDF 변환

    Args:
        onepager_md: Markdown 텍스트
        output_path: PDF 저장 경로

    Returns:
        PDF 파일 경로
    """
    # TODO: reportlab로 PDF 생성
    # 현재는 placeholder
    logger.info(f"[TODO] PDF generation to {output_path}")
    return output_path
