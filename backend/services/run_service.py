"""Run Service - 백그라운드 1p 생성 작업 관리"""
import logging
from typing import List, Dict, Any
from datetime import datetime
from backend.core.database import get_supabase_admin
from backend.langgraph_pipeline.graph import graph  # 이미 컴파일된 graph 사용
from supabase import Client

logger = logging.getLogger(__name__)


def update_run_status(
    run_id: str,
    status: str,
    error_message: str = None,
    completed_at: datetime = None
):
    """Run 상태 업데이트"""
    try:
        supabase = get_supabase_admin()
        
        update_data = {
            "status": status
        }
        
        if error_message:
            update_data["error_message"] = error_message
        
        if completed_at:
            update_data["completed_at"] = completed_at.isoformat()
        
        result = supabase.table("runs") \
            .update(update_data) \
            .eq("id", run_id) \
            .execute()
        
        if result.data:
            logger.info(f"[RUN {run_id}] Status updated to '{status}'")
        else:
            logger.error(f"[RUN {run_id}] Failed to update status")
            
    except Exception as e:
        logger.error(f"[RUN {run_id}] Error updating status: {e}")


def update_run_progress(
    run_id: str,
    current_node: str,
    percent: float
):
    """Run 진행률 업데이트"""
    try:
        supabase = get_supabase_admin()
        
        progress_json = {
            "current_node": current_node,
            "percent": percent,
            "timestamp": datetime.now().isoformat()
        }
        
        result = supabase.table("runs") \
            .update({"progress_json": progress_json}) \
            .eq("id", run_id) \
            .execute()
        
        if result.data:
            logger.info(f"[RUN {run_id}] Progress: {current_node} ({percent:.1f}%)")
        else:
            logger.error(f"[RUN {run_id}] Failed to update progress")
            
    except Exception as e:
        logger.error(f"[RUN {run_id}] Error updating progress: {e}")


def save_artifact_to_storage(
    run_id: str,
    content: str,
    format: str = "md"
) -> str:
    """
    Artifact를 Supabase Storage에 저장
    
    Returns:
        str: 저장된 파일의 URL
    """
    try:
        supabase = get_supabase_admin()
        
        # 파일명 생성
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"onepager_{run_id}_{timestamp}.{format}"
        
        # TODO: Supabase Storage 업로드 구현
        # 현재는 임시로 로컬 저장 또는 직접 URL 반환
        logger.warning(f"[RUN {run_id}] Supabase Storage upload not implemented yet")
        
        # 임시: content를 직접 저장하지 않고 placeholder URL 반환
        placeholder_url = f"https://storage.example.com/{filename}"
        
        # Artifact 레코드 생성
        artifact_result = supabase.table("artifacts").insert({
            "run_id": run_id,
            "kind": "onepager",
            "format": format,
            "url": placeholder_url,
            "metadata_json": {
                "filename": filename,
                "content_length": len(content),
                "created_at": datetime.now().isoformat()
            }
        }).execute()
        
        if artifact_result.data:
            artifact_id = artifact_result.data[0]["id"]
            logger.info(f"[RUN {run_id}] Artifact created: {artifact_id}")
            return placeholder_url
        else:
            logger.error(f"[RUN {run_id}] Failed to create artifact")
            return ""
            
    except Exception as e:
        logger.error(f"[RUN {run_id}] Error saving artifact: {e}")
        return ""


def execute_pipeline(
    run_id: str,
    book_ids: List[str],
    mode: str,
    format: str
):
    """
    LangGraph 파이프라인 실행 (백그라운드 작업)
    
    Args:
        run_id: Run ID
        book_ids: 도서 ID 리스트 (1개만 지원 - 1권당 1p)
        mode: synthesis 또는 simple_merge
        format: content 또는 service
    """
    try:
        logger.info(f"[RUN {run_id}] Starting pipeline with {len(book_ids)} books (mode={mode})")
        
        # Run 상태를 running으로 변경
        update_run_status(run_id, "running")
        
        # 도서 정보 조회
        supabase = get_supabase_admin()
        books_result = supabase.table("books") \
            .select("*") \
            .in_("id", book_ids) \
            .execute()
        
        if not books_result.data:
            raise Exception("Books not found")
        
        books = books_result.data
        
        # 1권당 1p 처리 (첫 번째 도서만)
        book = books[0]
        book_meta = book["meta_json"]
        
        logger.info(f"[RUN {run_id}] Processing book: {book_meta['title']}")
        
        # LangGraph 워크플로우는 이미 컴파일되어 있음 (graph.py의 전역 변수)
        
        # 입력 데이터 준비
        inputs = {
            "book_id": book["id"],
            "book_summary": book_meta.get("summary", ""),
            "book_title": book_meta.get("title", ""),
            "book_author": book_meta.get("author", ""),
            "book_topic": book_meta.get("topic", ""),
            "mode": mode,
            "format": format
        }
        
        # Config 설정 (thread_id로 상태 추적)
        config = {
            "configurable": {"thread_id": run_id},
            "recursion_limit": 50
        }
        
        # 노드별 진행률 매핑 (9개 노드)
        node_progress = {
            "anchor_mapper": 11.1,
            "review_domain": 33.3,  # 4개 병렬
            "integrator": 55.6,
            "producer": 77.8,
            "validator": 88.9,
            "assemble": 100.0
        }
        
        # 그래프 실행 (스트리밍)
        logger.info(f"[RUN {run_id}] Executing LangGraph pipeline...")
        
        for event in graph.stream(inputs, config):
            node_name = list(event.keys())[0]
            
            # 진행률 업데이트
            percent = node_progress.get(node_name, 0.0)
            update_run_progress(run_id, node_name, percent)
            
            logger.info(f"[RUN {run_id}] Node completed: {node_name}")
        
        # 최종 state는 checkpointer에서 가져오기
        final_state = graph.get_state(config)
        
        # 최종 결과물 추출
        if final_state and "onepager_md" in final_state.values:
            onepager_content = final_state.values["onepager_md"]
            
            # Artifact 저장
            artifact_url = save_artifact_to_storage(run_id, onepager_content, format="md")
            
            if not artifact_url:
                raise Exception("Failed to save artifact")
            
            # Run 상태를 completed로 변경
            update_run_status(run_id, "completed", completed_at=datetime.now())
            
            logger.info(f"[RUN {run_id}] Pipeline completed successfully")
            
        else:
            raise Exception("No onepager_md in final state")
        
    except Exception as e:
        logger.error(f"[RUN {run_id}] Pipeline failed: {e}")
        
        # Run 상태를 failed로 변경
        update_run_status(
            run_id,
            "failed",
            error_message=str(e),
            completed_at=datetime.now()
        )


def execute_pipeline_async(
    run_id: str,
    book_ids: List[str],
    mode: str,
    format: str
):
    """
    비동기 파이프라인 실행 래퍼
    
    FastAPI BackgroundTasks에서 호출
    """
    try:
        execute_pipeline(run_id, book_ids, mode, format)
    except Exception as e:
        logger.error(f"[RUN {run_id}] Async execution error: {e}")

