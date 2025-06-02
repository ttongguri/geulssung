import os
import re
from django.shortcuts import get_object_or_404
from .models import Post, PostEvaluation
import google.generativeai as genai
from dotenv import load_dotenv

# ── .env 파일에서 GEMINI_API_KEY 불러오기 ──
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ── 글 유형별 평가 기준 ──
FORMAT_CRITERIA = {
    "시": (
        "1. 이미지와 은유: 시어(언어)가 얼마나 풍부한 상징/은유를 사용했는지\n"
        "2. 감정 전달력: 짧은 구절 속에서 독자에게 감정을 효과적으로 전달했는지\n"
        "3. 운율 및 구조: 리듬, 호흡, 행간 배치가 어색함 없이 자연스러운지\n"
        "4. 압축성: 최소한의 단어로 최대한의 의미를 전달했는지"
    ),
    "에세이": (
        "1. 주제 명확성: 도입부에서 글의 주제가 분명하게 제시되었는지\n"
        "2. 개인적 통찰: 저자 고유의 경험/관점이 글 전반에 녹아 있는지\n"
        "3. 논리 전개: 각 단락이 유기적으로 연결되어 일관성 있게 흐르는지\n"
        "4. 문체·어조: 읽기 편안하면서도 저자만의 목소리가 드러나는지"
    ),
    "칼럼": (
        "1. 논지의 설득력: 주장(의견)을 뒷받침할 근거나 사례가 적절한지\n"
        "2. 시의성·독창성: 사회·정치·문화 이슈를 다룰 때 새롭고 흥미로운 시각을 제시했는지\n"
        "3. 논리 구조: 서론-본론-결론이 명확하고, 반론을 예측해 반박했는지\n"
        "4. 전달력: 전문 용어·통계 등을 적절히 활용하되, 일반 독자도 이해하기 쉽게 썼는지"
    ),
    "분석글": (
        "1. 데이터 근거: 제시한 수치·차트·통계가 논지를 뒷받침하는지\n"
        "2. 구조적 일관성: 문제 제기-분석-결론의 흐름이 체계적으로 짜여 있는지\n"
        "3. 깊이 있는 인사이트: 단순 정리가 아닌, 자료에서 얻은 의미나 시사점이 잘 나타나는지\n"
        "4. 비판적 시각: 장단점을 균형 있게 짚었는지, 오류 가능성이나 한계도 언급했는지"
    ),
}


def evaluate_post_with_gemini(post_id: int) -> dict:
    """
    Gemini 1.5 Flash 모델을 활용해 글을 평가합니다.
    """
    # ── 1) Post 객체 가져오기 ──
    post = get_object_or_404(Post, pk=post_id)
    text = post.final_content
    writing_type = getattr(post, "writing_type", None)

    # ── 2) 평가 기준 선택 ──
    criteria = FORMAT_CRITERIA.get(
        writing_type,
        "1. 문법 및 맞춤법 준수 여부\n"
        "2. 가독성: 문장이 자연스럽게 읽히는지\n"
        "3. 논리 전개: 서론-본론-결론이 명확히 구분되는지\n"
        "4. 전반적 완성도: 글의 목적이 잘 달성되었는지"
    )

    # ── 3) 프롬프트 생성 ──
    prompt = f"""
아래는 한국어 {writing_type or '일반'} 글입니다.
다음 기준에 따라 평가를 진행해 주세요:

<평가 기준>
{criteria}

1) 각 평가 항목(4개)에 대해 0~25점 사이의 점수를 매긴 후, 총합을 ‘점수’로 출력해 주세요. (예: 이미지와 은유 20점, 감정 전달력 22점, 운율 및 구조 18점, 압축성 19점 → 총점: 79점)
→ 반드시 세부 항목별 점수와 총점을 함께 제시해 주세요. 예시:
- 이미지와 은유: 20
- 감정 전달력: 22
- 운율 및 구조: 18
- 압축성: 19  
점수: 79

2) 위 기준에 따라 이 글의 장점(good)을 2~3문장으로 분리해서 써 주세요.
3) 위 기준에 따라 이 글의 개선점(improve)을 2~3문장으로 분리해서 써 주세요.

출력 형식 예시(반드시 아래 형식을 따라주세요):
---
점수: 85

장점:
- 이 글은 {writing_type or '글'}의 주제가 명확하며, 독자에게 핵심 메시지를 효과적으로 전달합니다.
- 예시나 비유를 통해 내용을 쉽게 이해할 수 있도록 구성했습니다.

개선점:
- 일부 문단에서 논리적 연결이 다소 부족해 보입니다.
- 특정 근거(데이터)가 더 추가되면 설득력이 높아질 것 같습니다.
---

아래 글을 평가해 주세요:
{text}
""".strip()

    # ── 4) Gemini 모델 호출 ──
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([prompt])
    raw = response.text.strip()

    # ── 5) 결과 파싱 ──
    score = 0
    good = ""
    improve = ""

    score_match = re.search(r"점수\s*:\s*(\d{1,3})", raw)
    if score_match:
        score = int(score_match.group(1))
        score = max(0, min(score, 100))

    pro_start = raw.find("장점:")
    con_start = raw.find("개선점:")
    if pro_start != -1 and con_start != -1:
        good = raw[pro_start + len("장점:"):con_start].strip()
        improve = raw[con_start + len("개선점:"):].strip()

    # ── 6) DB 저장 ──
    evaluation, _ = PostEvaluation.objects.get_or_create(post=post)
    evaluation.score = score
    evaluation.good = good
    evaluation.improve = improve
    evaluation.save()

    return {
        "score": score,
        "good": good,
        "improve": improve,
        "raw_response": raw,
    }
