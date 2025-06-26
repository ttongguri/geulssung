import os
import re
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count
from post.models import Post
from report.models import SentimentAnalysis, PostSentiment
import google.generativeai as genai
from collections import Counter, defaultdict

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

def report_view(request):
    user = request.user
    if not user.is_authenticated:
        return render(request, "report/unauthorized.html")

    user_posts = Post.objects.filter(author=user).order_by("created_at")
    if not user_posts.exists():
        return render(request, "report/no_data.html")

    # 사용자 정보 가져오기
    nickname = user.nickname
    date_joined = user.date_joined.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d")
    
    # 발행글 수 계산 (is_public=True인 글만)
    published_posts_count = Post.objects.filter(author=user, is_public=True).count()

    # 시간대 분석 추가
    f_time_group = get_peak_time_group([p for p in user_posts if p.category == 'emotion'])
    t_time_group = get_peak_time_group([p for p in user_posts if p.category == 'logic'])

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

    # 시간대별 분석
    time_groups = defaultdict(int)
    f_time_groups = defaultdict(int)
    t_time_groups = defaultdict(int)
    
    for post in user_posts:
        hour = post.created_at.hour
        
        # 전체 시간대 분석
        if 6 <= hour < 12:
            time_groups["오전"] += 1
        elif 12 <= hour < 18:
            time_groups["오후"] += 1
        elif 18 <= hour < 24:
            time_groups["저녁"] += 1
        else:
            time_groups["새벽"] += 1
            
        # 감성별 시간대 분석
        if post.category == 'emotion':
            if 6 <= hour < 12:
                f_time_groups["오전"] += 1
            elif 12 <= hour < 18:
                f_time_groups["오후"] += 1
            elif 18 <= hour < 24:
                f_time_groups["저녁"] += 1
            else:
                f_time_groups["새벽"] += 1
        elif post.category == 'logic':
            if 6 <= hour < 12:
                t_time_groups["오전"] += 1
            elif 12 <= hour < 18:
                t_time_groups["오후"] += 1
            elif 18 <= hour < 24:
                t_time_groups["저녁"] += 1
            else:
                t_time_groups["새벽"] += 1
    
    # 가장 활발한 시간대 찾기
    peak_time_group = max(time_groups.items(), key=lambda x: x[1])[0] if time_groups else None
    f_time_group = max(f_time_groups.items(), key=lambda x: x[1])[0] if f_time_groups else None
    t_time_group = max(t_time_groups.items(), key=lambda x: x[1])[0] if t_time_groups else None

    # 글자수 통계 계산
    char_counts = []
    max_char_count = 0
    max_char_post = None
    
    for post in user_posts:
        if post.final_content:
            char_count = len(post.final_content)
            char_counts.append(char_count)
            if char_count > max_char_count:
                max_char_count = char_count
                max_char_post = post
    
    avg_char_count = sum(char_counts) // len(char_counts) if char_counts else 0

    context = {
        "nickname": nickname,
        "date_joined": date_joined,
        "published_posts_count": published_posts_count,
        "gemini_result": gemini_result,
        "sentiment_labels": sentiment_labels,
        "sentiment_scores": sentiment_scores,
        "f_time_group": f_time_group,
        "t_time_group": t_time_group,
        "avg_char_count": avg_char_count,
        "max_char_count": max_char_count,
    }

    return render(request, "report/report.html", context)
