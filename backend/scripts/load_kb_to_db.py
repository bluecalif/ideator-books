"""Load KB data to Supabase database"""
import logging
from pathlib import Path
from backend.services.kb_service import KBService
from backend.core.database import get_supabase_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_kb_to_database():
    """KB 파일에서 데이터를 로드하여 Supabase kb_items 테이블에 저장"""
    
    logger.info("[START] Loading KB data to database...")
    
    # KB Service 초기화 (4개 도메인 파싱)
    kb_service = KBService()
    kb_service.load_all_domains()  # 명시적으로 로드 호출
    
    # Supabase Admin 클라이언트
    supabase = get_supabase_admin()
    
    # 기존 데이터 확인
    existing_result = supabase.table("kb_items").select("count").execute()
    existing_count = len(existing_result.data) if existing_result.data else 0
    
    if existing_count > 0:
        logger.warning(f"[WARN] KB items already exist ({existing_count} items)")
        response = input("Delete and reload? (y/N): ")
        if response.lower() != 'y':
            logger.info("[SKIP] KB loading cancelled")
            return
        
        # 기존 데이터 삭제 (모든 레코드)
        # Supabase SDK는 전체 삭제를 위해 항상 참인 조건 필요
        supabase.table("kb_items").delete().gte("created_at", "1900-01-01").execute()
        logger.info("[OK] Existing KB items deleted")
    
    # KB 데이터 준비
    kb_data = []
    total_count = 0
    
    for domain, items in kb_service.kb_items.items():
        logger.info(f"[{domain}] Processing {len(items)} items...")
        
        for item in items:
            kb_data.append({
                "domain": item.domain,
                "type": item.subcategory,
                "anchor_id": item.anchor_id,
                "content": item.content,
                "is_fusion": item.is_fusion,
                "is_integrated_knowledge": item.is_integrated_knowledge,
                "reference_books": item.reference_books
            })
            total_count += 1
    
    logger.info(f"[OK] Prepared {total_count} KB items")
    
    # Bulk insert (배치 크기: 100)
    batch_size = 100
    for i in range(0, len(kb_data), batch_size):
        batch = kb_data[i:i+batch_size]
        
        result = supabase.table("kb_items").insert(batch).execute()
        
        if result.data:
            logger.info(f"[OK] Inserted batch {i//batch_size + 1} ({len(batch)} items)")
        else:
            logger.error(f"[FAIL] Failed to insert batch {i//batch_size + 1}")
            return
    
    # 검증
    final_result = supabase.table("kb_items").select("count").execute()
    final_count = len(final_result.data) if final_result.data else 0
    
    logger.info("")
    logger.info("=" * 60)
    logger.info(f"[SUCCESS] KB loading complete!")
    logger.info(f"  Total items: {final_count}")
    logger.info(f"  Fusion items: {sum(1 for item in kb_data if item['is_fusion'])}")
    logger.info(f"  Integrated knowledge: {sum(1 for item in kb_data if item['is_integrated_knowledge'])}")
    logger.info("=" * 60)


if __name__ == "__main__":
    load_kb_to_database()

