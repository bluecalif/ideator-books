# Ideator Books - KB 기반 1-Pager 생성 서비스

전문가 지식 베이스(KB)를 활용하여 도서로부터 1-Page 제안서를 자동 생성하는 AI 서비스

## 📋 프로젝트 개요

- **목표**: 4개 도메인(경제/경영, 과학/기술, 역사/사회, 인문/자기계발) KB를 활용한 증거 기반 1p 생성
- **기술 스택**: 
  - Backend: FastAPI + LangGraph + OpenAI GPT-4.1-mini
  - Frontend: Next.js 14 (App Router) + TypeScript + TailwindCSS + shadcn/ui
  - Database: Supabase (PostgreSQL + Auth)
  - KB: 144개 전문가 인사이트 (TF-IDF 검색)

## 🏗️ 아키텍처

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Next.js    │────▶│  FastAPI     │────▶│  Supabase   │
│  Frontend   │◀────│  Backend     │◀────│  PostgreSQL │
│  (Port 3000)│     │  (Port 8000) │     │  + Auth     │
└─────────────┘     └──────────────┘     └─────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  LangGraph   │
                    │  Pipeline    │
                    │  (9 nodes)   │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  KB Service  │
                    │  (144 items) │
                    └──────────────┘
```

## 🚀 빠른 시작

### 1. 사전 요구사항

- Python 3.10+
- Node.js 18+
- OpenAI API Key
- Supabase 프로젝트

### 2. 환경 변수 설정

#### 백엔드 (.env)
```bash
# OpenAI
OPENAI_API_KEY=sk-your-api-key

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# API 설정
API_HOST=127.0.0.1
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

#### 프론트엔드 (frontend/.env.local)
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
```

### 3. 데이터베이스 설정

Supabase Dashboard에서 SQL Editor 실행:

```sql
-- backend/sql/schema.sql 내용 실행
-- 8개 테이블 생성: users, libraries, books, kb_items, runs, artifacts, reminders, audits
```

### 4. 백엔드 실행

```powershell
# 프로젝트 루트에서
cd backend
$env:PYTHONPATH = "C:\Projects\vibe-coding\ideator-books"
python -m uvicorn main:app --reload --port 8000
```

**확인**: http://localhost:8000/docs → FastAPI Swagger UI

### 5. 프론트엔드 실행

```powershell
# 새 터미널에서
cd frontend
npm install
npm run dev
```

**확인**: http://localhost:3000 → Next.js 앱

## 📊 주요 기능

### 1. **도서 라이브러리 관리** (`/library`)
- CSV 업로드 (Drag & Drop)
- 업로드된 라이브러리 목록
- 최근 생성 결과물 6개 표시

### 2. **도서 선택** (`/books/select`)
- 3열 레이아웃 (필터 | 도서 목록 | 선택 패널)
- 도메인/연도/주제 필터링
- 최대 10권 선택

### 3. **Fusion 모드 선택** (`/fusion`)
- **Synthesis**: 긴장축 2-3개 추출
- **Simple Merge**: 4개 도메인 병치
- AI 기반 추천

### 4. **생성 진행** (`/runs/[id]`)
- 9개 노드 실시간 진행률 표시
- 2초 폴링
- 평균 30-40초 소요

### 5. **1p 미리보기** (`/preview/[id]`)
- Markdown 렌더링
- 앵커 토글 (KB 참조 표시/숨김)
- MD 다운로드
- 리마인드 설정

### 6. **히스토리** (`/history`)
- 복습 카드 섹션 (리마인드 활성화된 항목)
- 날짜별/분야별 Tabs
- 삭제 기능

## 🔍 LangGraph 파이프라인 (9개 노드)

```
START
  ↓
AnchorMapper (각 도메인별 KB 앵커 매핑)
  ↓
4개 Reviewer (병렬 실행)
  ├─ 경제/경영
  ├─ 과학/기술
  ├─ 역사/사회
  └─ 인문/자기계발
  ↓
Integrator (긴장축 추출 or 병치)
  ↓
Producer (1p 제안서 창작)
  ↓
Assemble (최종 조립)
  ↓
Validator (품질 검증)
  ↓
END
```

## 📈 품질 지표

**Phase 1.5 (백엔드 단독)**:
- anchored_by: **70.5%**
- 가짜 앵커: **0개**
- 고유문장: **3개**
- 구조: **12/12 섹션**

**Phase 3.3 (통합 후)**:
- KB 항목: **144개** 로드
- anchored_by: **45%+** (LLM 특성상 변동)
- 가짜 앵커: **5개 이하** (통합지식 앵커 등)
- 생성 시간: **30-40초**

## 🗂️ 프로젝트 구조

```
ideator-books/
├── backend/                    # FastAPI 백엔드
│   ├── main.py                # 앱 엔트리포인트
│   ├── core/                  # 설정, DB, 인증
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── auth.py
│   │   └── constants.py       # 도메인 정의
│   ├── langgraph_pipeline/    # 1p 생성 파이프라인
│   │   ├── graph.py           # 워크플로우 정의
│   │   ├── state.py           # State 정의
│   │   ├── nodes/             # 9개 노드
│   │   └── utils.py           # 조립 함수
│   ├── services/              # 비즈니스 로직
│   │   ├── kb_service.py      # KB 파싱 및 검색
│   │   ├── book_service.py
│   │   └── run_service.py     # 백그라운드 작업
│   ├── api/routes/            # API 엔드포인트
│   │   ├── upload.py
│   │   ├── books.py
│   │   ├── fusion.py
│   │   ├── runs.py
│   │   ├── artifacts.py
│   │   ├── reminders.py
│   │   └── history.py
│   ├── models/                # Pydantic 스키마
│   └── sql/                   # DB 스키마
├── frontend/                  # Next.js 프론트엔드
│   ├── app/                   # 6개 페이지
│   │   ├── library/
│   │   ├── books/select/
│   │   ├── fusion/
│   │   ├── runs/[id]/
│   │   ├── preview/[id]/
│   │   └── history/
│   ├── components/            # UI 컴포넌트
│   │   ├── ui/                # shadcn/ui
│   │   ├── navbar.tsx
│   │   ├── history-card.tsx
│   │   └── progress-bar.tsx
│   ├── lib/                   # 유틸리티
│   │   ├── api.ts             # API 클라이언트
│   │   ├── supabase.ts
│   │   └── constants.ts       # 도메인 정의
│   └── hooks/
│       ├── useUser.ts
│       └── useRunProgress.ts
└── docs/                      # 문서 및 KB
    ├── PRD_ideator-books.md
    └── 지식베이스생성_*.md    # 4개 도메인 KB
```

## 🔑 핵심 설계 원칙

### 1. **Single Source of Truth**
- 도메인 이름: `backend/core/constants.py`, `frontend/lib/constants.ts`
- KB와 DB의 도메인 매핑 관리

### 2. **API Contract Sync**
- Request/Response 스키마 일치 (Pydantic ↔ TypeScript)
- 필드명 통일 (`params_json`, `progress_json`)

### 3. **1권당 1p**
- 복잡도 감소
- 병렬 처리 대비 안정성 우선

### 4. **No Retry**
- Validator 실패해도 1회만 실행
- LLM 비용 절감

## 🧪 테스트

### 백엔드 테스트
```powershell
$env:PYTHONPATH = "C:\Projects\vibe-coding\ideator-books"
python backend\tests\test_database_schema.py
```

### API 테스트
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### E2E 플로우
1. Library → CSV 업로드 (87권)
2. Books → 1권 선택
3. Fusion → Synthesis 모드
4. Runs → 진행 확인 (약 40초)
5. Preview → 1p 확인 및 다운로드
6. History → 히스토리 확인

## 📝 MVP 수용 기준

- [x] CSV 80~90권 → 1p 생성 성공
- [x] 히스토리 저장 및 재다운로드
- [x] 리마인드 큐 UI
- [x] 평균 생성 시간 ≤ 40s
- [x] 프론트엔드 6개 화면
- [x] 백엔드 7개 API 엔드포인트

## 🐛 알려진 이슈

- **anchored_by**: 목표 100% vs 실제 45-70% (LLM 특성상 한계)
- **가짜 앵커**: 통합지식 앵커 등 일부 발생 (5개 이하)
- **PDF 생성**: Placeholder (reportlab 구현 대기)

## 📚 참고 자료

- **PRD**: `docs/PRD_ideator-books.md`
- **KB**: `docs/지식베이스생성_*.md` (4개 도메인)
- **LangGraph 패턴**: `docs/07-LangGraph-Multi-Agent-Supervisor.ipynb`
- **Cursor Rules**: `.cursor/rules/*.mdc`

## 📞 개발 가이드

### PowerShell 명령어
- **환경변수 설정**: `$env:PYTHONPATH = "C:\Projects\vibe-coding\ideator-books"`
- **명령어 연결**: 세미콜론 `;` 사용 (`cd backend; python main.py`)
- **프로세스 종료**: `taskkill /F /PID [PID]`

### 주요 규칙
- **이모지 사용 금지**: PowerShell 인코딩 이슈 (cp949)
- **로그 형식**: `[OK]`, `[FAIL]`, `[WARN]` 태그 사용
- **.env 파일 확인**: `Get-Content .env -Force`

## 🎯 KPI

- 생성 성공률: **98%+** (목표)
- 평균 생성 시간: **30-40초** (달성)
- anchored_by: **45-70%** (현재)
- 복습 카드 클릭률: **35%+** (목표)

## 📜 라이선스

MIT License

## 🤝 기여

이 프로젝트는 MVP 개발 단계입니다. 이슈 및 PR은 환영합니다!

---

**개발**: bluecalif  
**저장소**: https://github.com/bluecalif/ideator-books.git  
**버전**: 0.1.0 (MVP)

