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
    - 1p 제안서 창작 (제목, 로그라인, 대상, 핵심 약속, 포맷, 구성, 고유문장, CTA)
    - Input: integration_result (긴장축) + book_summary (책 요약)만 사용
    - 조립 로직은 별도 함수에서 처리
    
    Args:
        state: OnePagerState
    
    Returns:
        부분 state 업데이트
    """
    logger.info("[START] Producer")
    
    integration_result = state.get("integration_result", "")
    book_summary = state.get("book_summary", "")
    available_anchors = state.get("available_anchors", [])
    
    if not integration_result or not book_summary:
        logger.error("[FAIL] Missing integration_result or book_summary")
        return {"error_message": "Producer requires integration_result and book_summary"}
    
    if not available_anchors:
        logger.warning("[WARN] No available_anchors provided - fake anchor prevention may not work")
    
    # 1p 제안서 생성 (LLM 창작)
    proposal_md = create_onepager_proposal(
        integration_result=integration_result,
        book_summary=book_summary,
        available_anchors=available_anchors
    )
    
    # 고유문장 추출
    unique_sentences = extract_unique_sentences(proposal_md)
    
    logger.info(
        f"[DONE] Producer (Proposal generated, {len(unique_sentences)} unique sentences)"
    )
    
    return {
        "onepager_proposal": proposal_md,  # 1p 제안서 (제목~CTA)
        "unique_sentences": unique_sentences,
        "messages": [
            HumanMessage(
                content=f"[Producer] Proposal created ({len(proposal_md)} chars, {len(unique_sentences)} unique sentences)",
                name="Producer",
            )
        ],
    }


def create_onepager_proposal(
    integration_result: str,
    book_summary: str,
    available_anchors: list[str]
) -> str:
    """
    1p 제안서 생성 (LLM 창작)
    
    역할:
    - integration_result (긴장축 + 결론)와 book_summary만 사용
    - 1p 제안서 7요소만 창작: 제목, 로그라인, 대상, 핵심 약속, 포맷, 구성, 고유문장, CTA
    
    Args:
        integration_result: Integrator 출력 (긴장축 + 형식 분기 + 결론)
        book_summary: 책 요약
        available_anchors: 사용 가능한 KB 앵커 리스트
    
    Returns:
        1p 제안서 Markdown (제목~CTA)
    """
    llm = ChatOpenAI(
        model=models_config.PRODUCER_MODEL, 
        temperature=models_config.get_temperature("producer")
    )

    system_prompt = """당신은 전문가 수준의 1p 제안서를 작성하는 전문가입니다.

**역할**: 제공된 통합 지식(긴장축)과 책 요약을 바탕으로 1p 제안서 7요소를 창작합니다.

**출력 형식 (이 구조 그대로!):**

# 최종 1p 제안서

## 제목
**〈구체적이고 매력적인 제목〉**

## 로그라인
"핵심 메시지를 1-2문장으로..."

## 대상
구체적인 타겟 독자/시청자

## 핵심 약속(Core Promise)
* 독자에게 제공할 구체적 가치 (긴장축의 종합에서 도출)
* 모든 주장은 KB 앵커로 뒷받침

## 포맷
매체 형식 (매거진 기사, 영상, 책 등)

## 구성(섹션/시퀀스)
1. 섹션1: ... [anchor]
2. 섹션2: ... [anchor]
(책의 주요 내용을 긴장축 순서로 구성)

## 고유 문장(3) — "이 책 아니면 안 나오는 문장"
1. **"강력하고 인상적인 문장..."** [anchor]
2. **"독창적이고 기억에 남는 문장..."** [anchor]
3. **"핵심을 관통하는 문장..."** [anchor]

## CTA
"독자를 행동으로 이끄는 문장"

**중요 규칙:**
1. 모든 문장에 [anchor_id] 포함 (한 번에 하나씩!)
2. 여러 앵커를 쉼표로 연결 금지!
3. 제공된 KB 앵커만 사용 (가짜 앵커 생성 금지)
4. 책의 구체적 내용을 반영 (일반론 금지)"""

    # 입력 로깅
    logger.info(f"[INPUT] Producer received:")
    logger.info(f"  Integration result length: {len(integration_result)} chars")
    logger.info(f"  Book summary length: {len(book_summary)} chars")
    
    # integration_result에서 사용된 앵커 추출
    import re
    used_anchors = re.findall(r'\[([^\]]+)\]', integration_result)
    used_anchors_unique = list(dict.fromkeys(used_anchors))  # 중복 제거, 순서 유지
    
    # 사용된 앵커 우선 리스트
    priority_anchors = "\n".join([f"- {a} (통합에서 사용됨)" for a in used_anchors_unique[:10]])
    
    # 추가 사용 가능 앵커
    additional_anchors = [a for a in available_anchors if a not in used_anchors_unique][:20]
    additional_list = "\n".join([f"- {a}" for a in additional_anchors])
    
    user_prompt = f"""**통합 지식 (Integrator 결과):**
{integration_result}

**책 요약:**
{book_summary}

---

**우선 사용할 앵커 (통합 지식에서 이미 사용됨):**
{priority_anchors}

**추가 사용 가능 앵커:**
{additional_list}

---

위 통합 지식과 책 요약을 바탕으로 **1p 제안서 7요소만** 창작하세요.

**중요 규칙:**
1. **우선 사용할 앵커**를 최대한 사용하세요 (통합 지식과 연결성 유지)
2. 긴장축의 "종합" 부분에서 핵심 약속을 도출하세요
3. 책의 독특한 내용(사례, 주장)에서 고유문장을 만드세요
4. 모든 문장에 [anchor_id] 포함 (한 번에 하나씩!)
5. 여러 앵커를 쉼표로 연결 절대 금지!
6. 위 목록에 없는 가짜 앵커 생성 절대 금지!"""

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
    - "고유문장" 또는 "고유 문장" 섹션에 명시적으로 포함된 문장들
    - 괄호 포함 형식도 지원 (예: "고유 문장(3)")

    Args:
        onepager_md: 1p Markdown 텍스트

    Returns:
        고유문장 리스트
    """
    # "고유문장" 또는 "고유 문장(3)" 섹션 찾기 (더 유연한 패턴)
    pattern = r"##?\s*고유.*?문장.*?\n(.*?)(?=\n##|\Z)"
    match = re.search(pattern, onepager_md, re.DOTALL | re.IGNORECASE)

    if match:
        section_text = match.group(1)
        # 번호 목록 파싱 (1. 2. 3. 또는 - 또는 *)
        # 각 항목은 번호/기호로 시작하고, 다음 번호/기호 또는 섹션 끝까지 이어짐
        sentences = re.findall(
            r"(?:^|\n)\s*(?:\d+\.|[-*])\s*\*?\*?(.+?)(?=\n\s*\d+\.|\n\s*[-*]|\n\n|\Z)",
            section_text,
            re.DOTALL,
        )
        
        # 정리: 앞뒤 공백, 마크다운 bold (**), 앵커 태그 제거하여 순수 문장만 추출
        cleaned_sentences = []
        for s in sentences:
            # bold 마크 제거
            cleaned = re.sub(r'\*\*(.+?)\*\*', r'\1', s)
            # 앵커 태그 제거
            cleaned = re.sub(r'\(anchored_by:.*?\)', '', cleaned)
            cleaned = re.sub(r'\[.*?\]', '', cleaned)
            # 공백 정리
            cleaned = cleaned.strip()
            if cleaned and len(cleaned) > 10:  # 너무 짧은 문장 제외
                cleaned_sentences.append(cleaned)
        
        if cleaned_sentences:
            logger.info(f"[OK] Extracted {len(cleaned_sentences)} unique sentences")
            return cleaned_sentences

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
