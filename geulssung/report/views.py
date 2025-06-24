import os
import re
from django.shortcuts import render
from post.models import Post
from report.models import SentimentAnalysis, PostSentiment
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

def analyze_post_sentiment(post):
    if hasattr(post, 'postsentiment'):
        return post.postsentiment.score

    prompt = f"""
    아래 글의 감성 점수를 -10에서 +10 사이의 정수로 평가해줘.
    점수가 높을수록 긍정적, 낮을수록 부정적이야.
    반드시 score라는 단어와 숫자를 포함해서 알려줘.

    글:
    \"\"\"{post.final_content}\"\"\"
    """

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        # "score: -5" 형태로부터 숫자만 추출
        match = re.search(r"[Ss]core['\"]?\s*[:=]\s*(-?\d+)", text)
        score = int(match.group(1)) if match else 0

        PostSentiment.objects.create(
            post=post,
            score=score,
            result_text=text
        )
        return score

    except Exception as e:
        print(f"[ERROR] 감성 분석 실패: {e}")
        return 0

def report_view(request):
    user = request.user
    if not user.is_authenticated:
        return render(request, "report/unauthorized.html")

    user_posts = Post.objects.filter(author=user).order_by("created_at")
    if not user_posts.exists():
        return render(request, "report/no_data.html")

    # 감성 요약 분석
    latest_summary = SentimentAnalysis.objects.filter(user=user).order_by("-analyzed_at").first()
    if latest_summary:
        gemini_result = latest_summary.result_text
    else:
        full_text = "\n\n".join([p.final_content for p in user_posts if p.final_content])
        prompt = f"""
        아래는 사용자가 작성한 글 모음이야.

        전체 감성을 아래 항목에 따라 요약해줘:
        1. 감성 분류: 긍정 / 중립 / 부정
        2. 감성 키워드 3~5개
        3. 인용할 만한 문장
        4. 전체 감성 흐름을 문단으로 요약

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
        sentiment_scores.append(analyze_post_sentiment(post))

    context = {
        "gemini_result": gemini_result,
        "sentiment_labels": sentiment_labels,
        "sentiment_scores": sentiment_scores,
    }

    return render(request, "report/report.html", context)
