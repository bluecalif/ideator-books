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
| 1.2.6 | 🔄 Git Commit: "KB 처리 시스템 완료" | ⏳ TODO | 파서 + 검색 + 테스트 |

### 1.3 LangGraph State 및 그래프 정의

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 1.3.1 | OnePagerState 정의 (state.py) | ⏳ TODO | TypedDict, Annotated, operator.add |
| 1.3.2 | LangGraph 구조 정의 (graph.py) | ⏳ TODO | StateGraph, 노드 연결, Send() API |
| 1.3.3 | 체크포인트 저장 (MemorySaver) | ⏳ TODO | 실패 시 재시도 |
| 1.3.4 | 🔄 Git Commit: "LangGraph State 정의" | ⏳ TODO | State + 그래프 골격 |

### 1.4 LangGraph 노드 구현

| ID | 작업 내용 | Status | 구현 패턴 | 비고 |
|----|----------|--------|----------|------|
| 1.4.1 | AnchorMapper | ⏳ TODO | LLM + KB 검색 | 도서→4도메인 앵커 매핑 |
| 1.4.2 | Reviewer_경제경영 | ⏳ TODO | create_react_agent | 장점·문제·조건 |
| 1.4.3 | Reviewer_과학기술 | ⏳ TODO | create_react_agent | 장점·문제·조건 |
| 1.4.4 | Reviewer_역사사회 | ⏳ TODO | create_react_agent | 장점·문제·조건 |
| 1.4.5 | Reviewer_인문자기계발 | ⏳ TODO | create_react_agent | 장점·문제·조건 |
| 1.4.6 | Integrator (Reduce) | ⏳ TODO | LLM structured output | 긴장축 2-3 + 결론 |
| 1.4.7 | Integrator (단순병합) | ⏳ TODO | 병치 로직 | 4도메인 병치 + 결론 |
| 1.4.8 | Producer (MD) | ⏳ TODO | LLM + 템플릿 | 동적 레이아웃 |
| 1.4.9 | Producer (PDF) | ⏳ TODO | reportlab | MD → PDF |
| 1.4.10 | Validator | ⏳ TODO | 규칙 기반 | anchored_by=100%, 고유문장≥3 |
| 1.4.11 | ✅ 테스트: 단일 노드 테스트 (AnchorMapper) | ⏳ TODO | 실제 KB 데이터 사용 |
| 1.4.12 | ✅ 테스트: 전체 파이프라인 실행 | ⏳ TODO | 샘플 도서 요약으로 end-to-end |
| 1.4.13 | 🔄 Git Commit: "LangGraph 노드 구현 완료" | ⏳ TODO | 5개 노드 + 테스트 |

**구현 핵심:**
- Reviewers: functools.partial + Send() API로 병렬 실행
- Integrator: Pydantic 모델로 structured output
- Validator: 정규식 + 카운팅, 실패 시 에러 메시지

### 1.5 Fusion Helper

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 1.5.1 | Fusion Helper 서비스 | ⏳ TODO | 모드 추천 로직 (Reduce vs 단순병합) |
| 1.5.2 | 샘플 2문장 생성 | ⏳ TODO | 각 모드별 미리보기 |
| 1.5.3 | ✅ 테스트: Fusion Helper 실행 | ⏳ TODO | 3권 샘플로 추천 검증 |
| 1.5.4 | 🔄 Git Commit: "Phase 1 완료" | ⏳ TODO | 백엔드 핵심 로직 |
| 1.5.5 | 📋 Phase 1 후속 검토: KB 통합지식 파싱 추가 여부 | ⏳ TODO | LangGraph 완성 후 Integrator 노드에서 필요성 판단. 현재는 128개 개별 인사이트만 사용 |

---

## Phase 2: API 레이어 (FastAPI + Supabase)

### 2.1 데이터베이스 (Supabase)

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 2.1.1 | SQL 스키마 작성 | ⏳ TODO | 7개 테이블 (users, libraries, books, kb_items, runs, artifacts, reminders, audits) |
| 2.1.2 | 인덱스 및 외래키 설정 | ⏳ TODO | 성능 최적화 |
| 2.1.3 | Row Level Security (RLS) 설정 | ⏳ TODO | 사용자별 데이터 격리 |
| 2.1.4 | ✅ 테스트: Supabase 연결 및 쿼리 | ⏳ TODO | 테이블 생성/조회 확인 |
| 2.1.5 | 🔄 Git Commit: "Supabase 스키마 완료" | ⏳ TODO | SQL + 마이그레이션 |

### 2.2 API 엔드포인트

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 2.2.1 | POST /api/upload | ⏳ TODO | CSV 업로드 |
| 2.2.2 | GET /api/books | ⏳ TODO | 도서 조회 (필터) |
| 2.2.3 | POST /api/fusion/preview | ⏳ TODO | Fusion Helper |
| 2.2.4 | POST /api/runs | ⏳ TODO | 1p 생성 요청 |
| 2.2.5 | GET /api/runs/{id} | ⏳ TODO | 진행 상태 |
| 2.2.6 | GET /api/artifacts/{id} | ⏳ TODO | MD/PDF 다운로드 |
| 2.2.7 | POST /api/reminders | ⏳ TODO | 리마인드 on/off |
| 2.2.8 | GET /api/history | ⏳ TODO | 히스토리 목록 |
| 2.2.9 | ✅ 테스트: API 엔드포인트 (curl/httpx) | ⏳ TODO | 각 엔드포인트 응답 확인 |
| 2.2.10 | 🔄 Git Commit: "API 엔드포인트 완료" | ⏳ TODO | 8개 엔드포인트 + 테스트 |

### 2.3 백그라운드 작업

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 2.3.1 | 백그라운드 작업 매니저 | ⏳ TODO | FastAPI BackgroundTasks |
| 2.3.2 | LangGraph 비동기 실행 | ⏳ TODO | graph.stream() 사용 |
| 2.3.3 | 진행률 업데이트 | ⏳ TODO | 각 노드 완료 시 DB 업데이트 |
| 2.3.4 | 에러 처리 및 재시도 | ⏳ TODO | thread_id 기반 재개 |
| 2.3.5 | ✅ 테스트: 백그라운드 작업 실행 | ⏳ TODO | 1p 생성 end-to-end |
| 2.3.6 | 🔄 Git Commit: "백그라운드 작업 완료" | ⏳ TODO | 비동기 실행 + 진행률 추적 |

### 2.4 인증

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 2.4.1 | Supabase Auth 연동 | ⏳ TODO | JWT 검증 |
| 2.4.2 | 인증 미들웨어 | ⏳ TODO | @require_auth |
| 2.4.3 | ✅ 테스트: 인증 플로우 | ⏳ TODO | 로그인/JWT 검증 |
| 2.4.4 | 🔄 Git Commit: "Phase 2 완료" | ⏳ TODO | API 레이어 전체 |

---

## Phase 3: 프론트엔드 UI (Next.js)

### 3.1 프로젝트 초기화

| ID | 작업 내용 | Status | 비고 |
|----|----------|--------|------|
| 3.1.1 | Next.js 14+ 프로젝트 생성 | ⏳ TODO | App Router |
| 3.1.2 | TailwindCSS + shadcn/ui | ⏳ TODO | UI 라이브러리 |
| 3.1.3 | Supabase 클라이언트 | ⏳ TODO | @supabase/supabase-js |
| 3.1.4 | React Query + Zustand | ⏳ TODO | 상태 관리 |
| 3.1.5 | ✅ 테스트: 프론트엔드 실행 확인 | ⏳ TODO | npm run dev, http://localhost:3000 |
| 3.1.6 | 🔄 Git Commit: "프론트엔드 초기화" | ⏳ TODO | Next.js + 라이브러리 설정 |

### 3.2 화면 구현

| ID | 화면 | Status | 비고 |
|----|------|--------|------|
| 3.2.1 | /library | ⏳ TODO | CSV 업로드, 최근 결과물 6개 |
| 3.2.2 | /books/select | ⏳ TODO | 3열 레이아웃 (필터/목록/옵션) |
| 3.2.3 | /fusion | ⏳ TODO | 추천 vs 대안 카드 비교 |
| 3.2.4 | /runs/[id] | ⏳ TODO | 진행 바 + 노드별 상태 |
| 3.2.5 | /preview/[id] | ⏳ TODO | 1p 미리보기 + 앵커 토글 |
| 3.2.6 | /history | ⏳ TODO | 히스토리 카드 + 복습 카드 |
| 3.2.7 | ✅ 테스트: 각 화면 UI/UX 확인 | ⏳ TODO | 반응형, 데이터 로딩 |
| 3.2.8 | 🔄 Git Commit: "Phase 3 완료" | ⏳ TODO | 프론트엔드 6개 화면 |

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
