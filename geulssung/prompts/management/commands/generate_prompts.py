import os
import json
import time
from pathlib import Path
from datetime import date
from django.core.management.base import BaseCommand
from prompts.models import Issue, GeneratedPrompt
from services.gemini_engine import ask_gemini  # ✅ Gemini용 엔진

class Command(BaseCommand):
    help = "Gemini 기반 글감 생성 후 DB 저장 (429 대응 포함)"

    def handle(self, *args, **kwargs):
        today = date.today().strftime("%Y-%m-%d")
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
        json_path = BASE_DIR / "scripts" / "data" / f"grouped_issues_{today}.json"

        if not json_path.exists():
            self.stderr.write(self.style.ERROR(f"❌ 파일 없음: {json_path}"))
            return

        with open(json_path, "r", encoding="utf-8") as f:
            grouped_issues = json.load(f)

        for category, topics in grouped_issues.items():
            if category == "전체":
                continue

            for topic in topics:
                issue_obj, _ = Issue.objects.get_or_create(category=category, title=topic)

                for style in ["칼럼", "분석글", "에세이", "시"]:
                    if GeneratedPrompt.objects.filter(issue=issue_obj, style=style).exists():
                        continue

                    prompt_msg = self.build_prompt(category, topic, style)
                    content = self.safe_ask_gemini(prompt_msg, role="generator")

                    if content:
                        GeneratedPrompt.objects.create(
                            issue=issue_obj,
                            style=style,
                            content=content,
                        )
                        self.stdout.write(self.style.SUCCESS(f"✅ {category} | {topic} | {style} 저장됨"))

                    time.sleep(5)  # ✅ 429 방지: 호출 간 딜레이

    def build_prompt(self, category, topic, style):
        base = f"'{topic}'이라는 키워드에서 연상되는 단어, 이미지, 느낌을 자유롭게 확장해서 "
        if style == "칼럼":
            return [{"role": "user", "content": f"{base}사회적 시각으로 접근할 수 있는 짧고 독특한 글감 하나를 제시해줘. 꼭 주제를 그대로 해석할 필요는 없어. 제목처럼 써줘."}]
        elif style == "분석글":
            return [{"role": "user", "content": f"{base}원인이나 배경을 분석적으로 탐색할 수 있는, 직관적이고 날카로운 글감 하나를 만들어줘. 짧은 문장으로."}]
        elif style == "에세이":
            return [{"role": "user", "content": f"{base}개인의 경험, 감정, 추억과 연결할 수 있는 짧고 섬세한 글감을 만들어줘. 한가지 소재만 제목처럼 간결하게."}]
        elif style == "시":
            return [{"role": "user", "content": f"{base}시적인 이미지나 은유로 풀 수 있는 짧은 글감 하나를 제시해줘. 한가지 소재만 간결하고, 함축적이고, 추상적으로."}]


    def safe_ask_gemini(self, messages, role="generator", retries=3):
        for attempt in range(retries):
            try:
                return ask_gemini(messages, role)
            except Exception as e:
                if "429" in str(e):
                    self.stdout.write(self.style.WARNING(f"⏳ 429 오류, {attempt+1}번째 대기 후 재시도 중..."))
                    time.sleep(15)
                else:
                    self.stderr.write(self.style.ERROR(f"❌ 예외 발생: {e}"))
                    return None
        self.stderr.write(self.style.ERROR("❌ 재시도 실패: 최대 시도 횟수 초과"))
        return None