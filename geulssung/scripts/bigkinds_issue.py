import time
import random
import json
import os
from datetime import date
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# === 셀레니움 브라우저 설정 ===
options = Options()
options.add_argument("--headless")  # 브라우저 창 띄우지 않음
options.add_argument("user-agent=Mozilla/5.0")
driver = webdriver.Chrome(options=options)  # ✅ webdriver-manager 없이

# === 사이트 접속 ===
driver.get("https://www.bigkinds.or.kr/")
time.sleep(random.uniform(2.5, 4.0))  # 페이지 로딩 대기

# === 이슈 데이터 수집 ===
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
            if topic:  # 혹시 비어있는 a태그 방지
                issue_data.append({
                    "category": category,
                    "topic": topic.strip()
                })
            time.sleep(random.uniform(0.4, 0.9))

        time.sleep(random.uniform(1.5, 2.5))  # 다음 카테고리 전 딜레이

    except Exception as e:
        print(f"❌ {category} 카테고리 에러: {e}")

driver.quit()

# === 저장
today = date.today().strftime("%Y-%m-%d")
BASE_DIR = Path(__file__).resolve().parent.parent  # geulssung/
output_dir = BASE_DIR / "scripts" / "data"
output_dir.mkdir(exist_ok=True)
filename = output_dir / f"issue_{today}.json"

with open(filename, "w", encoding="utf-8") as f:
    json.dump(issue_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 크롤링 및 저장 완료: {filename.resolve()}")
