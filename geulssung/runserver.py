import subprocess
import sys

print("▶️ 1단계: topic_sort.py 실행 시작...")
subprocess.run([sys.executable, "scripts/topic_sort.py"], check=True)  # venv python 사용 보장
print("✅ 1단계: topic_sort.py 실행 완료!\n")

# 2분 예상 소요 → 원하면 아래처럼 기다리는 것도 가능 (안 써도 됨)
# print("⏳ 2분 정도 대기 중...")
# time.sleep(120)  # 120초 대기 → 원하면 생략 가능

# 2️⃣ generate_prompts.py 실행
print("▶️ 2단계: generate_prompts.py 실행 시작...")
subprocess.run([sys.executable, "manage.py", "generate_prompts"], check=True)
print("✅ 2단계: generate_prompts.py 실행 완료!\n")

print("🎉 모든 작업 완료!")