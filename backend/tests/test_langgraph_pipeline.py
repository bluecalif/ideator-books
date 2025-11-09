"""LangGraph Pipeline Test Script"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv
import time
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

# Verify OpenAI API key
if not os.getenv("OPENAI_API_KEY"):
    print("[WARN] OPENAI_API_KEY not found in environment")
    print("[INFO] Some tests requiring LLM will be skipped")

from backend.langgraph_pipeline.graph import graph
from backend.langgraph_pipeline.state import create_initial_state
from backend.services.kb_service import kb_service
from backend.services.book_service import book_service
from langchain_core.runnables import RunnableConfig


def test_graph_initialization():
    """그래프 초기화 테스트"""
    print("\n" + "=" * 60)
    print("[TEST] Graph Initialization")
    print("=" * 60)

    if graph is None:
        print("[FAIL] Graph is None")
        return False

    print("[OK] Graph initialized successfully")
    print(
        f"[OK] Graph nodes: {list(graph.nodes.keys()) if hasattr(graph, 'nodes') else 'N/A'}"
    )

    return True


def test_kb_loading():
    """KB 로딩 (파이프라인 실행 전 필수)"""
    print("\n" + "=" * 60)
    print("[TEST] KB Loading for Pipeline")
    print("=" * 60)

    result = kb_service.load_all_domains()
    total = sum(result.values())

    print(f"[OK] {total} KB items loaded")
    for domain, count in result.items():
        print(f"  - {domain}: {count} items")

    return total > 0


def test_single_node_anchor_mapper():
    """AnchorMapper 노드 단독 테스트"""
    print("\n" + "=" * 60)
    print("[TEST] AnchorMapper Node (Single)")
    print("=" * 60)

    from backend.langgraph_pipeline.nodes.anchor_mapper import anchor_mapper_node

    # 테스트 state
    test_state = create_initial_state(
        book_ids=["book_1", "book_2"], mode="reduce", format="content"
    )

    try:
        result = anchor_mapper_node(test_state)

        if "anchors" in result:
            print("[OK] Anchors mapped:")
            for domain, anchor_id in result["anchors"].items():
                print(f"  - {domain}: {anchor_id}")

            if "anchor_analysis" in result:
                print(f"\n[OK] Analysis: {result['anchor_analysis'][:150]}...")

            return True
        else:
            print("[FAIL] No anchors in result")
            return False

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_csv_loader():
    """CSV 로더 테스트"""
    print("\n" + "=" * 60)
    print("[TEST] CSV Book Loader")
    print("=" * 60)

    count = book_service.load_books()

    if count > 0:
        print(f"[OK] {count} books loaded from CSV")

        # 통계
        stats = book_service.get_stats()
        print(f"\n[STATS] Total: {stats['total_books']}")
        print(f"[STATS] Year range: {stats['year_range']}")
        print(f"\n[STATS] By domain:")
        for domain, cnt in stats["by_domain"].items():
            print(f"  - {domain}: {cnt} books")

        # 샘플 조회
        sample_book = book_service.get_book_by_id(1)
        if sample_book:
            print(f"\n[SAMPLE] Book ID 1: {sample_book['Title']}")
            print(f"  Author: {sample_book['저자']}")
            print(f"  Domain: {sample_book['구분']}")
            print(f"  Summary: {sample_book['요약'][:150]}...")

        return True
    else:
        print("[FAIL] No books loaded")
        return False


def test_pipeline_execution():
    """전체 파이프라인 실행 테스트 (실제 도서 1권)"""
    print("\n" + "=" * 60)
    print("[TEST] Full Pipeline Execution with Real Book")
    print("=" * 60)
    print("[INFO] This may take ~1 minute (LLM calls)...")

    # OpenAI API 키 확인
    if not os.getenv("OPENAI_API_KEY"):
        print("[SKIP] OpenAI API key not found")
        return None

    # 실제 도서 1권 선택
    # 1: 100년 투자 가문의 비밀 (경제/경영)
    test_book_id = 1

    books = book_service.get_books_by_ids([test_book_id])

    if not books:
        print("[FAIL] Failed to load test book")
        return False

    book = books[0]
    book_id = book["일련번호"]
    book_title = book["Title"]
    book_summary = book["요약"]

    print(f"\n[INFO] Selected book:")
    print(f"  - {book_title} ({book['구분']})")

    # 디버그: 입력 데이터 확인
    print(f"\n[DEBUG] Input data:")
    print(f"  Book ID: {book_id}")
    print(f"  Title: {book_title}")
    print(f"  Summary length: {len(book_summary)} chars")
    print(f"  Summary preview: {book_summary[:200]}...")

    # 초기 state
    initial_state = create_initial_state(
        book_ids=[book_id],
        book_summary=book_summary,
        book_title=book_title,
        book_topic=book.get("Topic", ""),
        mode="reduce",
        format="content",
        remind_enabled=False,
    )

    # 실행 config
    config = RunnableConfig(
        recursion_limit=50, configurable={"thread_id": f"test_run_book_{book_id}"}
    )

    try:
        print(f"\n[INFO] Executing pipeline...")
        start_time = time.time()

        # 노드별 시간 측정
        node_times = []
        last_node_time = start_time

        # 스트리밍 실행
        node_count = 0
        for event in graph.stream(initial_state, config):
            node_name = list(event.keys())[0]
            node_data = event[node_name]
            node_count += 1

            # 노드 실행 시간 계산
            current_time = time.time()
            node_duration = current_time - last_node_time
            node_times.append((node_name, node_duration))

            print(f"\n[{node_count}] {node_name} ({node_duration:.2f}s)")

            # 노드별 주요 결과 출력
            if node_name == "anchor_mapper":
                anchors = node_data.get("anchors", {})
                print(f"  -> Anchors: {list(anchors.values())}")
                analysis = node_data.get("anchor_analysis", "")[:100]
                print(f"  -> Analysis: {analysis}...")
            elif node_name == "review_domain":
                reviews = node_data.get("reviews", [])
                if reviews:
                    r = reviews[0]
                    print(f"  -> Domain: {r.get('domain', 'N/A')}")
                    print(f"  -> Anchor: {r.get('anchor_id', 'N/A')}")
            elif node_name == "integrator":
                axes = node_data.get("tension_axes", [])
                print(f"  -> Tension axes: {len(axes) if axes else 0}")
                if axes:
                    print(f"  -> Example: {axes[0][:80]}...")
            elif node_name == "producer":
                md_len = len(node_data.get("onepager_md", ""))
                unique = len(node_data.get("unique_sentences", []))
                print(f"  -> 1p: {md_len} chars, {unique} unique sentences")
            elif node_name == "validator":
                passed = node_data.get("validation_passed", False)
                anchored = node_data.get("anchored_by_percent", 0)
                print(
                    f"  -> Validation: {'PASS' if passed else 'FAIL'} (anchored: {anchored:.1%})"
                )

            last_node_time = current_time

        total_time = time.time() - start_time

        # 최종 state 조회
        final_state = graph.get_state(config)

        print(f"\n[OK] Pipeline executed {node_count} nodes in {total_time:.2f}s")
        print(f"[OK] Average time per node: {total_time/node_count:.2f}s")

        # 결과를 파일로 저장
        output_dir = Path("backend/tests/output")
        output_dir.mkdir(exist_ok=True)

        # 1p MD 저장
        onepager_md = final_state.values.get("onepager_md", "")
        with open(output_dir / "test_onepager.md", "w", encoding="utf-8") as f:
            f.write(onepager_md)

        # 상세 로그 저장
        with open(output_dir / "test_log.txt", "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("LangGraph Pipeline Test Results\n")
            f.write("=" * 60 + "\n\n")

            f.write(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Execution Time: {total_time:.2f}s\n")
            f.write(f"Executed Nodes: {node_count}\n")
            f.write(f"Retry Count: {final_state.values.get('retry_count', 0)}\n\n")

            # 노드별 실행 시간
            f.write("Node Execution Times:\n")
            for node_name, duration in node_times:
                f.write(f"  - {node_name}: {duration:.2f}s\n")
            f.write("\n")

            f.write("Anchors:\n")
            for domain, anchor in final_state.values.get("anchors", {}).items():
                f.write(f"  - {domain}: {anchor}\n")

            f.write(
                f"\nReviews: {len(final_state.values.get('reviews', []))} reviews\n"
            )

            f.write(f"\nValidation Results:\n")
            f.write(
                f"  - Anchored by: {final_state.values.get('anchored_by_percent', 0):.1%}\n"
            )
            f.write(
                f"  - Unique sentences: {final_state.values.get('unique_sentence_count', 0)}\n"
            )
            f.write(
                f"  - External frames: {final_state.values.get('external_frame_count', 0)}\n"
            )
            f.write(
                f"  - Validation passed: {final_state.values.get('validation_passed', False)}\n"
            )

            errors = final_state.values.get("validation_errors", [])
            if errors:
                f.write(f"\nValidation Errors:\n")
                for error in errors:
                    f.write(f"  - {error}\n")

        print(f"\n[OK] Results saved to {output_dir}/")
        print(f"  - test_onepager.md ({len(onepager_md)} chars)")
        print(f"  - test_log.txt")

        # 결과 검증
        if final_state.values.get("validation_passed"):
            print("\n[PASS] Validation passed!")
        else:
            print("\n[WARN] Validation did not pass")
            errors = final_state.values.get("validation_errors", [])
            for error in errors[:5]:  # 처음 5개만
                print(f"  - {error}")

        # 주요 결과 출력
        print(
            f"\n[RESULT] Anchors: {list(final_state.values.get('anchors', {}).keys())}"
        )
        print(f"[RESULT] Reviews: {len(final_state.values.get('reviews', []))} reviews")
        print(
            f"[RESULT] Unique sentences: {final_state.values.get('unique_sentence_count', 0)}"
        )
        print(
            f"[RESULT] Anchored by: {final_state.values.get('anchored_by_percent', 0):.1%}"
        )

        return True

    except Exception as e:
        print(f"[ERROR] Pipeline execution failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """메인 테스트 실행"""
    print("\n" + "=" * 60)
    print("LangGraph Pipeline Test Suite")
    print("=" * 60)

    tests = [
        ("Graph Initialization", test_graph_initialization),
        ("KB Loading", test_kb_loading),
        ("AnchorMapper Node", test_single_node_anchor_mapper),
        ("CSV Loader", test_csv_loader),
        ("Full Pipeline", test_pipeline_execution),  # 실제 도서 1권으로 테스트
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result if result is not None else None  # None은 SKIP
        except Exception as e:
            print(f"\n[ERROR] Test '{test_name}' failed with exception: {e}")
            import traceback

            traceback.print_exc()
            results[test_name] = False

    # 결과 요약
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    total = len(results)

    for test_name, result in results.items():
        if result is None:
            status = "[SKIP]"
        elif result:
            status = "[PASS]"
        else:
            status = "[FAIL]"
        print(f"{status} {test_name}")

    print(
        f"\n[SUMMARY] Passed: {passed}, Failed: {failed}, Skipped: {skipped} (Total: {total})"
    )

    if failed > 0:
        print("\n[FAIL] Some tests failed")
        return 1
    elif passed == (total - skipped):
        print("\n[SUCCESS] All executable tests passed!")
        return 0
    else:
        print("\n[PARTIAL] Some tests were skipped")
        return 0


if __name__ == "__main__":
    exit(main())
