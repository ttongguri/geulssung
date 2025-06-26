import os
import re
import json
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count
from post.models import Post, PostEvaluation
from report.models import SentimentAnalysis, UserLevel
import google.generativeai as genai
from collections import Counter, defaultdict

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

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
        # 한국 시간으로 변환
        hour = post.created_at.astimezone(timezone.get_current_timezone()).hour
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
    # 사용자 정보 가져오기
    nickname = user.nickname
    date_joined = user.date_joined.astimezone(timezone.get_current_timezone()).strftime("%Y-%m-%d")
    
    # 발행글 수 계산 (is_public=True인 글만)
    published_posts_count = Post.objects.filter(author=user, is_public=True).count()
    
    # 사용자 등급 계산 (UserLevel 모델 사용)
    user_grade = UserLevel.get_user_grade(published_posts_count)
    profile_image_url = UserLevel.get_user_image_path(published_posts_count)
    
    # 점수추이 데이터 가져오기 (최근 10개)
    score_data = PostEvaluation.objects.filter(
        post__author=user
    ).select_related('post').order_by('-post__created_at')[:30]  # 넉넉히 30개까지 조회

    # 날짜별 최고점수만 남기기
    date_to_score = defaultdict(int)
    score_list = []  # 모든 점수 저장용
    for evaluation in score_data:
        date_str = evaluation.post.created_at.strftime("%m/%d")
        if evaluation.score > date_to_score[date_str]:
            date_to_score[date_str] = evaluation.score
        score_list.append(evaluation.score)
    # 날짜순 정렬 (최신순 10개만)
    sorted_items = sorted(date_to_score.items(), key=lambda x: x[0])[-10:]
    score_labels = [item[0] for item in sorted_items]
    score_values = [item[1] for item in sorted_items]

    # 평균/최고점수 계산
    avg_score = int(sum(score_list) / len(score_list)) if score_list else 0
    max_score = max(score_list) if score_list else 0

    # 시간대 분석 추가
    peak_time_group = get_peak_time_group(user_posts)
    f_time_group = get_peak_time_group([p for p in user_posts if p.category == 'emotion'])
    t_time_group = get_peak_time_group([p for p in user_posts if p.category == 'logic'])

    # 사용자 글 요약 분석
    latest_summary = SentimentAnalysis.objects.filter(user=user).order_by("-analyzed_at").first()
    if latest_summary:
        gemini_result = latest_summary.result_text
    else:
        full_text = "\n\n".join([p.final_content for p in user_posts if p.final_content])
        prompt = f"""
        한 사용자가 작성한 글들의 모음을 제시해드리겠습니다.
        이 글들을 분석하여 다음 항목에 따라 리포트를 작성해주세요. 숫자나 기호 없이 자연스러운 문장 형식으로 답변하고, 각 분석내용 요약해서 소제목처럼 달아주세요. md 문법은 사용하지 마세요.
        항상 이모지를 포함하여 예시와 같은 형식으로 답변해주세요.

        예시:
        💬 글의 전반적 톤: 진지하고 객관적

        사용자의 글은 전체적으로 진지하고, 객관적인 톤을 유지하고 있습니다. 각 사회 문제에 대한 심각성을 강조하며, 해결을 위한 낙관적인 태도를 보이지만, 동시에 문제의 복잡성을 인지하고 있다는 점을 드러냅니다. 비판적인 시각도 포함되어 있으나, 공격적이거나 감정적인 표현은 자제하고 있습니다.


        🏃 글의 전개 방식: 문제 제기 - 원인 분석 - 해결책 제시 - 결론의 논리적인 흐름

        모든 글은 유사한 구조로 작성되었습니다. 먼저 사회적 문제에 대한 문제의식을 제기하고, 그 문제가 단순히 개인의 문제가 아닌 사회 구조적인 원인을 가지고 있다는 점을 강조합니다. 다음으로 문제의 다양한 배경을 언급하며, 전문가들의 의견을 통해 구조적 원인을 지적하고 실질적인 해결책 모색의 필요성을 주장합니다. 마지막으로 해당 문제가 사회적 과제이며, 모두의 관심과 참여가 필요하다는 결론을 내립니다. 즉, 문제 제기 - 원인 분석 - 해결책 제시 - 결론의 논리적인 흐름을 따르는 전개 방식을 일관되게 사용하고 있습니다.


        ⭐ 작성자의 글쓰기 특징: 논리적, 체계적, 효율적 글쓰기

        사용자는 사회 문제에 대한 높은 관심과 문제 해결 의지를 가지고 있습니다. 글쓰기는 논리적이고 체계적이며, 객관적인 사실 전달에 중점을 두고 있습니다. 비슷한 구조와 어휘를 반복적으로 사용하는 것은 효율성을 중시하는 글쓰기 방식이라고 볼 수 있습니다. 다소 단조로운 면이 있지만, 주제를 명확하게 전달하는 데 효과적입니다. 사회 문제의 구조적 원인을 강조하는 점은 분석적이고 비판적인 시각을 가지고 있음을 나타냅니다.
        
        📌 자주 사용하는 표현:

        "문제의식은 점점 더 커지고 있다", "사회 구조적 원인을 내포하고 있다", "실질적인 대안을 모색할 필요가 있다", "정책적 지원과 제도 개선이 병행되어야 한다", "더 이상 미룰 수 없는 사회적 과제다", "모두가 관심을 가지고 참여할 때, 비로소 실질적인 변화가 가능할 것이다" 와 같은 표현들이 반복적으로 사용됩니다. 이는 사용자가 사회 문제에 대한 해결책을 제시하는 데 초점을 맞추고 있으며, 구체적인 해결 방안으로 정책적 지원과 제도 개선을 중요하게 생각하고 있음을 보여줍니다.


        ❤️ 인상 깊은 문장:

        "이 문제는 더 이상 미룰 수 없는 사회적 과제다"는 문장은 문제의 시급성을 강조하며 독자의 주의를 환기시키는 효과적인 문장입니다. "모두가 관심을 가지고 참여할 때, 비로소 실질적인 변화가 가능할 것이다"는 문장은 사회적 문제 해결을 위한 공동의 노력을 강조하며 희망적인 메시지를 전달합니다. 이 두 문장은 간결하면서도 강한 메시지를 담고 있어 인상적입니다.


        ✔️ 한 줄 평:

        이 사용자의 글쓰기는 "사회의 아픔을 꿰뚫는 날카로운 분석과 변화를 향한 굳건한 의지" 와 같습니다.

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
        # sentiment_scores.append(analyze_post_sentiment(post))

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
        "user_grade": user_grade,
        "profile_image_url": profile_image_url,
        "gemini_result": gemini_result,
        "sentiment_labels": sentiment_labels,
        "sentiment_scores": sentiment_scores,
        "peak_time_group": peak_time_group,
        "f_time_group": f_time_group,
        "t_time_group": t_time_group,
        "peak_time_group": peak_time_group,
        "avg_char_count": avg_char_count,
        "max_char_count": max_char_count,
        "score_labels": json.dumps(score_labels),
        "score_values": json.dumps(score_values),
        "avg_score": avg_score,
        "max_score": max_score,
    }

    return render(request, "report/report.html", context)
