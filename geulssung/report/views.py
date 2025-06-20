# report/views.py

from collections import Counter
from django.shortcuts import render
from post.models import Post

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

    context = {
        "hour_labels": hour_labels,
        "hour_values": hour_values,
        "month_labels": month_labels,
        "month_values": month_values,
        "peak_time_group": peak_time_group,
        "time_groups": time_groups,
    }

    return render(request, "report/report.html", context)
