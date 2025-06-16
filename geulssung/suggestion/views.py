from django.shortcuts import render, redirect
from .models import Suggestion
from django.contrib.auth.decorators import login_required

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

