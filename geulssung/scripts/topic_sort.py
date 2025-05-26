import json
from pathlib import Path
from datetime import date
from collections import defaultdict

# === 오늘 날짜 가져오기
today = date.today().strftime("%Y-%m-%d")

# === 파일 경로 자동 설정
BASE_DIR = Path(__file__).resolve().parent.parent  # geulssung/
data_dir = BASE_DIR / "scripts" / "data"
input_filename = f"issue_{today}.json"
output_filename = f"grouped_issues_{today}.json"
input_path = data_dir / input_filename
output_path = data_dir / output_filename

# === JSON 불러오기
if not input_path.exists():
    print(f"❌ 입력 파일 없음: {input_path.resolve()}")
    exit()

with open(input_path, "r", encoding="utf-8") as f:
    issues = json.load(f)

# === 카테고리별 토픽 묶기
grouped = defaultdict(list)
for item in issues:
    category = item.get("category")
    topic = item.get("topic")
    if category and topic:
        grouped[category].append(topic)

# === 저장
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(grouped, f, ensure_ascii=False, indent=2)

print(f"✅ 카테고리별 토픽 그룹 저장 완료: {output_path.resolve()}")
