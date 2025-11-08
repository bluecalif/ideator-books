"""KB Parser Test Script"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.kb_service import kb_service
from backend.tools.kb_search import search_kb_by_domain


def test_kb_loading():
    """KB 파일 로딩 테스트"""
    print("\n" + "=" * 60)
    print("[TEST] KB File Loading")
    print("=" * 60)

    result = kb_service.load_all_domains()

    print("\n[RESULT] Loaded items by domain:")
    for domain, count in result.items():
        print(f"  - {domain}: {count} items")

    return sum(result.values()) > 0


def test_kb_stats():
    """KB 통계 테스트"""
    print("\n" + "=" * 60)
    print("[TEST] KB Statistics")
    print("=" * 60)

    stats = kb_service.get_stats()

    print(f"\n[RESULT] Total items: {stats.total_items}")
    print(
        f"[RESULT] Fusion items: {stats.fusion_items} ({stats.fusion_items/stats.total_items*100:.1f}%)"
    )

    print("\n[RESULT] Items by domain:")
    for domain, count in stats.items_by_domain.items():
        print(f"  - {domain}: {count} items")

    print("\n[RESULT] Items by subcategory (top 10):")
    sorted_subcats = sorted(
        stats.items_by_subcategory.items(), key=lambda x: x[1], reverse=True
    )[:10]
    for subcat, count in sorted_subcats:
        print(f"  - {subcat}: {count} items")

    return stats.total_items > 0


def test_kb_uniqueness():
    """KB 고유성 검증 테스트"""
    print("\n" + "=" * 60)
    print("[TEST] KB Uniqueness Validation")
    print("=" * 60)

    validation = kb_service.validate_uniqueness()

    print(f"\n[RESULT] Unique anchor IDs: {validation['unique_anchors']}")
    print(f"[RESULT] Unique KB IDs: {validation['unique_kb_ids']}")
    print(f"[RESULT] Total items: {validation['total_items']}")

    if validation["duplicate_anchors"]:
        print(f"\n[WARN] Duplicate anchor IDs found:")
        for dup in validation["duplicate_anchors"]:
            print(f"  - {dup}")
    else:
        print("\n[OK] No duplicate anchor IDs")

    if validation["duplicate_kb_ids"]:
        print(f"\n[WARN] Duplicate KB IDs found:")
        for dup in validation["duplicate_kb_ids"]:
            print(f"  - {dup}")
    else:
        print("\n[OK] No duplicate KB IDs")

    return validation["unique_anchors"] and validation["unique_kb_ids"]


def test_kb_search():
    """KB 검색 테스트"""
    print("\n" + "=" * 60)
    print("[TEST] KB Search")
    print("=" * 60)

    # 테스트 쿼리
    queries = [
        ("부동산 투자", "경제경영"),
        ("인공지능", "과학기술"),
        ("역사적 교훈", "역사사회"),
        ("자기계발", "인문자기계발"),
    ]

    all_passed = True
    for query, domain in queries:
        print(f"\n[TEST] Query: '{query}' in domain '{domain}'")
        result = search_kb_by_domain(query, domain, top_k=3)

        if result and "No results" not in result:
            print(f"[OK] Found results")
            print("\n" + result[:300] + "..." if len(result) > 300 else result)
        else:
            print(f"[FAIL] No results found")
            all_passed = False

    return all_passed


def test_fusion_items():
    """융합형 인사이트 테스트"""
    print("\n" + "=" * 60)
    print("[TEST] Fusion Insights")
    print("=" * 60)

    fusion_items = [item for item in kb_service.all_items if item.is_fusion]

    print(f"\n[RESULT] Total fusion items: {len(fusion_items)}")
    print(f"\n[SAMPLE] First 5 fusion items:")

    for i, item in enumerate(fusion_items[:5], 1):
        print(f"\n{i}. [{item.anchor_id}]")
        print(f"   Domain: {item.domain} / {item.subcategory}")
        print(f"   Content: {item.content[:150]}...")
        print(f"   Books: {', '.join(item.reference_books)}")

    return len(fusion_items) > 0


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 60)
    print("KB Parser Test Suite")
    print("=" * 60)

    tests = [
        ("KB Loading", test_kb_loading),
        ("KB Statistics", test_kb_stats),
        ("KB Uniqueness", test_kb_uniqueness),
        ("Fusion Insights", test_fusion_items),
        ("KB Search", test_kb_search),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n[ERROR] Test '{test_name}' failed with exception: {e}")
            results[test_name] = False

    # 결과 요약
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r)
    total = len(results)

    for test_name, result in results.items():
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")

    print(f"\n[SUMMARY] {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[FAIL] Some tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
