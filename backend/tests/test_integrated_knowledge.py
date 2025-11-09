"""통합지식 파싱 테스트"""
import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.services.kb_service import kb_service


def test_integrated_knowledge_parsing():
    """통합지식 파싱 테스트"""
    print("\n[TEST] 통합지식 파싱 테스트")
    print("=" * 60)
    
    # KB 로드
    result = kb_service.load_all_domains()
    print(f"\n[OK] KB 로드 완료: {result}")
    
    # 통합지식 아이템만 필터링
    integrated_items = [item for item in kb_service.all_items if item.is_integrated_knowledge]
    
    print(f"\n[RESULT] 통합지식 아이템 수: {len(integrated_items)}")
    print(f"[RESULT] 전체 아이템 수: {len(kb_service.all_items)}")
    print(f"[RESULT] 통합지식 비율: {len(integrated_items) / len(kb_service.all_items) * 100:.1f}%")
    
    # 도메인별 통합지식 수
    print("\n[도메인별 통합지식]")
    for domain in kb_service.DOMAINS:
        domain_integrated = [
            item for item in integrated_items 
            if item.domain == domain
        ]
        print(f"  {domain}: {len(domain_integrated)}개")
        
        # 예시 출력
        if domain_integrated:
            example = domain_integrated[0]
            print(f"    예시 anchor_id: {example.anchor_id}")
            print(f"    내용 길이: {len(example.content)} chars")
            print(f"    내용 미리보기: {example.content[:100]}...")
    
    # 통합지식 anchor_id 형식 검증
    print("\n[Anchor ID 형식 검증]")
    invalid_anchors = []
    for item in integrated_items:
        if "통합지식" not in item.anchor_id:
            invalid_anchors.append(item.anchor_id)
    
    if invalid_anchors:
        print(f"  [FAIL] 잘못된 형식: {invalid_anchors}")
        return False
    else:
        print(f"  [OK] 모든 통합지식 anchor_id가 '통합지식' 포함")
    
    # 통합지식 검색 우선순위 테스트
    print("\n[검색 우선순위 테스트]")
    query = "경제 예측과 투자 전략"
    
    # 통합지식 우선 (기본)
    results_prioritized = kb_service.search(query, domain="경제경영", top_k=5)
    
    # 통합지식 우선 안함
    results_normal = kb_service.search(query, domain="경제경영", top_k=5, prioritize_integrated=False)
    
    print(f"\n  통합지식 우선 (prioritize=True):")
    for i, result in enumerate(results_prioritized[:3]):
        integrated_mark = "[통합]" if result.item.is_integrated_knowledge else ""
        print(f"    {i+1}. {integrated_mark} {result.item.anchor_id} (score: {result.similarity_score:.3f})")
    
    print(f"\n  일반 검색 (prioritize=False):")
    for i, result in enumerate(results_normal[:3]):
        integrated_mark = "[통합]" if result.item.is_integrated_knowledge else ""
        print(f"    {i+1}. {integrated_mark} {result.item.anchor_id} (score: {result.similarity_score:.3f})")
    
    # 통합지식이 상위에 있는지 확인
    top_integrated_count_prioritized = sum(
        1 for r in results_prioritized[:3] if r.item.is_integrated_knowledge
    )
    top_integrated_count_normal = sum(
        1 for r in results_normal[:3] if r.item.is_integrated_knowledge
    )
    
    print(f"\n  상위 3개 중 통합지식 수:")
    print(f"    우선순위 적용: {top_integrated_count_prioritized}개")
    print(f"    우선순위 미적용: {top_integrated_count_normal}개")
    
    if top_integrated_count_prioritized >= top_integrated_count_normal:
        print("  [OK] 통합지식 우선순위 작동")
    else:
        print("  [WARN] 통합지식 우선순위가 예상대로 작동하지 않음")
    
    # 최종 결과
    print("\n" + "=" * 60)
    if len(integrated_items) > 0:
        print("[PASS] 통합지식 파싱 테스트 성공!")
        print(f"       {len(integrated_items)}개 통합지식 아이템 파싱됨")
        return True
    else:
        print("[FAIL] 통합지식 아이템이 없습니다")
        return False


if __name__ == "__main__":
    success = test_integrated_knowledge_parsing()
    sys.exit(0 if success else 1)

