# AI 에이전트 운영 가이드

> **환경**: Windows PowerShell 5.1  
> **프로젝트**: ideator-books (Next.js + FastAPI + LangGraph)

---

## 1. PowerShell 명령어 표준

### 1.1 명령어 연결

```powershell
# ✅ 세미콜론 사용
cd C:\Projects\ideator-books; python -m pytest tests/

# ❌ Bash && 연산자 사용 금지
cd C:\Projects\ideator-books && python -m pytest tests/
```

### 1.2 환경 변수

```powershell
# 설정
$env:PYTHONPATH = "C:\Projects\vibe-coding\ideator-books"
$env:OPENAI_API_KEY = "sk-xxx"

# 확인
echo $env:OPENAI_API_KEY
Get-ChildItem Env:
```

### 1.3 디렉토리 및 파일

```powershell
# 디렉토리 생성 (부모 디렉토리 자동 생성)
New-Item -ItemType Directory -Path "backend\api\models" -Force

# 파일 작업
Get-Content file.txt          # 읽기
Copy-Item src.txt dst.txt     # 복사
Remove-Item file.txt          # 삭제
Test-Path .env                # 존재 확인
```

### 1.4 Python 실행

```powershell
# 스크립트 실행
python backend/tests/test_kb_parser.py
python -m pytest backend/tests/ -v

# 환경 변수 설정 후 실행
$env:LOG_LEVEL = "DEBUG"; python script.py

# Python -c (작은따옴표 사용)
python -c 'print("Hello")'
```

### 1.5 서버 실행

```powershell
# 백엔드 (FastAPI) - PYTHONPATH 필수
$env:PYTHONPATH = "C:\Projects\vibe-coding\ideator-books"
cd backend; python -m uvicorn main:app --reload --port 8000

# 프론트엔드 (Next.js)
cd frontend; npm run dev
```

### 1.6 출력 제한

```powershell
# head/tail 대체
git diff file.py | Select-Object -First 50
git log | Select-Object -Last 20

# 필터링
git status | Select-String "modified"
git status | Select-String -NotMatch "node_modules"
```

### 1.7 인코딩 규칙

**PowerShell은 이모지 미지원 → 텍스트 사용**

```python
# ❌ 이모지 사용 금지
print("✓ Test passed")
print("✅ Success")

# ✅ 텍스트 사용
print("[OK] Test passed")
print("[PASS] Success")
print("[FAIL] Failed")
```

---

## 2. 터미널 문제 해결

### 2.1 프로세스 강제 종료

```powershell
# Ctrl+C로 종료 시도 후

# 프로세스 종료
taskkill /F /IM node.exe
taskkill /F /IM python.exe

# 또는
Stop-Process -Name "node" -Force
Stop-Process -Name "python" -Force
```

### 2.2 포트 점유 확인 및 종료

```powershell
# 포트 확인
netstat -ano | findstr :3000
netstat -ano | findstr :8000

# PID로 종료
taskkill /F /PID [PID번호]
```

### 2.3 프로세스 모니터링

```powershell
# 프로세스 확인
Get-Process | Where-Object {$_.ProcessName -eq "node"}
Get-Process | Where-Object {$_.ProcessName -eq "python"}
```

---

## 3. 환경변수 파일 관리

### 3.1 핵심 문제

**.env 파일이 숨김 속성 → AI 도구가 인식 못함**

### 3.2 파일 확인 표준 (우선순위 순)

```powershell
# 1. PowerShell -Force 옵션 (최우선)
Get-ChildItem -Name "*.env*" -Force

# 2. 파일 내용 확인
Get-Content .env
Get-Content .env.example
Get-Content frontend\.env.local

# 3. 파일 존재 확인
Test-Path .env
Test-Path frontend\.env.local
```

```powershell
# ❌ 작동 안 함 (숨김 파일 미포함)
dir *.env*
ls .env*

# ❌ AI 도구 사용 불가 (숨김 파일 인식 한계)
glob_file_search(".env*")
read_file(".env")
```

### 3.3 파일 위치

```
ideator-books/
├── .env                # 백엔드 (프로젝트 루트)
├── .env.example        # 예시
└── frontend/
    └── .env.local      # 프론트엔드
```

### 3.4 환경변수 검증

**PowerShell**
```powershell
echo $env:OPENAI_API_KEY
echo $env:PYTHONPATH
Get-ChildItem Env:
```

**Python**
```python
import os
from dotenv import load_dotenv

load_dotenv()
print(f"OPENAI_API_KEY: {os.getenv('OPENAI_API_KEY')}")
```

### 3.5 Next.js 환경변수 규칙

```bash
# 클라이언트 사이드 (NEXT_PUBLIC_ 접두사 필수)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://xxx.supabase.co

# 서버 사이드 (접두사 없음)
OPENAI_API_KEY=sk-xxx
```

---

## 체크리스트

### 서버 실행 전
- [ ] `Get-Content .env` 로 파일 확인
- [ ] `echo $env:OPENAI_API_KEY` 로 환경변수 확인
- [ ] `$env:PYTHONPATH` 설정
- [ ] `netstat -ano | findstr :8000` 포트 충돌 확인

### 코드 작성 시
- [ ] 이모지 사용 금지 → `[OK]`, `[PASS]`, `[FAIL]` 사용
- [ ] 명령어 연결은 세미콜론(`;`) 사용
- [ ] 환경변수는 PowerShell 명령어로 확인
