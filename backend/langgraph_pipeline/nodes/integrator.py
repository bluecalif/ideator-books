"""Integrator Node - 4개 리뷰를 통합"""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from pydantic import BaseModel, Field
from typing import List, Optional
from backend.langgraph_pipeline.state import OnePagerState
from backend.langgraph_pipeline.utils import format_review_for_integrator
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TensionAxis(BaseModel):
    """긴장축 (Reduce 모드용)"""
    axis_name: str = Field(..., description="긴장축 이름 (예: 효율성 vs 윤리)")
    pole_a: str = Field(..., description="한쪽 극 설명")
    pole_b: str = Field(..., description="반대쪽 극 설명")
    synthesis: str = Field(..., description="종합/균형점")


class IntegrationResult(BaseModel):
    """Integrator 결과 (Reduce 모드용)"""
    tension_axes: List[TensionAxis] = Field(..., min_length=2, max_length=3)
    format_reasoning: str = Field(..., description="형식(콘텐츠/서비스) 분기 사유")
    conclusion: str = Field(..., description="최종 결론 1줄")


def integrator_node(state: OnePagerState) -> Dict[str, Any]:
    """
    Integrator 노드
    
    역할:
    - Reduce 모드: 4개 리뷰 → 긴장축 2-3개 추출
    - Simple Merge 모드: 4개 리뷰 병치 + 결론
    
    Args:
        state: OnePagerState
    
    Returns:
        부분 state 업데이트
    """
    logger.info("[START] Integrator")
    
    mode = state.get("mode", "reduce")
    reviews = state.get("reviews", [])
    format_type = state.get("format", "content")
    
    if not reviews:
        logger.error("[FAIL] No reviews to integrate")
        return {
            "error_message": "No reviews available for integration"
        }
    
    # 리뷰 포맷팅
    formatted_reviews = format_review_for_integrator(reviews)
    
    if mode == "reduce":
        result = integrate_reduce_mode(formatted_reviews, format_type)
    else:  # simple_merge
        result = integrate_simple_merge_mode(formatted_reviews, format_type)
    
    logger.info(f"[DONE] Integrator ({mode} mode)")
    
    return result


def integrate_reduce_mode(reviews_text: str, format_type: str) -> Dict[str, Any]:
    """
    Reduce 모드: 긴장축 추출
    
    Args:
        reviews_text: 포맷된 리뷰 텍스트
        format_type: content or service
    
    Returns:
        부분 state 업데이트
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    
    system_prompt = f"""당신은 4개 도메인(경제경영, 과학기술, 역사사회, 인문자기계발)의 리뷰를 통합하여 **긴장축(Tension Axes)**을 추출하는 전문가입니다.

목표:
1. 4개 리뷰에서 **2-3개의 핵심 긴장축**을 찾으세요
2. 긴장축: 서로 대립하거나 균형이 필요한 두 극 (예: 효율 vs 윤리, 단기 vs 장기)
3. 각 긴장축에 대해 종합/균형점을 제시하세요
4. 형식({format_type})에 맞는 분기 사유를 설명하세요
5. 최종 결론 1줄을 작성하세요

출력은 JSON 형식으로 제공하세요."""
    
    user_prompt = f"""4개 도메인 리뷰:

{reviews_text}

위 리뷰를 분석하여 긴장축을 추출하세요."""
    
    try:
        # Structured output 사용
        structured_llm = llm.with_structured_output(IntegrationResult)
        
        response = structured_llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        # State 업데이트
        tension_axes_list = [
            f"{axis.axis_name}: {axis.pole_a} ↔ {axis.pole_b} (종합: {axis.synthesis})"
            for axis in response.tension_axes
        ]
        
        integration_text = "\n".join([
            "## 긴장축",
            *[f"{i+1}. {axis}" for i, axis in enumerate(tension_axes_list)],
            "",
            f"## 형식 분기 사유",
            response.format_reasoning,
            "",
            f"## 결론",
            response.conclusion
        ])
        
        return {
            "tension_axes": tension_axes_list,
            "format_reasoning": response.format_reasoning,
            "integration_result": integration_text,
            "messages": [
                HumanMessage(
                    content=f"[Integrator-Reduce] {len(tension_axes_list)} tension axes extracted",
                    name="Integrator"
                )
            ]
        }
    
    except Exception as e:
        logger.error(f"[FAIL] Reduce mode integration error: {e}")
        return {
            "error_message": f"Integration failed: {str(e)}"
        }


def integrate_simple_merge_mode(reviews_text: str, format_type: str) -> Dict[str, Any]:
    """
    Simple Merge 모드: 4개 리뷰 병치 + 결론
    
    Args:
        reviews_text: 포맷된 리뷰 텍스트
        format_type: content or service
    
    Returns:
        부분 state 업데이트
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    system_prompt = f"""당신은 4개 도메인의 리뷰를 병치하고 간단한 결론을 작성하는 전문가입니다.

목표:
1. 4개 리뷰를 그대로 나열 (병치)
2. 형식({format_type})에 맞는 분기 사유 1줄
3. 전체를 관통하는 결론 1줄

간결하고 명확하게 작성하세요."""
    
    user_prompt = f"""4개 도메인 리뷰:

{reviews_text}

위 리뷰를 병치하고 결론을 작성하세요."""
    
    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])
        
        integration_text = f"""## 4개 도메인 리뷰 (병치)

{reviews_text}

## 형식 분기
{format_type} 형식 선택 사유: (LLM 생성 예정)

## 결론
{response.content}
"""
        
        return {
            "tension_axes": None,  # Simple merge는 긴장축 없음
            "format_reasoning": f"{format_type} 형식 선택",
            "integration_result": integration_text,
            "messages": [
                HumanMessage(
                    content=f"[Integrator-SimpleMerge] Reviews merged",
                    name="Integrator"
                )
            ]
        }
    
    except Exception as e:
        logger.error(f"[FAIL] Simple merge integration error: {e}")
        return {
            "error_message": f"Integration failed: {str(e)}"
        }

