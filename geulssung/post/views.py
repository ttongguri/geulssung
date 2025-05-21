from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post
from django.http import HttpResponseForbidden

@login_required
def write_post_view(request):
    if request.method == 'POST':
        post = Post(
            author=request.user,
            title=request.POST['title'],
            category=request.POST['category'],  # 사용자 선택값 그대로 저장
            genre=request.POST['genre'],
            step1=request.POST.get('step1', ''),
            step2=request.POST.get('step2', ''),
            step3=request.POST.get('step3', ''),
            final_content=request.POST.get('final_text', ''),
            is_public='is_public' in request.POST  # 체크박스 처리
        )
        post.save()
        return redirect('post_detail', post_id=post.id)
    
    return render(request, 'post/write_form.html')

def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post/post_detail.html', {'post': post})

