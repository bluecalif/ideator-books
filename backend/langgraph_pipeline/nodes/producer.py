"""Producer Node - 1-pager 생성"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend.langgraph_pipeline.state import OnePagerState
from backend.core.models_config import models_config
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
    available_anchors = state.get("available_anchors", [])
    
    # 책 정보
    book_ids = state.get("book_ids", [])
    book_title = state.get("book_title", "Unknown")
    book_author = state.get("book_author", "Unknown")
    book_topic = state.get("book_topic", "Unknown")
    book_summary = state.get("book_summary", "")

    if not reviews or not integration_result:
        logger.error("[FAIL] Missing reviews or integration result")
        return {"error_message": "Producer requires reviews and integration result"}
    
    if not available_anchors:
        logger.warning("[WARN] No available_anchors provided - fake anchor prevention may not work")

    # 1p 생성
    onepager_md = generate_onepager_md(
        reviews=reviews,
        integration_result=integration_result,
        tension_axes=tension_axes,
        mode=mode,
        format_type=format_type,
        available_anchors=available_anchors,
        book_id=book_ids[0] if book_ids else 0,
        book_title=book_title,
        book_author=book_author,
        book_topic=book_topic,
        book_summary=book_summary,
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
    available_anchors: list[str],
    book_id: int,
    book_title: str,
    book_author: str,
    book_topic: str,
    book_summary: str,
) -> str:
    """
    1p Markdown 생성 (품질 개선 버전: 1p 제안서 7요소 구조 + 출발지식)

    Args:
        reviews: 4개 도메인 리뷰
        integration_result: 통합 결과
        tension_axes: 긴장축 (Reduce 모드)
        mode: reduce or simple_merge
        format_type: content or service
        available_anchors: 사용 가능한 KB 앵커 리스트
        book_id: 도서 ID
        book_title: 제목
        book_author: 저자
        book_topic: 주제
        book_summary: 요약

    Returns:
        Markdown 텍스트
    """
    llm = ChatOpenAI(model=models_config.PRODUCER_MODEL, temperature=models_config.PRODUCER_TEMP)

    system_prompt = f"""당신은 전문가 수준의 1-pager를 작성하는 전문가입니다.

**필수 구조 (docs/1p사례.md 기준):**

# 출발 지식
일련번호: [book_id]
제목: [book_title]
연도: [year]
저자: [book_author]
구분: [domain]
Topic: [topic]
요약: [book_summary 첫 200-300자]

---

# 형식 분기
**{format_type}형** — 구체적이고 설득력 있는 선정 사유 1줄 (책의 구체적 내용 기반)

# 도메인 리뷰 카드
## 1) [도메인] — 상위 앵커: *[통합지식 anchor]*
* **장점**: ... (anchored_by: [통합지식 anchor])
* **문제**: ... (anchored_by: [anchor])
* **조건**: ... (anchored_by: [anchor])

(4개 도메인 반복)

# 통합 기록 (긴장 축)
1. **극A** × **극B** (상충/경계/대립)
2. ...

> **결론 1줄**: 핵심을 관통하는 문장

# 최종 1p 제안서 ({format_type} 판)

## 제목
**〈구체적이고 매력적인 제목〉**

## 로그라인
"핵심 메시지를 1-2문장으로..."

## 대상
구체적인 타겟 독자/시청자

## 핵심 약속(Core Promise)
* 독자/시청자에게 제공할 구체적 가치
* 모든 주장은 KB 앵커로 뒷받침

## 포맷
매체 형식 (매거진 기사, 영상, 책 등)

## 구성(섹션/시퀀스)
1. 섹션1: ... (anchored_by: [anchor])
2. 섹션2: ... (anchored_by: [anchor])
(구체적 구성안)

## 고유 문장(3) — "이 책 아니면 안 나오는 문장"
1. **"강력하고 인상적인 문장..."** (anchored_by: [anchor])
2. **"독창적이고 기억에 남는 문장..."** (anchored_by: [anchor])
3. **"핵심을 관통하는 문장..."** (anchored_by: [anchor])

## CTA
"독자를 행동으로 이끄는 문장"

**중요 규칙:**
1. 모든 문장에 [anchor_id] 포함
2. **가짜 앵커 생성 절대 금지** → 제공된 KB 앵커만 사용
3. 통합지식 앵커 필수 사용
4. 일반론 금지, 책의 구체적 내용 반영
5. 외부 프레임워크 언급 금지

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
    
    # 입력 리뷰 로깅 (디버깅용)
    logger.info(f"[INPUT] Producer received reviews (first 600 chars):")
    logger.info(review_summary[:600])

    # 사용 가능한 앵커 리스트 (처음 50개만 예시로 제공)
    anchor_list = "\n".join([f"- {a}" for a in available_anchors[:50]])
    if len(available_anchors) > 50:
        anchor_list += f"\n... 외 {len(available_anchors) - 50}개 더"
    
    # 책 요약 첫 300자 (출발지식 섹션용)
    summary_preview = book_summary[:300] + ("..." if len(book_summary) > 300 else "")
    
    user_prompt = f"""**출발지식 (반드시 맨 위에 포함):**
일련번호: {book_id}
제목: {book_title}
저자: {book_author}
주제: {book_topic}
요약: {summary_preview}

---

4개 도메인 리뷰:
{review_summary}

통합 결과:
{integration_result}

**사용 가능한 KB 앵커 (이것만 사용!):**
{anchor_list}

**경고**: 위 목록에 없는 앵커를 절대 생성하지 마세요! 
예를 들어 "투자전략_최적화_001" 같은 가짜 앵커는 절대 금지입니다.
반드시 위 리스트에 있는 앵커만 사용하세요.

위 출발지식과 리뷰를 바탕으로 {format_type} 형식의 완전한 1p 제안서를 작성하세요.

**필수 섹션 (반드시 순서대로 모두 포함!):**

1. # 출발 지식 (위 정보 그대로)
2. # 형식 분기 (선정 사유 1줄 - 책의 구체적 내용 기반)
3. # 도메인 리뷰 카드 (4개 도메인별로 장점/문제/조건 포함)
4. # 통합 기록 (긴장축 2-3개 + 결론 1줄)
5. # 최종 1p 제안서 (7요소: 제목/로그라인/대상/약속/포맷/구성/고유문장/CTA)

**중요:**
- 모든 문장에 [anchor_id] 포함
- 도메인 리뷰 카드와 통합 기록 섹션 절대 생략 금지!"""

    try:
        response = llm.invoke(
            [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        )
        
        # 토큰 사용량 로깅
        usage = response.response_metadata.get('usage', {})
        logger.info(f"[TOKEN] Producer: "
                   f"model={models_config.PRODUCER_MODEL}, "
                   f"input={usage.get('prompt_tokens', 0)}, "
                   f"output={usage.get('completion_tokens', 0)}, "
                   f"total={usage.get('total_tokens', 0)}")

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
