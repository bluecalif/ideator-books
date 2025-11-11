# ideator-books MVP 개발 계획 및 진행 상황

## 프로젝트 개요
- **목표**: 전문가 KB 기반 1p 생성 서비스 MVP 구축
- **기술 스택**: Next.js + FastAPI + PostgreSQL(Supabase) + LangGraph
- **개발 순서**: 백엔드 → API → UI

---

## Phase 0: 환경 설정 및 사전 준비

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 0.0 | Git 초기화 및 원격 저장소 연결 | ✅ DONE | https://github.com/bluecalif/ideator-books.git |
| 0.1 | 필수 패키지 추가 설치 | ✅ DONE | fastapi, uvicorn, supabase, reportlab, httpx |
| 0.2 | Supabase 프로젝트 생성 및 연결 | ✅ DONE | URL: xsrbxmhrnamsyhldjuju.supabase.co |
| 0.3 | OpenAI API 키 설정 | ✅ DONE | OPENAI_API_KEY 보유 |
| 0.4 | .env 및 .env.example 파일 생성 | ✅ DONE | 환경 변수 설정 |
| 0.5 | 프로젝트 디렉토리 구조 생성 | ✅ DONE | backend/ 완료, frontend/ 대기 |
| 0.6 | KB 파일 분석 | ✅ DONE | 4개 도메인 MD (경제경영/과학기술/역사사회/인문자기계발) |
| 0.7 | 🔄 Git Commit: "Phase 0 완료" | ✅ DONE | commit f86876c, pushed to origin/master |

---

## Phase 1: 백엔드 핵심 로직 (LangGraph 파이프라인)

### 1.1 프로젝트 구조 및 기본 설정

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 1.1.1 | FastAPI 초기화 (backend/main.py) | ✅ DONE | Health check 엔드포인트 테스트 성공 |
| 1.1.2 | 디렉토리 구조 생성 | ✅ DONE | core/, langgraph_pipeline/, services/, models/, api/ |
| 1.1.3 | 환경 설정 (backend/core/config.py) | ✅ DONE | Pydantic Settings 적용 |
| 1.1.4 | Supabase 연결 (backend/core/database.py) | ✅ DONE | get_supabase() dependency 구현 |

### 1.2 KB 처리 시스템

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 1.2.1 | KB 파서 구현 (backend/services/kb_service.py) | ✅ DONE | MD → 구조화 데이터, TF-IDF 검색 |
| 1.2.2 | KB 데이터 모델 (backend/models/schemas.py) | ✅ DONE | KBItem, KBSearchResult, KBStats |
| 1.2.3 | 4개 도메인 KB 파싱 및 검증 | ✅ DONE | 128개 인사이트 (융합형 48개, 37.5%) |
| 1.2.4 | KB 검색 도구 (backend/tools/kb_search.py) | ✅ DONE | LangChain Tool 래퍼, 도메인별 검색 |
| 1.2.5 | ✅ 테스트: KB 파싱 실제 데이터 검증 | ✅ DONE | 5/5 테스트 통과 (로딩/통계/고유성/융합형/검색) |
| 1.2.6 | 🔄 Git Commit: "KB 처리 시스템 완료" | ✅ DONE | 파서 + 검색 + 테스트 |

### 1.3 LangGraph State 및 그래프 정의

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 1.3.1 | OnePagerState 정의 (state.py) | ✅ DONE | TypedDict, Annotated, operator.add, 20+ 필드 |
| 1.3.2 | LangGraph 구조 정의 (graph.py) | ✅ DONE | StateGraph 골격, Send() API 준비 |
| 1.3.3 | 체크포인트 저장 (MemorySaver) | ✅ DONE | compile_graph with checkpointer |
| 1.3.4 | 노드 유틸리티 함수 (utils.py) | ✅ DONE | agent_node, 검증, 로깅 헬퍼 |
| 1.3.5 | ✅ (테스트 생략) Phase 1.4에서 통합 테스트 | N/A | 노드 미구현으로 단독 실행 불가 |
| 1.3.6 | 🔄 Git Commit: "LangGraph State 정의" | ✅ DONE | State + 그래프 골격 + 유틸리티 |

### 1.4 LangGraph 노드 구현

| ID | 작업 내용 | Status | 구현 패턴 | 비고 |
|----|----------|--------|----------|------|
| 1.4.1 | AnchorMapper | ✅ DONE | LLM + KB 검색 | 도서→4도메인 앵커 매핑, 분석 |
| 1.4.2 | Reviewer_경제경영 | ✅ DONE | create_react_agent | functools.partial |
| 1.4.3 | Reviewer_과학기술 | ✅ DONE | create_react_agent | functools.partial |
| 1.4.4 | Reviewer_역사사회 | ✅ DONE | create_react_agent | functools.partial |
| 1.4.5 | Reviewer_인문자기계발 | ✅ DONE | create_react_agent | functools.partial |
| 1.4.6 | Integrator (Reduce) | ✅ DONE | LLM structured output | TensionAxis Pydantic 모델 |
| 1.4.7 | Integrator (단순병합) | ✅ DONE | 병치 로직 | 4도메인 병치 + 결론 |
| 1.4.8 | Producer (MD) | ✅ DONE | LLM + 템플릿 | 동적 레이아웃, 고유문장 추출 |
| 1.4.9 | Producer (PDF) | 🔄 REVIEW | reportlab | Placeholder (Phase 2에서 완성) |
| 1.4.10 | Validator | ✅ DONE | 규칙 기반 | anchored_by/고유문장/외부프레임 검증 |
| 1.4.11 | ✅ 테스트: 단일 노드 테스트 (AnchorMapper) | ✅ DONE | 4개 도메인 앵커 매핑 성공 + AI 분석 |
| 1.4.12 | CSV 로더 작성 (book_service.py) | ✅ DONE | 87권 로드, 도메인별 통계 |
| 1.4.13 | 1권당 1p 생성 구조로 변경 (핵심!) | ✅ DONE | 3권 → 3개 1p (각 50초, 총 150초) |
| 1.4.14 | 재시도 로직 제거 | ✅ DONE | Validator 실패해도 1회만 실행 |
| 1.4.15 | 모든 LLM gpt-4o-mini로 통일 | ✅ DONE | 비용 절감 (15배) |
| 1.4.16 | 노드별 시간 측정 및 중간 결과 출력 | ✅ DONE | 각 노드 시간/결과 출력, 파일 저장 |
| 1.4.17 | ✅ 테스트: 1권당 1p 생성 (1권) | ✅ DONE | 54초, 8개 노드, 1,708자 |
| 1.4.18 | book_summary State 전달 개선 | ✅ DONE | book_summaries → book_summary/title/topic |
| 1.4.19 | 디버그 로그 추가 | ✅ DONE | AnchorMapper, Reviewer 입력 확인 |
| 1.4.20 | 🔄 Git Commit: "LangGraph 노드 구현 완료" | ✅ DONE | 5개 노드 + 1권당 1p + 테스트 (커밋 5e4806d) |

**구현 핵심:**
- Reviewers: functools.partial + Send() API로 병렬 실행
- Integrator: Pydantic 모델로 structured output (synthesis 모드)
- Producer: 조립(템플릿) + 창작(LLM)으로 분리
- Validator: 정규식 + 카운팅, 실패 시 에러 메시지

### 1.5 1p 품질 개선 (모범 사례 대비)

**초기 문제점:**
- ❌ 형식 분기 사유가 일반적
- ❌ 도메인 리뷰가 피상적 (책 내용과 연결 약함)
- ❌ 개별 인사이트 앵커만 사용 (통합지식 없음)
- ❌ 긴장축이 일반적
- ❌ 1p 제안서 없음 (제목, 로그라인, 대상, 포맷, 구성, CTA)
- ❌ 고유문장이 약함
- ❌ 가짜 앵커 생성 (예: `투자전략_최적화_001`)

**모범 사례 (docs/1p사례.md) 핵심 요소:**
- 구체적 형식 분기 (도구형/이야기형/분석형)
- 도메인별 **통합지식 앵커** 활용
- 명확한 긴장축 (의미vs성과, 개인vs사회)
- 완성된 1p 제안서 (7요소: 제목/로그라인/대상/약속/포맷/구성/CTA)
- 강력한 고유문장 3개
- 100% 실제 KB 앵커

| ID | 작업 내용 | Status | 구현 대상 | 비고 |
|----|----------|--------|----------|------|
| 1.5.1 | 모범 사례 분석 및 품질 기준 정의 | ✅ DONE | - | docs/1p사례.md 기준 확립, .cursor/rules 생성 |
| 1.5.2 | KB 통합지식 파싱 및 활용 | ✅ DONE | kb_service.py, schemas.py | "통합지식" 섹션 파싱, is_integrated_knowledge 필드, 가중치 0.05 |
| 1.5.3 | State에 available_anchors, book_author 추가 | ✅ DONE | state.py | 가짜 앵커 방지, 저자 정보 전달 |
| 1.5.4 | AnchorMapper 앵커 리스트 전달 | ✅ DONE | anchor_mapper.py | 144개 KB 앵커 State에 저장, 모델 설정 분리 |
| 1.5.5 | Reviewer → Structured Output 변경 | ✅ DONE | reviewers.py | Agent 제거, DomainReview Pydantic, 책 내용 중심 프롬프트 강화 |
| 1.5.6 | Integrator 긴장축 개선 | ✅ DONE | integrator.py | 명확한 대립/상충/경계, 모범 예시, 모델 설정 |
| 1.5.7 | Producer "출발 지식" + 섹션 명시 | ✅ DONE | producer.py | 출발지식 섹션, 도메인 리뷰 카드, 통합 기록 명시, 모델 설정 |
| 1.5.8 | Validator 가짜 앵커 검증 추가 | ✅ DONE | validator.py | validate_fake_anchors() 로직 |
| 1.5.9 | LLM 모델 설정 분리 | ✅ DONE | models_config.py | 노드별 모델/Temperature 관리 |
| 1.5.10 | CSV "요약" 컬럼 사용 | ✅ DONE | test_phase1_5_quality.py | 100권 노션 원본_수정.csv |
| 1.5.11 | 상세 로깅 추가 | ✅ DONE | reviewers.py, integrator.py, producer.py | 입력/출력 500-800자 로깅 |
| 1.5.12 | Cursor 룰 생성 | ✅ DONE | llm-model-evaluation.mdc, AGENTS.md | 모델 비교, 인코딩 규칙 |
| 1.5.13 | ✅ 테스트: gpt-4.1-mini 평가 | ✅ DONE | - | anchored_by 62.2%, 구조 12/12, 달성률 50% |
| 1.5.14 | 모델 비교 테스트 (gpt-4.1-mini, gpt-4o-mini, gpt-5-mini) | ✅ DONE | - | 3개 모델 비교 완료, 최종 선정: gpt-4.1-mini |
| 1.5.15 | 가짜 앵커 방지 강화 | ✅ DONE | producer.py | 쉼표 연결 금지 프롬프트 추가, 가짜 앵커 0개 달성 |
| 1.5.16 | 고유문장 추출 regex 수정 | ✅ DONE | producer.py | extract_unique_sentences() 개선, 3개 추출 성공 |
| 1.5.17 | 🔄 Git Commit: "Phase 1.5 완료" | ✅ DONE | - | commit b9f9b49, 10 files changed |

**최종 성과 (2025-11-09, Phase 1.5 완료):**
- ✅ **구조 완성**: 12/12 섹션 (출발지식, 형식분기, 도메인 리뷰 카드, 통합 기록, 최종 1p)
- ✅ **anchored_by**: 18.2% → **70.5%** (3.9배 개선)
- ✅ **가짜 앵커**: 3개 → **0개** (완전 해결!)
- ✅ **고유문장 추출**: 0개 → **3개** (regex 수정 성공)
- ✅ **앵커 사용**: 11회 → **33회** (3배)
- ✅ **고유 앵커**: 3개 → **5개** (1.7배)
- ✅ **달성률**: 33% → **67%** (+34%p)
- ✅ **모델 비교**: gpt-4.1-mini, gpt-4o-mini, gpt-5-mini 테스트 완료
- ✅ **Temperature 처리**: GPT-5 시리즈 자동 1.0 설정

**해결된 과제:**
- ✅ **가짜 앵커**: 프롬프트 개선으로 완전 해결
- ✅ **고유문장 추출**: regex 패턴 수정으로 정상 작동
- ⚠️ **anchored_by 70.5%**: 목표 100% 미달 (LLM 특성상 한계)

**달성된 품질 기준:**
1. ✅ 구체적인 형식 분기
2. ✅ 풍부한 도메인 리뷰 (책 내용 반영)
3. ✅ 통합지식 앵커 활용
4. ✅ 명확한 긴장축
5. ✅ 완성된 1p 제안서 (12/12 섹션)
6. ✅ 강력한 고유문장 3개 (생성 및 추출 성공)
7. ✅ 실제 KB 앵커 (가짜 앵커 0개)

### 1.6 아키텍처 정리 (Fusion 모드 명확화)

**핵심 결정:**
- ❌ "reduce" 이름 폐기 → ✅ "synthesis" 통일 (긴장축 3개 추출)
- ❌ Fusion Helper 복잡한 구현 → ✅ Phase 2 API에서 간단 추천만
- ✅ Producer 역할 명확화: 1p 제안서 창작만 (조립 로직 분리)

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 1.6.1 | 모드 이름 변경 (reduce → synthesis) | ✅ DONE | state.py, integrator.py, test 코드 변경 완료 |
| 1.6.2 | Producer 리팩토링 | ✅ DONE | Input 최소화 (integration_result + book_summary), 제안서만 창작 |
| 1.6.3 | 최종 1p 조립 함수 분리 | ✅ DONE | utils.assemble_final_1p() + graph.assemble_node() |
| 1.6.4 | ✅ 테스트: 리팩토링 검증 | ✅ DONE | 9개 노드, 가짜 앵커 0개, anchored_by 63.0% |
| 1.6.5 | 🔄 Git Commit: "Phase 1.6 완료" | ✅ DONE | 아키텍처 정리 (커밋 3e1564d) |

**Phase 1.6 성과:**
- ✅ **모드 명확화**: "synthesis" (긴장축 3개) vs "simple_merge" (4개 병치)
- ✅ **Producer 역할 분리**: 제안서 창작만 (조립 로직 분리)
- ✅ **Assemble 노드 추가**: 템플릿 기반 조립 (9개 노드)
- ✅ **Input 최소화**: integration_result + book_summary만
- ✅ **스트리밍 가능 구조**: 각 노드 결과 독립적 표시 가능
- ⚠️ **anchored_by**: 70.5% → 63.0% (조립 과정에서 약간 감소, 추후 개선 가능)

---

## Phase 2: API 레이어 (FastAPI + Supabase)

### 2.1 데이터베이스 (Supabase)

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 2.1.1 | SQL 스키마 작성 (backend/sql/schema.sql) | ✅ DONE | 8개 테이블 + 인덱스 + RLS 정책 |
| 2.1.2 | 인덱스 및 제약조건 설정 | ✅ DONE | FK(ON DELETE CASCADE), 인덱스(user_id, status, anchor_id), GIN(jsonb) |
| 2.1.3 | Row Level Security (RLS) 설정 | ✅ DONE | auth.uid() 기반 격리, kb_items 공개 읽기 전용 |
| 2.1.4 | Supabase 마이그레이션 실행 | ✅ DONE | Dashboard 완료 + CLI 연결 완료 |
| 2.1.5 | ✅ 테스트: 테이블 생성 및 기본 쿼리 | ✅ DONE | 8개 테이블 모두 검증 완료 |
| 2.1.6 | 🔄 Git Commit: "Supabase 스키마 완료" | ✅ DONE | commit f42c522 (6 files, 808 insertions) |

### 2.2 API 엔드포인트

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 2.2.0 | Pydantic 모델 확장 (models/schemas.py) | ✅ DONE | 8개 카테고리, 20+ 모델 정의 |
| 2.2.1 | POST /api/upload (routes/upload.py) | ✅ DONE | CSV 파싱 + bulk insert |
| 2.2.2 | GET /api/books (routes/books.py) | ✅ DONE | JSONB 필터링 + 페이지네이션 |
| 2.2.3 | POST /api/fusion/preview (routes/fusion.py) | ✅ DONE | 도서 수 기반 추천 로직 |
| 2.2.4 | POST /api/runs (routes/runs.py) | ✅ DONE | run 레코드 생성 (백그라운드 작업은 Phase 2.3) |
| 2.2.5 | GET /api/runs/{id} (routes/runs.py) | ✅ DONE | progress_json 반환 |
| 2.2.6 | GET /api/artifacts/{id} (routes/artifacts.py) | ✅ DONE | MD 반환 / PDF 리디렉트 |
| 2.2.7 | POST /api/reminders (routes/reminders.py) | ✅ DONE | 토글 + upsert 로직 |
| 2.2.8 | GET /api/history (routes/history.py) | ✅ DONE | 3-way 조인 (runs + artifacts + reminders) |
| 2.2.9 | Router 등록 (main.py) | ✅ DONE | 7개 라우터 등록 완료 |
| 2.2.10 | ✅ 테스트: API 엔드포인트 (httpx) | ⏳ TODO | tests/test_api_endpoints.py 작성 및 실행 (Phase 2 마무리 시) |
| 2.2.11 | 🔄 Git Commit: "API 엔드포인트 완료" | ✅ DONE | commit ddf3002 (11 files, 920 insertions) |

### 2.3 백그라운드 작업

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 2.3.1 | 작업 매니저 (services/run_service.py) | ✅ DONE | execute_pipeline + update 헬퍼 함수들 |
| 2.3.2 | LangGraph 비동기 실행 | ✅ DONE | graph.stream() + 노드별 진행률 (9개 노드 매핑) |
| 2.3.3 | Supabase Storage 통합 | ✅ DONE | artifact 레코드 생성 (Storage는 placeholder) |
| 2.3.4 | 진행률 업데이트 | ✅ DONE | progress_json: {current_node, percent, timestamp} |
| 2.3.5 | 에러 처리 | ✅ DONE | try-except + status="failed" + error_message |
| 2.3.6 | POST /api/runs 백그라운드 작업 연결 | ✅ DONE | BackgroundTasks.add_task(execute_pipeline_async) |
| 2.3.7 | ✅ 테스트: 백그라운드 작업 실행 | ✅ DONE | E2E 성공: CSV → Books → Fusion → Run (28.6s) → History |
| 2.3.8 | 🔄 Git Commit: "백그라운드 작업 완료" | ✅ DONE | commit ee10dd7 (8 files, 670 insertions) |

### 2.4 인증

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 2.4.1 | JWT 검증 함수 (core/auth.py) | ✅ DONE | verify_supabase_token + get_current_user (Skeleton) |
| 2.4.2 | 인증 Dependency | ✅ DONE | require_auth, get_optional_user (비동기 지원) |
| 2.4.3 | 엔드포인트 보호 | ✅ DONE | books, runs, history에 user_id = Depends(require_auth) 추가 |
| 2.4.4 | ✅ 테스트: 인증 플로우 | ✅ DONE | E2E 테스트 통과 (인증 헤더 포함) |
| 2.4.5 | 🔄 Git Commit: "Phase 2 완료" | ✅ DONE | commit d27534a (6 files, 154 insertions) |

---

## Phase 3: 프론트엔드 UI (Next.js)

### 3.1 프로젝트 초기화

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 3.1.1 | Next.js 14+ 프로젝트 생성 | ✅ DONE | App Router, TypeScript, TailwindCSS |
| 3.1.2 | 필수 패키지 설치 | ✅ DONE | Supabase, React Query, Zustand, axios |
| 3.1.3 | shadcn/ui 초기화 및 컴포넌트 | ✅ DONE | button, card, input, label, select, badge, progress, sonner |
| 3.1.4 | 환경 변수 설정 (.env.local) | ✅ DONE | API_URL, SUPABASE_URL, SUPABASE_ANON_KEY |
| 3.1.5 | 핵심 유틸리티 파일 | ✅ DONE | lib/supabase.ts, lib/api.ts, lib/query-client.ts |
| 3.1.6 | 레이아웃 및 Provider 설정 | ✅ DONE | app/layout.tsx, app/providers.tsx (React Query Provider, Sonner) |
| 3.1.7 | Supabase Auth UI 통합 | ✅ DONE | app/auth/page.tsx, middleware.ts (@supabase/ssr) |
| 3.1.8 | 사용자 정보 훅 | ✅ DONE | hooks/useUser.ts (세션 관리, 로그아웃) |
| 3.1.9 | ✅ 테스트: 프론트엔드 실행 확인 | ✅ DONE | npm run dev (http://localhost:3000), 인증 리디렉트 확인 |
| 3.1.10 | 🔄 Git Commit: "프론트엔드 초기화" | ⏳ TODO | Next.js + 라이브러리 + 인증 설정 |

### 3.2 화면 구현

| ID | 화면 | Status | 주요 작업 | 비고 |
|----|------|--------|----------|------|
| 3.2.1 | /library | ✅ DONE | CSV 업로드(drag&drop), 최근 6개 결과물 그리드, 업로드된 라이브러리 목록(Collapsible), 라이브러리 삭제 | components/csv-upload.tsx, history-card.tsx, Collapsible |
| 3.2.2 | /books/select | ✅ DONE | 3열 레이아웃, 필터(도메인/연도/주제), 도서 선택, Zustand 상태 관리, 중복 도서 제거 | components/book-filter.tsx, book-list.tsx, book-selection-panel.tsx |
| 3.2.3 | /fusion | ✅ DONE | POST /api/fusion/preview, 추천/대안 카드 비교, POST /api/runs 실행, 페이지 이동 시 상태 유지 | components/fusion-card.tsx |
| 3.2.4 | /runs/[id] | ✅ DONE | 2초 폴링, 9개 노드 실시간 상태 표시, 완료 시 자동 이동, 노드 이름 동기화 | components/progress-bar.tsx, hooks/useRunProgress.ts |
| 3.2.5 | /preview/[id] | ✅ DONE | Markdown 렌더링(react-markdown), 앵커 토글, MD 다운로드, 리마인드 설정 | react-markdown, remark-gfm, Artifacts API JSON 반환 |
| 3.2.6 | /history | ✅ DONE | 히스토리 목록(페이지네이션), 복습 카드 섹션, 항목 클릭 시 미리보기 | history-card 재사용 |
| 3.2.7 | ✅ 테스트: 각 화면 API 연동 확인 | ✅ DONE | 백엔드 API 호출 및 응답 검증, 주요 플로우 테스트 완료 |
| 3.2.8 | ✅ 테스트: E2E 사용자 플로우 | ✅ DONE | Library → Books → Fusion → Runs → Preview 기본 플로우 확인 |
| 3.2.9 | 🔄 Git Commit: "Phase 3 완료" | ✅ DONE | Phase 3.3 커밋에 포함 (commit 8560656) |

**Phase 3 주요 수정 및 개선:**
- ✅ API Contract Sync: `.cursor/rules/api-contract-sync.mdc` 생성 (백엔드-프론트엔드 계약 동기화 규칙)
- ✅ 노드 이름 동기화: 백엔드 `anchor_mapper` ↔ 프론트엔드 `ProgressBar` 일치
- ✅ Artifacts API 개선: JSON 반환 + `/download` 엔드포인트 분리
- ✅ OPENAI_API_KEY 설정: `main.py`에서 `os.environ` 명시적 설정
- ✅ Run State 초기화: `create_initial_state` 헬퍼 함수 사용, `book_ids` 리스트 전달
- ✅ 도메인 필터 동기화: 프론트엔드 `DOMAINS` 배열에 슬래시 포함 (`경제/경영`)
- ✅ 실시간 진행바: 2초 폴링으로 노드별 상태 업데이트 확인
- ✅ Preview 페이지: Markdown 렌더링 정상 작동, content 표시

### 3.3 품질 개선 (KB Service 초기화)

**문제 분석:**
- ⚠️ KB Service 초기화: vectorizer 미초기화 경고 (`[WARN] No candidates or vectorizer not initialized`)
- ⚠️ anchored_by 품질: 24.4% (목표 100%), 백엔드 Phase 1.5 수준(70.5%)과 격차
- ⚠️ 가짜 앵커: 4개 발견 (`anchor_긴장축1`, `anchor_통합지식` 등)
- ⚠️ available_anchors 미전달: Producer에서 가짜 앵커 방지 기능 미작동

**근본 원인:**
- `backend/services/kb_service.py` Line 301에서 global instance 생성하지만 `load_all_domains()` 미호출
- `backend/main.py` 앱 시작 시 KB 초기화 로직 없음
- `kb_service.all_items`가 비어있어 `available_anchors`가 빈 리스트로 전달

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 3.3.1 | KB Service 자동 로드 (kb_service.py) | ✅ DONE | 모듈 import 시 자동 로드, 경로 수정 |
| 3.3.2 | 네비게이션 바 추가 (navbar.tsx) | ✅ DONE | 전체 페이지에 홈/라이브러리/히스토리 네비 |
| 3.3.3 | 히스토리 카드 개선 | ✅ DONE | 출발 지식(제목+저자), 1p 제목, CTA 표시 |
| 3.3.4 | 히스토리 카드 삭제 기능 | ✅ DONE | DELETE /api/runs/{id}, 권한 검증 |
| 3.3.5 | 출발 지식 가독성 개선 | ✅ DONE | 각 항목 개행, **굵게** 표시 |
| 3.3.6 | 형식 분기 간소화 | ✅ DONE | Synthesis/Simple Merge 모두 간단히 |
| 3.3.7 | 통합 기록 간소화 (simple_merge) | ✅ DONE | 도메인 리뷰 참조로 간소화 |
| 3.3.8 | 도메인 통일 (constants) | ✅ DONE | backend/core/constants.py, frontend/lib/constants.ts |
| 3.3.9 | 히스토리 날짜별/분야별 Tabs | ✅ DONE | Tabs + Collapsible, domain 필드 추가 |
| 3.3.10 | 🔄 Git Commit: "Phase 3.3 완료" | ✅ DONE | commit 8560656 (71 files, 14,799 insertions) |

**Phase 3.3 최종 성과:**
- ✅ KB Service 자동 로드 (144개 항목)
- ✅ KB 파일 경로 수정 (작업 디렉토리 독립적)
- ✅ 네비게이션 바 (전체 페이지)
- ✅ 히스토리 카드 개선 (출발 지식, 1p 제목, CTA)
- ✅ 히스토리 삭제 기능
- ✅ 1p 템플릿 개선 (출발 지식 가독성, 형식 분기/통합 기록 간소화)
- ✅ 도메인 통일 (backend/core/constants.py, frontend/lib/constants.ts)
- ✅ 히스토리 날짜별/분야별 Tabs
- ✅ 프론트엔드 6개 화면 완성

---

## Phase 4: 통합 및 테스트

### 4.1 End-to-End 테스트

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 4.1.1 | 테스트 시나리오 작성 | ⏳ TODO | PRD 수용 기준 기반 |
| 4.1.2 | CSV 업로드 → 도서 선택 | ⏳ TODO | 80~90권 CSV |
| 4.1.3 | 3권 선택 → 1p 3건 생성 | ⏳ TODO | 각각 다른 모드 |
| 4.1.4 | Validator 검증 통과 | ⏳ TODO | anchored_by=100%, 고유문장≥3 |
| 4.1.5 | 히스토리 저장 및 재다운로드 | ⏳ TODO | 3건 모두 확인 |
| 4.1.6 | 리마인드 큐 및 복습 카드 | ⏳ TODO | 미리보기 동작 |

### 4.2 성능 검증

| ID | 작업 내용 | Status | 목표 |
|----|----------|--------|------|
| 4.2.1 | 생성 성공률 측정 | ⏳ TODO | ≥ 98% |
| 4.2.2 | 평균 생성 시간 | ⏳ TODO | ≤ 30s (단일 도서) |
| 4.2.3 | PDF 발행 시간 | ⏳ TODO | < 3s |
| 4.2.4 | 동시성 테스트 | ⏳ TODO | 30명 동시 |

### 4.3 문서화 및 배포

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 4.3.1 | README.md 작성 | ⏳ TODO | 설치/실행 가이드 |
| 4.3.2 | API 문서 (FastAPI) | ⏳ TODO | /docs, /redoc |
| 4.3.3 | .env.example | ⏳ TODO | 환경 변수 예시 |
| 4.3.4 | 🔄 Git Commit: "Phase 4 완료 - MVP 완성" | ⏳ TODO | 최종 릴리스 |

---

## 추가 필수 패키지

### Python (pyproject.toml에 추가)
- `fastapi`, `uvicorn[standard]`, `python-multipart`
- `supabase`, `postgrest`
- `reportlab` (PDF 생성)
- `httpx` (HTTP 클라이언트)

**이미 설치됨:** langgraph, langchain, langchain-openai, langchain-teddynote, pydantic, python-dotenv

### JavaScript (frontend/package.json)
- `next`, `react`, `react-dom`
- `@supabase/supabase-js`
- `@tanstack/react-query`, `zustand`
- `tailwindcss`, `axios`

---

## LangGraph 핵심 패턴 (참고)

### State 정의
- `TypedDict` + `Annotated[list, operator.add]` 사용
- messages, reviews, unique_sentences 등 누적 필드는 operator.add

### 노드 구현
- `create_react_agent(llm, tools=[...])` + `functools.partial`
- 각 노드는 `state`를 받고 `dict` 반환 (부분 업데이트)

### 병렬 처리
- `Send()` API로 4개 Reviewer 동시 실행
- `workflow.add_conditional_edges(source, function, destinations)`

### 재시도
- `MemorySaver()` + `workflow.compile(checkpointer=memory)`
- `thread_id`로 실패 지점 재개

### 진행률 추적
- `graph.stream(inputs, config)` 사용
- 각 노드 이벤트를 DB에 저장 → 프론트엔드 폴링/SSE

**참고 파일:** `docs/07-LangGraph-Multi-Agent-Supervisor.ipynb`, `docs/10-LangGraph-Research-Assistant.ipynb`

---

## 파일 구조 (핵심)

```
ideator-books/
├── backend/
│   ├── main.py
│   ├── core/ (config, database)
│   ├── langgraph_pipeline/ (graph, state, nodes/, utils)
│   ├── services/ (kb_service, book_service, fusion_service)
│   ├── models/ (schemas)
│   ├── tools/ (kb_search)
│   └── api/routes/ (upload, books, runs, history)
├── frontend/
│   ├── app/ (6개 페이지)
│   ├── components/ (4개 핵심 컴포넌트)
│   ├── lib/ (api, supabase)
│   └── hooks/ (useRunProgress)
├── docs/ (PRD, KB 4개, 노트북 2개)
└── TODOs.md (이 파일)
```

---

## 상태 범례
- ⏳ TODO: 시작 전
- 🚧 IN PROGRESS: 진행 중
- ✅ DONE: 완료
- ⚠️ BLOCKED: 차단됨
- 🔄 REVIEW: 검토 중

---

## 수용 기준 (MVP Done)
- [ ] CSV 80~90권 → 3권 선택 → 1p 3건 생성 성공
- [ ] anchored_by 100%, 고유문장 3개 검증 통과
- [ ] 리마인드 큐 및 복습 카드 제공
- [ ] 히스토리 3건 저장 & 재다운로드 가능

## KPI 목표
- 생성 성공률 ≥ 98%
- 평균 생성 시간 ≤ 30s
- 승인 라운드 = 1
- 복습 카드 클릭률 ≥ 35%

---

## 참고 자료
- **PRD**: `docs/PRD_ideator-books.md`
- **KB**: `docs/지식베이스생성_*.md` (4개 도메인)
- **LangGraph 패턴**: `docs/07-LangGraph-Multi-Agent-Supervisor.ipynb`, `docs/10-LangGraph-Research-Assistant.ipynb`
