"""Phase 1.5 품질 개선 통합 테스트 - 실제 데이터"""
import sys
import io
from pathlib import Path
import logging
from datetime import datetime
from dotenv import load_dotenv

# UTF-8 출력 강제 (Windows PowerShell 인코딩 문제 해결)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 프로젝트 루트를 sys.path에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# .env 파일 로드
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from backend.services.kb_service import kb_service
from backend.services.book_service import book_service
from backend.langgraph_pipeline.state import create_initial_state
from backend.langgraph_pipeline.graph import graph
from backend.core.models_config import models_config

# 모델명 가져오기 (파일명에 사용)
model_name = models_config.PRODUCER_MODEL.replace('/', '_').replace('.', '_')

# 로깅 설정
log_file = Path(__file__).parent / "output" / f"test_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
log_file.parent.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def test_phase1_5_quality():
    """Phase 1.5 품질 개선 통합 테스트"""
    
    print("\n" + "="*80)
    print(f"Phase 1.5 품질 개선 통합 테스트 - {models_config.PRODUCER_MODEL}")
    print("="*80)
    print(f"\n[MODELS]")
    print(f"   - AnchorMapper: {models_config.ANCHOR_MAPPER_MODEL}")
    print(f"   - Reviewer: {models_config.REVIEWER_MODEL}")
    print(f"   - Integrator: {models_config.INTEGRATOR_MODEL}")
    print(f"   - Producer: {models_config.PRODUCER_MODEL}")
    
    # 1. KB 로드
    print("\n[1/5] KB 로드 중...")
    kb_result = kb_service.load_all_domains()
    print(f"[OK] KB 로드 완료: {sum(kb_result.values())}개 아이템")
    
    # 통합지식 확인
    integrated_items = [item for item in kb_service.all_items if item.is_integrated_knowledge]
    print(f"   - 통합지식: {len(integrated_items)}개")
    for domain in kb_service.DOMAINS:
        domain_integrated = [i for i in integrated_items if i.domain == domain]
        print(f"     • {domain}: {len(domain_integrated)}개")
    
    # 2. CSV 로드
    print("\n[2/5] CSV 로드 중...")
    csv_path = project_root / "docs" / "100권 노션 원본_수정.csv"
    
    if not csv_path.exists():
        print(f"[FAIL] CSV 파일 없음: {csv_path}")
        return False
    
    book_service.csv_path = csv_path
    book_count = book_service.load_books()
    
    if book_count == 0:
        print(f"[FAIL] CSV 로드 실패")
        return False
    
    print(f"[OK] 도서 로드 완료: {book_count}권")
    
    # 통계 출력
    stats = book_service.get_stats()
    print(f"   - 도메인별: {stats['by_domain']}")
    
    # 테스트용 책 선택 (첫 번째 책)
    test_book_raw = book_service.books[0]
    
    # 필드 매핑 (CSV 컬럼명 → 테스트용)
    test_book = {
        'id': test_book_raw.get('일련번호', 1),
        'title': test_book_raw.get('Title', '제목 없음'),
        'author': test_book_raw.get('저자', '저자 미상'),
        'topic': test_book_raw.get('Topic', '주제 없음'),
        'summary': test_book_raw.get('요약', '요약 없음'),  # '요약' 컬럼만 사용
        'domain': test_book_raw.get('구분', '미분류')
    }
    
    print(f"\n📚 테스트 도서:")
    print(f"   - ID: {test_book['id']}")
    print(f"   - 제목: {test_book['title']}")
    print(f"   - 저자: {test_book['author']}")
    print(f"   - 도메인: {test_book['domain']}")
    print(f"   - 주제: {test_book['topic']}")
    print(f"   - 요약 길이: {len(test_book['summary'])} chars")
    
    # 3. 1p 생성 (LangGraph 실행)
    print("\n[3/5] 1p 생성 중...")
    print("   (이 과정은 약 1-2분 소요됩니다...)")
    
    # State 생성
    initial_state = create_initial_state(
        book_ids=[test_book['id']],
        mode="reduce",  # Reduce 모드 테스트
        format="content",  # 콘텐츠형
        remind_enabled=False,
        book_summary=test_book['summary'],
        book_title=test_book['title'],
        book_author=test_book['author'],
        book_topic=test_book['topic']
    )
    
    # Config
    config = {"configurable": {"thread_id": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"}}
    
    # 실행
    node_count = 0
    final_state = None
    producer_output = None  # Producer 출력 별도 저장
    validator_output = None  # Validator 출력 별도 저장
    
    try:
        for event in graph.stream(initial_state, config):
            node_name = list(event.keys())[0]
            node_count += 1
            
            print(f"   ✓ Node {node_count}: {node_name}")
            logger.info(f"Node completed: {node_name}")
            
            # 노드별 주요 정보 로깅
            node_data = event[node_name]
            
            # Producer와 Validator 출력 저장
            if node_name == "producer":
                producer_output = node_data
            elif node_name == "validator":
                validator_output = node_data
            
            if node_name == "anchor_mapper":
                anchors = node_data.get("anchors", {})
                available_count = len(node_data.get("available_anchors", []))
                logger.info(f"  Anchors: {anchors}")
                logger.info(f"  Available anchors: {available_count}개")
                print(f"      - 앵커 매핑 완료: {len(anchors)}개 도메인")
                print(f"      - 사용 가능 앵커: {available_count}개")
            
            elif "reviewer" in node_name.lower():
                reviews = node_data.get("reviews", [])
                if reviews:
                    review = reviews[-1]  # 마지막 추가된 리뷰
                    logger.info(f"  Review ({review['domain']}): {len(review.get('raw_content', ''))} chars")
                    print(f"      - {review['domain']} 리뷰 완료")
            
            elif node_name == "integrator":
                tension_axes = node_data.get("tension_axes", [])
                logger.info(f"  Tension axes: {len(tension_axes)}개")
                for i, axis in enumerate(tension_axes, 1):
                    logger.info(f"    {i}. {axis}")
                print(f"      - 긴장축: {len(tension_axes)}개 추출")
            
            elif node_name == "producer":
                onepager_length = len(node_data.get("onepager_md", ""))
                unique_count = len(node_data.get("unique_sentences", []))
                logger.info(f"  1p length: {onepager_length} chars")
                logger.info(f"  Unique sentences: {unique_count}개")
                print(f"      - 1p 생성 완료: {onepager_length} chars")
                print(f"      - 고유문장: {unique_count}개")
            
            elif node_name == "validator":
                anchored = node_data.get("anchored_by_percent", 0)
                unique = node_data.get("unique_sentence_count", 0)
                external = node_data.get("external_frame_count", 0)
                fake = node_data.get("fake_anchor_count", 0) if "fake_anchor_count" in str(node_data) else "N/A"
                passed = node_data.get("validation_passed", False)
                
                logger.info(f"  Validation: anchored={anchored:.1%}, unique={unique}, external={external}, fake={fake}")
                print(f"      - anchored_by: {anchored:.1%}")
                print(f"      - 고유문장: {unique}개")
                print(f"      - 외부프레임: {external}개")
                print(f"      - 가짜앵커: {fake}개" if fake != "N/A" else "")
                print(f"      - 검증: {'✅ PASS' if passed else '❌ FAIL'}")
            
            # 최종 state 저장
            final_state = node_data
        
        print(f"\n✅ 파이프라인 실행 완료: {node_count}개 노드")
        
    except Exception as e:
        print(f"\n❌ 파이프라인 실행 중 오류: {e}")
        logger.error(f"Pipeline error: {e}", exc_info=True)
        return False
    
    # 4. 결과 저장
    print("\n[4/5] 결과 저장 중...")
    
    if not producer_output or "onepager_md" not in producer_output:
        print("❌ Producer 출력이 없습니다")
        return False
    
    onepager_md = producer_output["onepager_md"]
    
    if not onepager_md:
        print("❌ 1p가 비어 있습니다")
        return False
    output_file = Path(__file__).parent / "output" / f"1p_{model_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"# 품질 개선 테스트 결과\n\n")
        f.write(f"**테스트 시각**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**사용 모델**: {models_config.PRODUCER_MODEL}\n\n")
        f.write(f"**테스트 도서**: {test_book['title']} ({test_book['author']})\n\n")
        f.write(f"---\n\n")
        f.write(onepager_md)
    
    print(f"✅ 1p 저장 완료: {output_file}")
    print(f"   크기: {len(onepager_md)} chars")
    
    # 5. 품질 점검 리포트
    print("\n[5/5] 품질 점검 리포트")
    print("="*80)
    
    # 5.1 통합지식 사용 여부
    integrated_anchor_count = onepager_md.count("통합지식")
    print(f"\n✓ 통합지식 앵커 사용: {integrated_anchor_count}회")
    
    # 5.2 1p 제안서 구조 확인
    required_sections = [
        "# 형식 분기",
        "# 도메인 리뷰 카드",
        "# 통합 기록",
        "# 최종 1p 제안서",
        "## 제목",
        "## 로그라인",
        "## 대상",
        "## 핵심 약속",
        "## 포맷",
        "## 구성",
        "## 고유 문장",
        "## CTA"
    ]
    
    print(f"\n✓ 1p 제안서 구조 확인:")
    missing_sections = []
    for section in required_sections:
        if section in onepager_md:
            print(f"   ✅ {section}")
        else:
            print(f"   ❌ {section} (누락)")
            missing_sections.append(section)
    
    # 5.3 앵커 사용 통계
    import re
    anchors_used = re.findall(r'\[([^\]]+)\]', onepager_md)
    unique_anchors = set(anchors_used)
    
    print(f"\n✓ 앵커 사용 통계:")
    print(f"   - 총 사용: {len(anchors_used)}회")
    print(f"   - 고유 앵커: {len(unique_anchors)}개")
    
    # 5.4 검증 결과
    print(f"\n✓ 검증 결과:")
    validation_passed = validator_output.get("validation_passed") if validator_output else False
    validation_errors = validator_output.get("validation_errors", []) if validator_output else []
    
    if validation_passed:
        print("   ✅ 모든 검증 통과!")
    else:
        print("   ❌ 검증 실패:")
        for error in validation_errors:
            print(f"      - {error}")
    
    # 최종 결과
    print("\n" + "="*80)
    print("📊 최종 평가")
    print("="*80)
    
    # Validator 출력에서 검증 데이터 가져오기
    anchored_by_percent = validator_output.get("anchored_by_percent", 0) if validator_output else 0
    unique_sentence_count = validator_output.get("unique_sentence_count", 0) if validator_output else 0
    external_frame_count = validator_output.get("external_frame_count", 0) if validator_output else 0
    
    success_criteria = [
        (integrated_anchor_count > 0, "통합지식 앵커 사용"),
        (len(missing_sections) == 0, "1p 제안서 구조 완성"),
        (anchored_by_percent >= 0.9, "앵커 커버리지 90% 이상"),
        (unique_sentence_count >= 3, "고유문장 3개 이상"),
        (external_frame_count == 0, "외부 프레임워크 0개"),
        (validation_passed, "최종 검증 통과")
    ]
    
    passed_count = sum(1 for passed, _ in success_criteria if passed)
    total_count = len(success_criteria)
    
    for passed, criterion in success_criteria:
        status = "✅" if passed else "❌"
        print(f"{status} {criterion}")
    
    print(f"\n🎯 달성률: {passed_count}/{total_count} ({passed_count/total_count*100:.0f}%)")
    
    print(f"\n📁 출력 파일:")
    print(f"   - 1p: {output_file}")
    print(f"   - 로그: {log_file}")
    
    print("\n" + "="*80)
    
    if passed_count == total_count:
        print("✅ 모든 품질 기준을 충족했습니다!")
        return True
    else:
        print(f"⚠️  {total_count - passed_count}개 기준 미달성")
        return False


if __name__ == "__main__":
    print("\n[START] Phase 1.5 Quality Test\n")
    
    success = test_phase1_5_quality()
    
    if success:
        print("\n[SUCCESS] All quality criteria met!")
        print("\nNext steps:")
        print("1. Check .md file in output directory for 1p content")
        print("2. Check .log file for node details")
        print("3. Reply 'OK' if satisfied")
        print("4. Request improvements if needed")
    else:
        print("\n[WARN] Some quality criteria not met")
        print("Improvements needed.")
    
    sys.exit(0 if success else 1)

