import os
import re
from django.shortcuts import render
from post.models import Post
from report.models import SentimentAnalysis, PostSentiment
import google.generativeai as genai
from collections import Counter

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# 감성 점수 분석 코드
# def analyze_post_sentiment(post):
#     if hasattr(post, 'postsentiment'):
#         return post.postsentiment.score

#     prompt = f"""
#     아래 글의 감성 점수를 -10에서 +10 사이의 정수로 평가해줘.
#     점수가 높을수록 긍정적, 낮을수록 부정적이야.
#     반드시 score라는 단어와 숫자를 포함해서 알려줘.

#     글:
#     \"\"\"{post.final_content}\"\"\"
#     """

#     try:
#         response = model.generate_content(prompt)
#         text = response.text.strip()

#         # "score: -5" 형태로부터 숫자만 추출
#         match = re.search(r"[Ss]core['\"]?\s*[:=]\s*(-?\d+)", text)
#         score = int(match.group(1)) if match else 0

#         PostSentiment.objects.create(
#             post=post,
#             score=score,
#             result_text=text
#         )
#         return score

#     except Exception as e:
#         print(f"[ERROR] 감성 분석 실패: {e}")
#         return 0

# 시간대 분석 코드
def get_peak_time_group(posts):
    # 시간대 그룹: 새벽(0~5), 아침(6~11), 오후(12~17), 저녁(18~23)
    time_groups = {
        "새벽": range(0, 6),
        "아침": range(6, 12),
        "오후": range(12, 18),
        "저녁": range(18, 24),
    }
    group_counts = Counter()
    for post in posts:
        hour = post.created_at.hour
        for group, hours in time_groups.items():
            if hour in hours:
                group_counts[group] += 1
                break
    if group_counts:
        return group_counts.most_common(1)[0][0]
    return None

# 글 분석 코드
def report_view(request):
    user = request.user
    if not user.is_authenticated:
        return render(request, "report/unauthorized.html")

    user_posts = Post.objects.filter(author=user).order_by("created_at")
    if not user_posts.exists():
        return render(request, "report/no_data.html")

    # 시간대 분석 추가
    peak_time_group = get_peak_time_group(user_posts)
    f_time_group = get_peak_time_group([p for p in user_posts if p.category == 'emotion'])
    t_time_group = get_peak_time_group([p for p in user_posts if p.category == 'logic'])

    # 글 요약 분석
    latest_summary = SentimentAnalysis.objects.filter(user=user).order_by("-analyzed_at").first()
    if latest_summary:
        gemini_result = latest_summary.result_text
    else:
        full_text = "\n\n".join([p.final_content for p in user_posts if p.final_content])
        prompt = f"""
        한 사용자가 작성한 글들의 모음을 제시해드리겠습니다.
        이 글들을 분석하여 다음 항목에 따라 리포트를 작성해주세요. 숫자나 기호 없이 자연스러운 문장 형식으로 답변하고, 각 내용을 요약해서 소제목처럼 달아주세요. md 문법은 사용하지 마세요.
        항상 예시와 같은 형식으로 답변해주세요.

        예시:
        항목: 항목 별 리포트 내용 한 줄 요약
        구체적인 리포트 내용

        다음으로 6개 항목을 제시해드리겠습니다.

        글의 전반적 톤:
        사용자의 글이 대체로 어떤 분위기와 정서를 담고 있는지 서술해주세요. 예: 차분한 톤, 격정적인 어조, 냉소적인 무드 등

        글의 전개 방식:
        글들이 어떤 구조나 흐름으로 전개되는지, 글의 흐름에 어떤 패턴이 있는지 설명해주세요.
        
        자주 사용하는 표현:
        글을 쓸 때 자주 등장하는 단어나 어휘, 표현 방식, 문장 습관 등을 분석해주세요. 이 표현을 왜 자주 쓰는지 짐작해도 좋습니다.

        작성자의 글쓰기 특징:
        글에서 드러나는 글쓰기 습관, 태도, 주제의식 등을 종합적으로 분석해주세요.

        인상 깊은 문장:
        사용자의 글 중 인상 깊은 문장 두세 개를 인용하고, 그 이유도 함께 설명해주세요.

        한 줄 평:
        이 사용자의 글쓰기를 비유적 표현이나 속담, 사자성어 등을 활용해 한 문장으로 정리해주세요.

        분석에 활용할 글 모음은 아래에 있습니다:

        \"\"\"{full_text}\"\"\"
        """

        try:
            response = model.generate_content(prompt)
            gemini_result = response.text.strip()
            SentimentAnalysis.objects.create(user=user, result_text=gemini_result)
        except Exception as e:
            gemini_result = f"[분석 실패] {str(e)}"

    sentiment_labels = []
    sentiment_scores = []

    for post in user_posts:
        if not post.final_content:
            continue
        sentiment_labels.append(post.created_at.strftime("%Y-%m-%d"))

    context = {
        "gemini_result": gemini_result,
        "sentiment_labels": sentiment_labels,
        "sentiment_scores": sentiment_scores,
        "peak_time_group": peak_time_group,
        "f_time_group": f_time_group,  # F글 시간대
        "t_time_group": t_time_group,  # T글 시간대
    }

    return render(request, "report/report.html", context)
