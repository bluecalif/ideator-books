"""LangGraph Workflow Definition"""
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import Send
from backend.langgraph_pipeline.state import OnePagerState
from backend.langgraph_pipeline.nodes.anchor_mapper import anchor_mapper_node
from backend.langgraph_pipeline.nodes.reviewers import (
    reviewer_economics,
    reviewer_science,
    reviewer_history,
    reviewer_humanities,
    review_domain_node
)
from backend.langgraph_pipeline.nodes.integrator import integrator_node
from backend.langgraph_pipeline.nodes.producer import producer_node
from backend.langgraph_pipeline.nodes.validator import validator_node
import logging

logger = logging.getLogger(__name__)


def create_workflow() -> StateGraph:
    """
    1p 생성 LangGraph 워크플로우 생성
    
    노드 구조:
    START → AnchorMapper → [Review_경제경영, Review_과학기술, Review_역사사회, Review_인문자기계발]
         → Integrator → Producer → Validator → END
    
    Validator 실패 시 → AnchorMapper로 재시도
    """
    # StateGraph 생성
    workflow = StateGraph(OnePagerState)
    
    # 노드 추가
    workflow.add_node("anchor_mapper", anchor_mapper_node)
    workflow.add_node("review_domain", review_domain_node)
    workflow.add_node("integrator", integrator_node)
    workflow.add_node("producer", producer_node)
    workflow.add_node("validator", validator_node)
    
    # 엣지 연결
    workflow.add_edge(START, "anchor_mapper")
    
    # AnchorMapper → 4개 Reviewer (병렬)
    workflow.add_conditional_edges(
        "anchor_mapper",
        initiate_reviews,  # Send() API로 4개 Reviewer 병렬 실행
        ["review_domain"]
    )
    
    # 모든 Reviewer → Integrator
    workflow.add_edge("review_domain", "integrator")
    
    # 순차 실행
    workflow.add_edge("integrator", "producer")
    workflow.add_edge("producer", "validator")
    
    # Validator → 재시도 또는 종료
    workflow.add_conditional_edges(
        "validator",
        should_retry,
        {True: END, False: "anchor_mapper"}
    )
    
    logger.info("[OK] Workflow structure defined with all nodes connected")
    return workflow


def compile_graph(workflow: StateGraph, use_checkpointer: bool = True):
    """
    그래프 컴파일
    
    Args:
        workflow: StateGraph 인스턴스
        use_checkpointer: 체크포인터 사용 여부 (재시도 기능)
    
    Returns:
        컴파일된 그래프
    """
    if use_checkpointer:
        memory = MemorySaver()
        graph = workflow.compile(checkpointer=memory)
        logger.info("[OK] Graph compiled with checkpointer (retry enabled)")
    else:
        graph = workflow.compile()
        logger.info("[OK] Graph compiled without checkpointer")
    
    return graph


def initiate_reviews(state: OnePagerState):
    """
    4개 도메인 Reviewer를 병렬로 시작 (Send() API)
    
    Returns:
        Send() 명령 리스트
    """
    domains = ["경제경영", "과학기술", "역사사회", "인문자기계발"]
    
    return [
        Send(
            "review_domain",
            {
                **state,
                "current_domain": domain  # 각 Reviewer가 자신의 도메인 알 수 있게
            }
        )
        for domain in domains
    ]


def should_retry(state: OnePagerState) -> bool:
    """
    Validator 후 항상 종료 (재시도 없음)
    
    Returns:
        항상 True (END)
    """
    validation_passed = state.get("validation_passed", False)
    anchored_by = state.get("anchored_by_percent", 0)
    
    if validation_passed:
        logger.info("[SUCCESS] Validation passed → END")
    else:
        logger.warning(
            f"[WARN] Validation failed (anchored: {anchored_by:.1%}) "
            f"but proceeding to END (no retry)"
        )
    
    return True  # 항상 종료


# Global workflow and graph instances (lazy initialization)
_workflow = None
_graph = None


def get_graph():
    """
    Graph 인스턴스 가져오기 (lazy initialization)
    
    모듈 캐싱 문제를 방지하고 최신 노드 코드를 반영
    """
    global _workflow, _graph
    
    if _graph is None:
        logger.info("[INFO] Initializing graph (first time)...")
        _workflow = create_workflow()
        _graph = compile_graph(_workflow, use_checkpointer=True)
        logger.info("[OK] Graph initialized")
    
    return _graph


# Backward compatibility
graph = get_graph()

