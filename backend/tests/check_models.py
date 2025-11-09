"""OpenAI 사용 가능 모델 확인"""
import sys
from pathlib import Path
from dotenv import load_dotenv

# 프로젝트 루트
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# .env 로드
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from openai import OpenAI

client = OpenAI()

print("=" * 80)
print("OpenAI 사용 가능 모델 리스트")
print("=" * 80)

models = client.models.list()

# GPT 모델만 필터링
gpt_models = []
for model in models.data:
    if 'gpt' in model.id.lower():
        gpt_models.append(model.id)

# 정렬
gpt_models.sort()

print(f"\n총 {len(gpt_models)}개 GPT 모델:\n")
for i, model_id in enumerate(gpt_models, 1):
    print(f"{i:3d}. {model_id}")

# gpt-5 관련 모델 찾기
print("\n" + "=" * 80)
print("GPT-5 관련 모델:")
print("=" * 80)

gpt5_models = [m for m in gpt_models if 'gpt-5' in m.lower()]
if gpt5_models:
    for model_id in gpt5_models:
        print(f"  ✅ {model_id}")
else:
    print("  ❌ GPT-5 모델 없음")
    
# 권장 모델
print("\n" + "=" * 80)
print("권장 모델:")
print("=" * 80)
recommended = ['gpt-4o', 'gpt-4o-mini', 'gpt-3.5-turbo', 'o1-mini']
for rec in recommended:
    if rec in gpt_models:
        print(f"  ✅ {rec}")
    else:
        print(f"  ❌ {rec} (사용 불가)")

