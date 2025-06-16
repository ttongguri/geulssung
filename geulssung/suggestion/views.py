from django.shortcuts import render, redirect, get_object_or_404
from .models import Suggestion
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST

# 건의 게시판 페이지
@login_required
def suggestion_board_view(request):
    if request.method == 'POST':
        content = request.POST['content']
        if content.strip():
            Suggestion.objects.create(user=request.user, content=content)
        return redirect('suggestion_board')

    suggestions = Suggestion.objects.order_by('-created_at')
    return render(request, 'suggestion/board.html', {'suggestions': suggestions})

# 건의 삭제 기능
@login_required
def delete_suggestion_view(request, suggestion_id):
    if not request.user.is_staff:
        return HttpResponseForbidden("관리자만 삭제할 수 있습니다.")

    suggestion = get_object_or_404(Suggestion, id=suggestion_id)
    suggestion.delete()
    return redirect('suggestion_board')

# 건의 추천 기능
@require_POST
@login_required
def vote_suggestion_view(request, suggestion_id):
    suggestion = get_object_or_404(Suggestion, id=suggestion_id)
    user = request.user
    action = request.POST.get('action')

    if action == 'upvote':
        if user in suggestion.upvoted_users.all():
            suggestion.upvoted_users.remove(user)
        else:
            suggestion.upvoted_users.add(user)
            suggestion.downvoted_users.remove(user)
    elif action == 'downvote':
        if user in suggestion.downvoted_users.all():
            suggestion.downvoted_users.remove(user)
        else:
            suggestion.downvoted_users.add(user)
            suggestion.upvoted_users.remove(user)

    return JsonResponse({
        'upvotes': suggestion.upvoted_users.count(),
        'downvotes': suggestion.downvoted_users.count(),
        'user_action': action
    })