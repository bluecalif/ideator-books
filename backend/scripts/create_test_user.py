"""Create test user for development"""
import logging
from backend.core.database import get_supabase_admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_test_user():
    """테스트용 임시 사용자 생성"""
    
    supabase = get_supabase_admin()
    
    # 고정된 임시 UUID (API에서 사용)
    test_user_id = "00000000-0000-0000-0000-000000000001"
    test_email = "test@ideator-books.dev"
    
    logger.info(f"[START] Creating test user...")
    
    # 기존 사용자 확인
    existing = supabase.table("users").select("*").eq("id", test_user_id).execute()
    
    if existing.data:
        logger.info(f"[OK] Test user already exists: {test_email}")
        return test_user_id
    
    # 새 사용자 생성
    try:
        # Note: users 테이블은 auth.users FK 제약이 있음
        # Supabase Auth에 먼저 사용자 생성 필요 또는 제약 제거
        
        # 임시 해결: SQL로 직접 INSERT (RLS 우회)
        logger.warning("[WARN] Cannot insert user due to auth.users FK constraint")
        logger.info("[INFO] Solution: Use Supabase Dashboard to create user manually")
        logger.info(f"      OR modify schema to remove FK constraint temporarily")
        
        return None
        
    except Exception as e:
        logger.error(f"[ERROR] Failed to create test user: {e}")
        return None


if __name__ == "__main__":
    create_test_user()



