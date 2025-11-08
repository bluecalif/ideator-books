"""Utility functions for LangGraph nodes"""
from langchain_core.messages import HumanMessage, AIMessage
from backend.langgraph_pipeline.state import OnePagerState
from typing import Dict, Any, Callable
import functools
import logging

logger = logging.getLogger(__name__)


def agent_node(state: OnePagerState, agent: Any, name: str) -> Dict[str, Any]:
    """
    ReAct Agent를 LangGraph 노드로 래핑하는 헬퍼 함수
    
    사용 예시:
    ```python
    reviewer_agent = create_react_agent(llm, tools=[kb_search_tool])
    reviewer_node = functools.partial(
        agent_node,
        agent=reviewer_agent,
        name="Reviewer_경제경영"
    )
    workflow.add_node("review_economics", reviewer_node)
    ```
    
    Args:
        state: OnePagerState
        agent: create_react_agent로 생성된 agent
        name: 노드 이름
    
    Returns:
        부분 state 업데이트 (messages 추가)
    """
    try:
        # Agent 실행
        response = agent.invoke(state)
        
        # 응답 메시지 추출
        last_message = response["messages"][-1]
        
        # State 업데이트
        return {
            "messages": [
                HumanMessage(
                    content=last_message.content,
                    name=name
                )
            ],
            "current_node": name
        }
    
    except Exception as e:
        logger.error(f"[FAIL] Agent node '{name}' error: {e}")
        return {
            "error_message": f"Error in {name}: {str(e)}",
            "current_node": name
        }


def create_node_wrapper(func: Callable) -> Callable:
    """
    일반 함수를 LangGraph 노드로 래핑하는 데코레이터
    
    사용 예시:
    ```python
    @create_node_wrapper
    def anchor_mapper(state: OnePagerState) -> Dict[str, Any]:
        # 노드 로직
        return {"anchors": {...}}
    ```
    """
    @functools.wraps(func)
    def wrapper(state: OnePagerState) -> Dict[str, Any]:
        node_name = func.__name__
        logger.info(f"[START] Node: {node_name}")
        
        try:
            result = func(state)
            result["current_node"] = node_name
            logger.info(f"[OK] Node: {node_name}")
            return result
        
        except Exception as e:
            logger.error(f"[FAIL] Node '{node_name}' error: {e}")
            return {
                "error_message": f"Error in {node_name}: {str(e)}",
                "current_node": node_name
            }
    
    return wrapper


def log_state_transition(state: OnePagerState, node_name: str):
    """State 전환 로깅"""
    logger.debug(
        f"[STATE] {node_name} | "
        f"Books: {len(state.get('book_ids', []))} | "
        f"Reviews: {len(state.get('reviews', []))} | "
        f"Messages: {len(state.get('messages', []))}"
    )


def validate_state_requirements(
    state: OnePagerState,
    required_fields: list[str],
    node_name: str
) -> bool:
    """
    노드 실행 전 필수 필드 검증
    
    Args:
        state: 현재 State
        required_fields: 필수 필드 목록
        node_name: 노드 이름
    
    Returns:
        검증 통과 여부
    """
    missing = [field for field in required_fields if not state.get(field)]
    
    if missing:
        logger.error(
            f"[FAIL] {node_name} missing required fields: {missing}"
        )
        return False
    
    return True


def format_review_for_integrator(reviews: list[Dict]) -> str:
    """
    Reviewer 결과를 Integrator가 읽기 쉬운 형식으로 변환
    
    Args:
        reviews: Reviewer 노드들의 결과 리스트
    
    Returns:
        포맷된 텍스트
    """
    formatted = []
    for review in reviews:
        domain = review.get("domain", "Unknown")
        formatted.append(f"## {domain} 도메인 리뷰")
        formatted.append(f"**장점**: {review.get('advantages', 'N/A')}")
        formatted.append(f"**문제**: {review.get('problems', 'N/A')}")
        formatted.append(f"**조건**: {review.get('conditions', 'N/A')}")
        formatted.append(f"**참조**: [{review.get('anchor_id', 'N/A')}]")
        formatted.append("")
    
    return "\n".join(formatted)


def extract_anchor_ids(text: str) -> list[str]:
    """
    텍스트에서 [anchor_id] 패턴 추출
    
    Args:
        text: 1p 텍스트
    
    Returns:
        anchor_id 리스트
    """
    import re
    pattern = r'\[([^\]]+)\]'
    matches = re.findall(pattern, text)
    return matches


def calculate_anchored_by_percent(text: str) -> float:
    """
    anchored_by 비율 계산
    
    각 문장이 [anchor_id]를 가지고 있는지 확인
    
    Args:
        text: 1p 텍스트
    
    Returns:
        anchored_by 비율 (0.0 ~ 1.0)
    """
    import re
    
    # 문장 분리 (간단한 구현)
    sentences = [s.strip() for s in re.split(r'[.!?]\s+', text) if s.strip()]
    
    if not sentences:
        return 0.0
    
    # [anchor_id]를 포함한 문장 카운트
    anchored_count = sum(1 for s in sentences if re.search(r'\[([^\]]+)\]', s))
    
    return anchored_count / len(sentences)

