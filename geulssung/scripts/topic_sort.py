import time
import random
import json
import os
from datetime import date
from pathlib import Path
from collections import defaultdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# === 브라우저 설정 ===
options = Options()
options.add_argument("--headless")
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Chrome(options=options)

# === 사이트 접속 ===
driver.get("https://www.bigkinds.or.kr/")
time.sleep(random.uniform(2.5, 4.0))

# === 이슈 수집 ===
issue_data = []

category_buttons = driver.find_elements(By.CSS_SELECTOR, "a.button.issue-category")
for btn in category_buttons:
    try:
        category = btn.get_attribute("data-category")
        print(f"📍 카테고리: {category}")

        driver.execute_script("arguments[0].click();", btn)
        time.sleep(random.uniform(2.0, 3.0))

        items = driver.find_elements(By.CSS_SELECTOR, "a.txt_title02.issue-item-link")
        print(f"  - 이슈 {len(items)}개 감지됨")

        for item in items:
            topic = item.get_attribute("data-topic")
            if topic:
                issue_data.append({
                    "category": category,
                    "topic": topic.strip()
                })
            time.sleep(random.uniform(0.4, 0.9))

        time.sleep(random.uniform(1.5, 2.5))

    except Exception as e:
        print(f"❌ {category} 카테고리 에러: {e}")

driver.quit()

# === 카테고리별 그룹화 ===
grouped = defaultdict(list)
for item in issue_data:
    category = item.get("category")
    topic = item.get("topic")
    if category and topic:
        grouped[category].append(topic)

# === 저장
today = date.today().strftime("%Y-%m-%d")
BASE_DIR = Path(__file__).resolve().parent.parent
output_dir = BASE_DIR / "scripts" / "data"
output_dir.mkdir(exist_ok=True)
output_path = output_dir / f"grouped_issues_{today}.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(grouped, f, ensure_ascii=False, indent=2)

print(f"\n✅ 그룹화된 이슈 저장 완료: {output_path.resolve()}")