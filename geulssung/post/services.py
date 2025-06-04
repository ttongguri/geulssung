import os
import re
from django.shortcuts import get_object_or_404
from .models import Post, PostEvaluation
import google.generativeai as genai
from dotenv import load_dotenv

# ── .env에서 GEMINI_API_KEY 불러오기 ──
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# ── 글 유형별 평가 기준 (개정판) ──
BASE_CRITERIA = {
    "시": [
        "1. 심상과 상징성: 인상적인 이미지나 상징이 독창적으로 드러나는가",
        "2. 감정 전달력: 시적 표현을 통해 감정이 자연스럽게 전달되는가",
        "3. 언어의 절제와 응축: 짧은 문장 속에 의미가 밀도 있게 담겼는가",
        "4. 운율과 구조적 완성도: 행갈이, 반복, 리듬 등의 사용이 자연스럽고 조화를 이루는가",
        "5. 시적 자유와 완성도: 전통적 형식에 얽매이지 않되, 시로서의 긴장감과 응집력을 갖췄는가"
    ],
    "에세이": [
        "1. 주제 명확성: 독자가 글의 주제를 쉽게 파악할 수 있는가",
        "2. 개인적 진정성: 글쓴이만의 경험/감정이 진정성 있게 녹아 있는가",
        "3. 논리적 흐름: 단락 간 연결이 자연스럽고 설득력이 있는가",
        "4. 문장력과 표현: 문장이 매끄럽고 읽는 재미가 있는가",
        "5. 글감 반영도: 글감이나 질문을 중심으로 충실히 전개되었는가"
    ],
    "칼럼": [
        "1. 주장의 명확성: 글의 핵심 주장(논지)이 선명하고 일관성 있는가",
        "2. 근거와 설득력: 주장에 대한 논리적·사례적 뒷받침이 충분한가",
        "3. 문제의식과 시의성: 시의적절하고 의미 있는 주제를 다루었는가",
        "4. 대중성과 전달력: 누구나 읽기 쉽게 구성되어 있는가",
        "5. 글감 반영도: 주제에서 벗어나지 않고 충실히 응답했는가"
    ],
    "분석글": [
        "1. 자료 활용력: 수치/사례/인용 등이 글 전체를 뒷받침하는가",
        "2. 문제 분석의 깊이: 단순 요약을 넘어서, 통찰력 있는 해석이 있는가",
        "3. 구조적 일관성: 문제제기–분석–결론의 흐름이 논리적인가",
        "4. 객관성과 균형감: 편향되지 않고 다양한 시각을 고려했는가",
        "5. 글감 반영도: 주제에 대해 정확하고 적절한 방식으로 접근했는가"
    ]
}

def evaluate_post_with_gemini(post_id: int) -> dict:
    post = get_object_or_404(Post, id=post_id)
    text = post.final_content
    writing_type = getattr(post, "writing_type", None)
    prompt_text = (  
        getattr(post.prompt, "content", None)
        or getattr(post, "custom_prompt", None)
        or "(글감 없음)"
        )

    # ── 1) 평가 기준 구성 ──
    base = BASE_CRITERIA.get(writing_type, [
        "1. 문법 및 맞춤법 준수 여부",
        "2. 가독성: 문장이 자연스럽게 읽히는지",
        "3. 표현력: 단어 선택과 문장 구성의 적절성",
        "4. 논리 전개: 글의 흐름이 일관되는지",
        "5. 주제 전달력: 독자가 중심 내용을 쉽게 파악할 수 있는지"
    ])
    criteria_text = "\n".join(base)

    # ── 2) 프롬프트 생성 ──
    prompt = f"""
아래는 한국어 {writing_type or '일반'} 글입니다.  
작성자는 다음 글감을 참고하여 글을 작성했습니다:

[제시된 글감]  
{prompt_text or "(글감 없음)"}

<평가 기준>  
{criteria_text}

유의사항:  
- 이 기준은 '시'를 제외한 모든 글에 적용됩니다.  
- 시는 길이가 짧더라도 심상, 감정, 언어의 밀도를 중심으로 평가해 주세요.  
- 그 외 글의 경우, 단락 없이 짧거나 평가 기준을 충족하지 못하면 평가 불가로 간주해 주세요. (점수: 0)  
- 단순히 항목이 존재한다고 점수를 주지 말고, **질적으로 완성도가 높은지를 기준**으로 판단해 주세요.

<항목별 점수 부여 기준 (0~20점 × 5항목 = 총점 100점)>  
- 0점: 평가 불가 (지나치게 짧거나 무의미한 글)  
- 10점: 매우 미흡 (기준 충족 거의 없음)  
- 12~13점: 개선 필요 (다수 문제 존재)  
- 14~17점: 보통 또는 양호 (기본은 충족)  
- 18~20점: 우수~매우 우수 (개선점 없음 또는 미미)

<출력 형식 — 반드시 아래 구조를 따르세요>  
- 항목별 점수는 보여주지 마세요.  
- 총점(예: 점수: 72)만 출력하고, 장점과 개선점은 각각 2줄 이내로 작성하세요.

점수: 72

장점:  
- 주제를 명확히 드러내며, 글감과의 연결이 비교적 잘 이루어졌습니다.  
- 글의 흐름이 일정하고, 구조적으로 기본을 갖추고 있습니다.

개선점:  
- 문장이 단조롭고 진정성이 부족하여 공감이 어렵습니다.  
- 일부 표현이 어색하거나 논리적 연결이 약해 설득력이 떨어집니다.

아래 글을 위 기준에 따라 평가해 주세요:
{text}
""".strip()

    # ── 3) Gemini 모델 호출 ──
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content([prompt])
    raw = response.text.strip()

    # ── 4) 결과 파싱 ──
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

    # ── 5) DB 저장 ──
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
