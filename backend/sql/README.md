# Supabase Database Migration Guide

## 개요
이 디렉토리에는 ideator-books 프로젝트의 Supabase 데이터베이스 스키마가 포함되어 있습니다.

## 마이그레이션 실행 방법

### 방법 1: Supabase Dashboard (권장)

1. **Supabase Dashboard 접속**
   - https://supabase.com/dashboard 로그인
   - 프로젝트 선택: `xsrbxmhrnamsyhldjuju`

2. **SQL Editor 열기**
   - 왼쪽 메뉴에서 "SQL Editor" 클릭
   - "New query" 버튼 클릭

3. **스키마 실행**
   - `schema.sql` 파일 내용을 복사하여 붙여넣기
   - "RUN" 버튼 클릭
   - 실행 결과 확인 (약 2-3초 소요)

4. **테이블 확인**
   - 왼쪽 메뉴에서 "Table Editor" 클릭
   - 8개 테이블 생성 확인:
     - users
     - libraries
     - books
     - kb_items
     - runs
     - artifacts
     - reminders
     - audits

### 방법 2: Supabase CLI (고급)

```powershell
# Supabase CLI 설치 (이미 설치되어 있지 않은 경우)
scoop install supabase

# 프로젝트 연결
supabase link --project-ref xsrbxmhrnamsyhldjuju

# 마이그레이션 실행
supabase db push
```

## 테이블 구조

### 1. users (사용자 프로필)
- Supabase Auth 확장
- 기본 프로필 정보 (email, name)

### 2. libraries (CSV 컬렉션)
- 사용자가 업로드한 CSV 파일 그룹
- 1명의 사용자는 여러 라이브러리 소유 가능

### 3. books (도서 메타데이터)
- 개별 도서 정보
- meta_json: {title, author, year, domain, topic, summary}

### 4. kb_items (지식베이스)
- 4개 도메인(경제경영, 과학기술, 역사사회, 인문자기계발) KB
- anchor_id로 참조 가능
- is_fusion: 융합형 인사이트 여부
- is_integrated_knowledge: 통합지식 여부

### 5. runs (1p 생성 작업)
- 1-pager 생성 job 추적
- params_json: {book_ids, mode, format, remind_enabled}
- progress_json: {current_node, percent, timestamp}
- status: pending → running → completed/failed

### 6. artifacts (생성 결과물)
- MD/PDF 형식의 1p 파일
- Supabase Storage URL 저장

### 7. reminders (복습 큐)
- 사용자별 리마인드 설정
- active: true/false 토글

### 8. audits (검증 로그)
- anchored_by_ok: 100% KB 앵커 검증
- unique3_ok: 고유문장 3개 이상
- external0_ok: 외부 프레임 0개

## Row Level Security (RLS)

### 정책 요약
- **users**: 본인 프로필만 조회/수정
- **libraries**: 본인 라이브러리만 CRUD
- **books**: 본인 라이브러리의 도서만 조회/생성
- **kb_items**: 모든 사용자 읽기 가능 (공개)
- **runs**: 본인 run만 CRUD
- **artifacts**: 본인 run의 artifact만 조회/생성
- **reminders**: 본인 reminder만 CRUD
- **audits**: 본인 run의 audit만 조회

## 인덱스

### 성능 최적화를 위한 인덱스
- **FK 인덱스**: user_id, library_id, run_id
- **필터 인덱스**: status, domain, anchor_id
- **GIN 인덱스**: JSONB 컬럼 (meta_json)
- **복합 인덱스**: (user_id, active), (schedule)

## 테스트

### 기본 쿼리 테스트

```sql
-- 1. 테이블 생성 확인
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- 2. RLS 활성화 확인
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

-- 3. 인덱스 확인
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
ORDER BY tablename, indexname;

-- 4. 정책 확인
SELECT policyname, tablename, cmd, qual 
FROM pg_policies 
WHERE schemaname = 'public' 
ORDER BY tablename, policyname;
```

## 문제 해결

### 에러: "relation already exists"
- 테이블이 이미 존재하는 경우
- 해결: DROP TABLE 후 재실행 또는 `IF NOT EXISTS` 확인

### 에러: "permission denied"
- 서비스 역할 키가 아닌 anon 키 사용 시
- 해결: Dashboard에서 실행 (자동으로 서비스 역할 사용)

### RLS 테스트 실패
- auth.uid() null 반환
- 해결: 실제 JWT 토큰으로 인증 후 테스트

## 다음 단계

1. ✅ 스키마 실행 완료
2. ⏳ KB 데이터 로드 (backend/services/kb_service.py)
3. ⏳ API 엔드포인트 구현 (backend/api/routes/)
4. ⏳ 백그라운드 작업 구현 (backend/services/run_service.py)

