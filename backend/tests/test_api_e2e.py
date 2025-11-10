"""End-to-End API Test"""
import httpx
import time
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"


def test_health_check():
    """서버 헬스 체크"""
    logger.info("[TEST] Health check...")
    
    response = httpx.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    
    logger.info("[PASS] Health check successful")


def test_upload_csv():
    """CSV 업로드 테스트"""
    logger.info("[TEST] Uploading CSV...")
    
    # 테스트 CSV 파일 경로
    csv_path = Path("docs/100권 노션 원본_수정.csv")
    
    if not csv_path.exists():
        logger.warning(f"[SKIP] CSV file not found: {csv_path}")
        return None
    
    # Unique filename (timestamp)
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"test_books_{timestamp}.csv"
    
    with open(csv_path, 'rb') as f:
        files = {"file": (filename, f, "text/csv")}
        response = httpx.post(f"{BASE_URL}/api/upload", files=files, timeout=30.0)
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    
    library_id = data["id"]
    logger.info(f"[PASS] Library created: {library_id}")
    
    return library_id


def test_get_books(library_id: str = None):
    """도서 조회 테스트"""
    logger.info("[TEST] Getting books...")
    
    params = {"limit": 10}
    if library_id:
        params["library_id"] = library_id
    
    response = httpx.get(f"{BASE_URL}/api/books", params=params, timeout=10.0)
    assert response.status_code == 200
    books = response.json()
    
    logger.info(f"[PASS] Retrieved {len(books)} books")
    
    if books:
        sample_book = books[0]
        logger.info(f"  Sample: {sample_book['meta_json']['title']} by {sample_book['meta_json']['author']}")
        return books
    
    return []


def test_fusion_preview(book_ids: list):
    """Fusion preview 테스트"""
    logger.info(f"[TEST] Fusion preview with {len(book_ids)} books...")
    
    response = httpx.post(
        f"{BASE_URL}/api/fusion/preview",
        json={"book_ids": book_ids},
        timeout=10.0
    )
    
    assert response.status_code == 200
    data = response.json()
    
    logger.info(f"[PASS] Recommended: {data['recommended_mode']['mode']}")
    logger.info(f"  Alternative: {data['alternative_mode']['mode']}")
    
    return data


def test_create_run(book_ids: list, mode: str = "synthesis"):
    """Run 생성 테스트"""
    logger.info(f"[TEST] Creating run with {len(book_ids)} books (mode={mode})...")
    
    response = httpx.post(
        f"{BASE_URL}/api/runs",
        json={
            "book_ids": book_ids,
            "mode": mode,
            "format": "content",
            "remind_enabled": False
        },
        timeout=10.0
    )
    
    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.text}"
    data = response.json()
    
    run_id = data["id"]
    logger.info(f"[PASS] Run created: {run_id} (status={data['status']})")
    
    return run_id


def test_poll_run_status(run_id: str, max_wait: int = 120):
    """Run 상태 폴링 (completed 또는 failed까지)"""
    logger.info(f"[TEST] Polling run {run_id}...")
    
    start_time = time.time()
    
    while True:
        response = httpx.get(f"{BASE_URL}/api/runs/{run_id}", timeout=10.0)
        assert response.status_code == 200
        data = response.json()
        
        status_value = data["status"]
        progress = data["progress_json"]
        current_node = progress.get("current_node", "unknown")
        percent = progress.get("percent", 0.0)
        
        elapsed = time.time() - start_time
        logger.info(f"  [{elapsed:.1f}s] Status: {status_value}, Node: {current_node}, Progress: {percent:.1f}%")
        
        if status_value == "completed":
            logger.info(f"[PASS] Run completed in {elapsed:.1f}s")
            return True
        
        elif status_value == "failed":
            error_msg = data.get("error_message", "Unknown error")
            logger.error(f"[FAIL] Run failed: {error_msg}")
            return False
        
        elif elapsed > max_wait:
            logger.error(f"[FAIL] Timeout after {max_wait}s")
            return False
        
        # 2초 대기 후 재시도
        time.sleep(2)


def test_get_history():
    """히스토리 조회 테스트"""
    logger.info("[TEST] Getting history...")
    
    response = httpx.get(f"{BASE_URL}/api/history?limit=5", timeout=10.0)
    assert response.status_code == 200
    history = response.json()
    
    logger.info(f"[PASS] Retrieved {len(history)} history items")
    
    for item in history:
        logger.info(f"  - Run {item['run_id']}: {item['status']}, {len(item['artifacts'])} artifacts")
    
    return history


def run_e2e_test():
    """전체 E2E 테스트"""
    logger.info("=" * 80)
    logger.info("Starting End-to-End API Test")
    logger.info("=" * 80)
    logger.info("")
    
    try:
        # 1. Health check
        test_health_check()
        logger.info("")
        
        # 2. CSV 업로드
        library_id = test_upload_csv()
        logger.info("")
        
        # 3. Books 조회
        books = test_get_books(library_id)
        logger.info("")
        
        if not books:
            logger.warning("[SKIP] No books found, skipping run creation")
            return
        
        # 4. Fusion preview
        book_ids = [books[0]["id"]]  # 1권만 테스트
        test_fusion_preview(book_ids)
        logger.info("")
        
        # 5. Run 생성
        run_id = test_create_run(book_ids, mode="synthesis")
        logger.info("")
        
        # 6. Run 상태 폴링
        success = test_poll_run_status(run_id, max_wait=120)
        logger.info("")
        
        if not success:
            logger.error("[FAIL] Run did not complete successfully")
            return
        
        # 7. History 조회
        test_get_history()
        logger.info("")
        
        logger.info("=" * 80)
        logger.info("[SUCCESS] End-to-End API Test Complete!")
        logger.info("=" * 80)
        
    except AssertionError as e:
        logger.error(f"[FAIL] Assertion error: {e}")
        raise
    except Exception as e:
        logger.error(f"[ERROR] Test failed: {e}")
        raise


if __name__ == "__main__":
    run_e2e_test()

