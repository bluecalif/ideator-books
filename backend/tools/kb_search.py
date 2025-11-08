"""LangChain Tool for KB search"""
from langchain.tools import Tool
from typing import Optional
from backend.services.kb_service import kb_service
import logging

logger = logging.getLogger(__name__)


def create_kb_search_tool() -> Tool:
    """
    KB 검색 LangChain Tool 생성
    
    LangGraph의 Reviewer 에이전트가 사용할 도구
    """
    
    def search_kb(query: str, domain: Optional[str] = None, top_k: int = 5) -> str:
        """
        KB 검색 실행
        
        Args:
            query: 검색 쿼리 (도서 요약 또는 개념)
            domain: 도메인 필터 (경제경영/과학기술/역사사회/인문자기계발)
            top_k: 반환할 결과 개수
        
        Returns:
            검색 결과 (포맷된 문자열)
        """
        try:
            results = kb_service.search(query, domain=domain, top_k=top_k)
            
            if not results:
                return f"No KB items found for query: '{query}'"
            
            # 결과 포맷팅
            formatted_results = []
            for i, result in enumerate(results, 1):
                item = result.item
                fusion_mark = "[FUSION]" if item.is_fusion else ""
                score = f"(score: {result.similarity_score:.3f})"
                
                formatted_results.append(
                    f"{i}. {fusion_mark} [{item.anchor_id}] {item.content}\n"
                    f"   출처: {', '.join(item.reference_books)} {score}"
                )
            
            return "\n\n".join(formatted_results)
        
        except Exception as e:
            logger.error(f"[FAIL] KB search error: {e}")
            return f"Error during KB search: {str(e)}"
    
    return Tool(
        name="kb_search",
        description=(
            "Search the expert knowledge base for relevant insights. "
            "Useful when you need to find domain-specific expert knowledge "
            "related to book summaries or concepts. "
            "Input should be a search query string. "
            "Optionally specify domain as one of: 경제경영, 과학기술, 역사사회, 인문자기계발"
        ),
        func=search_kb
    )


def search_kb_by_domain(query: str, domain: str, top_k: int = 3) -> str:
    """
    도메인별 KB 검색 (간편 함수)
    
    Args:
        query: 검색 쿼리
        domain: 도메인 (경제경영/과학기술/역사사회/인문자기계발)
        top_k: 반환할 결과 개수
    
    Returns:
        검색 결과 (포맷된 문자열)
    """
    results = kb_service.search(query, domain=domain, top_k=top_k)
    
    if not results:
        return f"No results found in domain '{domain}' for query: '{query}'"
    
    formatted_results = []
    for result in results:
        item = result.item
        fusion_mark = "[융합형]" if item.is_fusion else ""
        formatted_results.append(
            f"{fusion_mark} [{item.anchor_id}] {item.content}\n"
            f"출처: {', '.join(item.reference_books)}"
        )
    
    return "\n\n".join(formatted_results)

