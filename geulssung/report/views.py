# report/views.py

from collections import Counter
from django.shortcuts import render
from post.models import Post
import re

# 감성 키워드 예시
SENTIMENT_KEYWORDS = [
    '행복', '사랑', '기쁨', '슬픔', '외로움', '그리움', '설렘', '분노', '불안', '감사', '희망', '우울', '두려움'
]

def report_view(request):
    user = request.user
    if not user.is_authenticated:
        return render(request, "report/unauthorized.html")

    user_posts = Post.objects.filter(author=user)

    if not user_posts.exists():
        return render(request, "report/no_data.html")

    # 시간대별 카운트
    hour_counts = Counter([post.created_at.hour for post in user_posts])
    hour_labels = list(range(24))
    hour_values = [hour_counts.get(h, 0) for h in hour_labels]

    # 4구간 분류
    time_groups = {
        "새벽": sum(hour_counts.get(h, 0) for h in range(0, 6)),
        "아침": sum(hour_counts.get(h, 0) for h in range(6, 12)),
        "낮":   sum(hour_counts.get(h, 0) for h in range(12, 18)),
        "밤":   sum(hour_counts.get(h, 0) for h in range(18, 24)),
    }

    peak_time_group = max(time_groups, key=lambda k: time_groups[k]) if sum(time_groups.values()) > 0 else None

    # 월별 분석
    month_counts = Counter([post.created_at.strftime('%Y-%m') for post in user_posts])
    month_labels = sorted(month_counts.keys())
    month_values = [month_counts[m] for m in month_labels]

    # 감정 키워드 & 단어 빈도 분석
    all_text = " ".join([post.final_content for post in user_posts if post.final_content])

    sentiment_counts = Counter()
    for keyword in SENTIMENT_KEYWORDS:
        sentiment_counts[keyword] = all_text.count(keyword)
    top_sentiments = [word for word, count in sentiment_counts.most_common(5) if count > 0]

    words = re.findall(r'\b[가-힣]{2,}\b', all_text)
    word_counts = Counter(words)
    top_words = [word for word, count in word_counts.most_common(10)]

    context = {
        "hour_labels": hour_labels,
        "hour_values": hour_values,
        "month_labels": month_labels,
        "month_values": month_values,
        "peak_time_group": peak_time_group,
        "time_groups": time_groups,
        "top_sentiments": top_sentiments,
        "top_words": top_words,
    }

    return render(request, "report/report.html", context)
