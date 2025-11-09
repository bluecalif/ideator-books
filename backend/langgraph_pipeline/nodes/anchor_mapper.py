"""AnchorMapper Node - 도서 요약을 4개 도메인별 앵커에 매핑"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from backend.langgraph_pipeline.state import OnePagerState
from backend.services.kb_service import kb_service
from backend.core.models_config import models_config
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# 도메인 리스트
DOMAINS = ["경제경영", "과학기술", "역사사회", "인문자기계발"]


def anchor_mapper_node(state: OnePagerState) -> Dict[str, Any]:
    """
    AnchorMapper 노드

    역할:
    1. 도서 요약을 분석
    2. 4개 도메인별로 KB 검색
    3. 각 도메인당 가장 관련 있는 앵커 1개 선택
    4. 합치/상충/누락/경계 분석

    Args:
        state: OnePagerState

    Returns:
        부분 state 업데이트
    """
    logger.info("[START] AnchorMapper")
    
    book_ids = state.get("book_ids", [])
    
    # 1권만 처리 (PRD 요구사항)
    if not book_ids:
        logger.error("[FAIL] No book_ids provided")
        return {"error_message": "No book_ids provided"}
    
    # 첫 번째 책만 사용 (1권당 1p)
    book_id = book_ids[0]
    
    # 단일 책 요약 직접 사용
    book_summary = state.get("book_summary", "")
    book_title = state.get("book_title", f"Book {book_id}")
    
    # 디버그 로그
    logger.info(f"[DEBUG] AnchorMapper received:")
    logger.info(f"  Book ID: {book_id}")
    logger.info(f"  Book Title: {book_title}")
    logger.info(f"  Summary length: {len(book_summary)} chars")
    logger.info(f"  Summary preview: {book_summary[:200]}...")
    
    if not book_summary or len(book_summary) < 10:
        logger.error("[FAIL] Book summary is empty or too short!")
        return {"error_message": "No valid book summary provided"}

    # 각 도메인별 앵커 찾기
    anchors = {}
    anchor_details = []

    for domain in DOMAINS:
        # KB 검색 (단일 책 요약 사용)
        results = kb_service.search(query=book_summary, domain=domain, top_k=3)

        if results:
            # 가장 유사도 높은 앵커 선택
            best_result = results[0]
            anchors[domain] = best_result.item.anchor_id

            anchor_details.append(
                {
                    "domain": domain,
                    "anchor_id": best_result.item.anchor_id,
                    "content": best_result.item.content[:100] + "...",
                    "score": best_result.similarity_score,
                    "is_fusion": best_result.item.is_fusion,
                }
            )

            logger.info(
                f"[OK] {domain}: {best_result.item.anchor_id} "
                f"(score: {best_result.similarity_score:.3f})"
            )
        else:
            logger.warning(f"[WARN] {domain}: No anchor found")
            anchors[domain] = f"{domain}_default_001"

    # 앵커 분석 (LLM 사용)
    anchor_analysis = analyze_anchors(anchor_details, book_summary)
    
    # 사용 가능한 모든 KB 앵커 리스트 (가짜 앵커 방지용)
    available_anchors = [item.anchor_id for item in kb_service.all_items]
    logger.info(f"[OK] Available anchors: {len(available_anchors)} items")

    logger.info("[DONE] AnchorMapper")

    return {
        "anchors": anchors,
        "anchor_analysis": anchor_analysis,
        "available_anchors": available_anchors,
        "messages": [
            HumanMessage(
                content=f"Mapped anchors: {anchors}\nAnalysis: {anchor_analysis}",
                name="AnchorMapper",
            )
        ],
    }


def analyze_anchors(anchor_details: list[Dict], book_summary: str) -> str:
    """
    앵커 간 관계 분석 (합치/상충/누락/경계)

    Args:
        anchor_details: 도메인별 선택된 앵커 상세
        book_summary: 도서 요약

    Returns:
        분석 결과 (합치/상충/누락/경계)
    """
    llm = ChatOpenAI(model=models_config.ANCHOR_MAPPER_MODEL, temperature=models_config.ANCHOR_MAPPER_TEMP)

    # 앵커 내용 요약
    anchor_summary = "\n".join(
        [
            f"- {a['domain']}: {a['content']} (융합형: {a['is_fusion']})"
            for a in anchor_details
        ]
    )

    system_prompt = """당신은 4개 도메인(경제경영, 과학기술, 역사사회, 인문자기계발)의 앵커 간 관계를 분석하는 전문가입니다.

다음 4가지를 분석하세요:
1. **합치**: 어떤 앵커들이 유사한 방향을 가리키는가?
2. **상충**: 어떤 앵커들이 서로 모순되거나 대립하는가?
3. **누락**: 도서 요약에 비해 빠진 관점은 무엇인가?
4. **경계**: 앵커가 적용 가능한 범위와 한계는?

간결하게 3-4줄로 요약하세요."""

    user_prompt = f"""도서 요약:
{book_summary}

선택된 앵커:
{anchor_summary}

분석을 제공하세요."""

    messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]

    try:
        response = llm.invoke(messages)
        
        # 토큰 사용량 로깅 (로그 파일만)
        usage = response.response_metadata.get('usage', {})
        logger.info(f"[TOKEN] AnchorMapper: "
                   f"model={models_config.ANCHOR_MAPPER_MODEL}, "
                   f"input={usage.get('prompt_tokens', 0)}, "
                   f"output={usage.get('completion_tokens', 0)}, "
                   f"total={usage.get('total_tokens', 0)}")
        
        return response.content
    except Exception as e:
        logger.error(f"[FAIL] Anchor analysis error: {e}")
        return "분석 실패: LLM 호출 오류"
