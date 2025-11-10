"""Reviewer Nodes - 4개 도메인별 리뷰 에이전트"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from backend.langgraph_pipeline.state import OnePagerState
from backend.tools.kb_search import create_kb_search_tool
from backend.langgraph_pipeline.utils import agent_node
from backend.core.models_config import models_config
from backend.services.kb_service import kb_service
from pydantic import BaseModel, Field
from typing import Dict, Any
import functools
import logging

logger = logging.getLogger(__name__)


class DomainReview(BaseModel):
    """도메인 리뷰 구조화 출력"""
    advantages: str = Field(
        ..., 
        description="이 책의 [구체적 내용]은 앵커 관점에서... (2-3문장, 반드시 책의 구체적 사례 명시, 앵커 포함)"
    )
    problems: str = Field(
        ..., 
        description="하지만 이 책의 [특정 부분]은... (2-3문장, 구체적 문제점, 앵커 포함)"
    )
    conditions: str = Field(
        ..., 
        description="이 책의 아이디어가 성공하려면... (2-3문장, 실행 조건, 앵커 포함)"
    )

# KB 검색 도구
kb_search_tool = create_kb_search_tool()


def create_reviewer_prompt(domain: str) -> str:
    """
    도메인별 Reviewer 프롬프트 생성 (품질 개선 버전)
    
    Args:
        domain: 도메인 (경제경영/과학기술/역사사회/인문자기계발)
    
    Returns:
        Enhanced system prompt
    """
    return f"""당신은 **{domain}** 도메인 전문가입니다.

**목표**: 주어진 도서를 **깊이 있게 분석**하여, {domain} 관점의 구체적인 리뷰를 제공합니다.

**프로세스**:
1. **책의 핵심 메시지 정확히 파악** - 책이 실제로 말하는 것이 무엇인지
2. **KB 검색** (kb_search 도구 사용) - 관련 인사이트 찾기
   - **통합지식 우선 활용**: "통합지식" 포함된 앵커를 최우선으로 사용
   - 융합형 인사이트도 우선 고려
3. **책 내용과 KB를 구체적으로 연결** - 일반론 금지

**출력 형식** (각 섹션 2-3문장):

**장점**: 이 책의 [구체적 내용/주장]은 [{domain}·[소분류] 통합지식] 관점에서 볼 때 ... (구체적 연결). 예를 들어 ... (책의 예시/사례와 KB 연결).

**문제**: 하지만 책의 [특정 부분/한계]는 [anchor_id] 관점에서 볼 때 ... (구체적 문제점). 이는 ... (왜 문제인지 설명).

**조건**: 이 책의 아이디어가 성공하려면 [anchor_id]에서 말하는 [구체적 조건]이 필요합니다. 구체적으로 ... (실행 가능한 조건).

**핵심 규칙**:
1. **통합지식 앵커 1개 이상 필수 사용**
2. **책의 구체적 내용 명시** - "이 책은 ..."이 아니라 "이 책의 X 부분에서 Y라고 주장하는데 ..."
3. **일반론 금지** - "도움이 된다", "중요하다" 같은 추상적 표현 대신 구체적 분석
4. **모든 문장에 [anchor_id] 포함**
"""


def review_domain_node(state: OnePagerState, domain: str = None) -> Dict[str, Any]:
    """
    특정 도메인에 대한 리뷰 수행
    
    Args:
        state: OnePagerState
        domain: 도메인 (None이면 state['current_domain'] 사용)
    
    Returns:
        부분 state 업데이트
    """
    # domain이 None이면 state에서 가져오기 (Send() API 사용 시)
    if domain is None:
        domain = state.get("current_domain", "경제경영")
    
    logger.info(f"[START] Reviewer_{domain}")
    
    # 입력 준비
    anchor_id = state.get("anchors", {}).get(domain, "")
    book_ids = state.get("book_ids", [])
    
    # 1권만 처리
    if not book_ids:
        logger.error(f"[{domain}] No book_ids provided")
        # error_message는 반환하지 않음 (병렬 실행 시 충돌 방지)
        return {"messages": [HumanMessage(content=f"[{domain}] Error: No book_ids", name=f"Reviewer_{domain}")]}
    
    book_id = book_ids[0]
    
    # 단일 책 요약 직접 사용
    book_summary = state.get("book_summary", "")
    book_title = state.get("book_title", f"Book {book_id}")
    book_topic = state.get("book_topic", "주제 없음")
    
    # 디버그 로그
    logger.info(f"[DEBUG] Reviewer_{domain} received:")
    logger.info(f"  Book: {book_title}")
    logger.info(f"  Topic: {book_topic}")
    logger.info(f"  Summary length: {len(book_summary)} chars")
    logger.info(f"  Summary preview: {book_summary[:150]}...")
    
    if not book_summary:
        logger.error(f"[FAIL] Reviewer_{domain}: No book summary!")
        return {"error_message": f"[{domain}] No book summary provided"}
    
    # KB 추가 검색 (책 요약 기반)
    additional_kb = kb_service.search(book_summary, domain=domain, top_k=3)
    additional_insights = "\n".join([
        f"- [{kb.item.anchor_id}] {kb.item.content[:100]}..."
        for kb in additional_kb
    ])
    
    # Structured LLM 생성 (GPT-5 시리즈는 temperature=1.0 자동 적용)
    llm = ChatOpenAI(
        model=models_config.REVIEWER_MODEL, 
        temperature=models_config.get_temperature("reviewer")
    )
    structured_llm = llm.with_structured_output(DomainReview)
    
    system_prompt = f"""{create_reviewer_prompt(domain)}

**중요 규칙:**
1. 반드시 "이 책의 [구체적 내용]은..." 형식으로 시작
2. 모든 문장에 [anchor_id] 포함
3. 일반론 금지, 책의 구체적 사례만 사용"""
    
    user_prompt = f"""**할당된 {domain} 앵커 (평가 기준):**
{anchor_id}

**분석 대상 (출발지식):**
제목: {book_title}
주제: {book_topic}

핵심 내용:
{book_summary}

**추가 참조 가능 KB:**
{additional_insights}

---

위 책을 할당된 앵커 관점에서 평가하여 advantages, problems, conditions를 작성하세요.
반드시 "이 책의 [구체적 부분]은..." 형식으로 시작하고, 모든 문장에 [anchor_id]를 포함하세요."""
    
    # Structured output 실행
    try:
        response = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # 토큰 사용량 로깅
        usage = response.__dict__.get('response_metadata', {}).get('usage', {})
        logger.info(f"[TOKEN] Reviewer_{domain}: "
                   f"model={models_config.REVIEWER_MODEL}, "
                   f"input={usage.get('prompt_tokens', 0)}, "
                   f"output={usage.get('completion_tokens', 0)}, "
                   f"total={usage.get('total_tokens', 0)}")
        
        # 구조화된 출력 확인
        logger.info(f"[STRUCTURED] Reviewer_{domain}:")
        logger.info(f"  장점 (first 150 chars): {response.advantages[:150]}...")
        logger.info(f"  문제 (first 150 chars): {response.problems[:150]}...")
        logger.info(f"  조건 (first 150 chars): {response.conditions[:150]}...")
        
        review = {
            "domain": domain,
            "anchor_id": anchor_id,
            "advantages": response.advantages,
            "problems": response.problems,
            "conditions": response.conditions,
            "raw_content": f"장점: {response.advantages}\n\n문제: {response.problems}\n\n조건: {response.conditions}"
        }
        
        logger.info(f"[DONE] Reviewer_{domain}")
        
        return {
            "reviews": [review],
            "messages": [
                HumanMessage(
                    content=f"[{domain}] Review completed",
                    name=f"Reviewer_{domain}"
                )
            ]
        }
    
    except Exception as e:
        logger.error(f"[FAIL] Reviewer_{domain} error: {e}")
        return {
            "reviews": [{
                "domain": domain,
                "anchor_id": anchor_id,
                "error": str(e)
            }],
            "error_message": f"Reviewer_{domain} failed: {str(e)}"
        }


# functools.partial로 각 도메인별 노드 생성
def create_reviewer_nodes():
    """
    4개 도메인별 Reviewer 노드 생성
    
    Returns:
        {domain: node_function} 딕셔너리
    """
    nodes = {}
    for domain in DOMAINS:
        nodes[domain] = functools.partial(review_domain_node, domain=domain)
    
    return nodes


# 개별 노드 함수 (그래프에 추가할 때 사용)
reviewer_economics = functools.partial(review_domain_node, domain="경제경영")
reviewer_science = functools.partial(review_domain_node, domain="과학기술")
reviewer_history = functools.partial(review_domain_node, domain="역사사회")
reviewer_humanities = functools.partial(review_domain_node, domain="인문자기계발")

