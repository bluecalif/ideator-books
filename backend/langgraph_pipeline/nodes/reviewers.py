"""Reviewer Nodes - 4개 도메인별 리뷰 에이전트"""
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import SystemMessage, HumanMessage
from backend.langgraph_pipeline.state import OnePagerState
from backend.tools.kb_search import create_kb_search_tool
from backend.langgraph_pipeline.utils import agent_node
from typing import Dict, Any
import functools
import logging

logger = logging.getLogger(__name__)

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
    
    # LLM 및 Agent 생성
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    # Agent 생성 (system prompt는 user message에 포함)
    agent = create_react_agent(
        llm,
        tools=[kb_search_tool]
    )
    
    # 입력 준비
    anchor_id = state.get("anchors", {}).get(domain, "")
    book_ids = state.get("book_ids", [])
    
    # 1권만 처리
    if not book_ids:
        return {"error_message": f"[{domain}] No book_ids provided"}
    
    book_id = book_ids[0]
    
    # 단일 책 요약 직접 사용
    book_summary = state.get("book_summary", "")
    book_title = state.get("book_title", f"Book {book_id}")
    
    # 디버그 로그
    logger.info(f"[DEBUG] Reviewer_{domain} received:")
    logger.info(f"  Book: {book_title}")
    logger.info(f"  Summary length: {len(book_summary)} chars")
    logger.info(f"  Summary preview: {book_summary[:150]}...")
    
    if not book_summary:
        logger.error(f"[FAIL] Reviewer_{domain}: No book summary!")
        return {"error_message": f"[{domain}] No book summary provided"}
    
    user_message = f"""{create_reviewer_prompt(domain)}

---

도서 요약:
{book_summary}

할당된 앵커: {anchor_id}

위 앵커를 기반으로 {domain} 관점에서 장점, 문제, 조건을 분석하세요.
kb_search 도구를 사용하여 관련 KB 인사이트를 찾아 활용하세요."""
    
    # Agent 실행
    try:
        response = agent.invoke({
            "messages": [HumanMessage(content=user_message)]
        })
        
        review_content = response["messages"][-1].content
        
        # 리뷰 결과 파싱 (간단한 구현)
        review = {
            "domain": domain,
            "anchor_id": anchor_id,
            "advantages": extract_section(review_content, "장점"),
            "problems": extract_section(review_content, "문제"),
            "conditions": extract_section(review_content, "조건"),
            "raw_content": review_content
        }
        
        logger.info(f"[DONE] Reviewer_{domain}")
        
        return {
            "reviews": [review],
            "messages": [
                HumanMessage(
                    content=f"[{domain}] Review completed\n{review_content[:200]}...",
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


def extract_section(text: str, section_name: str) -> str:
    """
    리뷰 텍스트에서 특정 섹션 추출
    
    Args:
        text: 리뷰 전체 텍스트
        section_name: 섹션 이름 (장점/문제/조건)
    
    Returns:
        해당 섹션 내용
    """
    import re
    
    # **장점**: 내용 형식 찾기
    pattern = rf'\*\*{section_name}\*\*[:\s]*(.+?)(?=\*\*|$)'
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return f"{section_name} 내용 추출 실패"


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

