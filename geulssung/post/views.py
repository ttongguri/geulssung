from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post
from django.http import HttpResponseForbidden


# /test로 연결 되는 테스트 페이지 입니다.
def test_page_view(request):
    return render(request, "test.html")

# /geulssung으로 연결 되는 메인 페이지 입니다.
def home_view(request):
    return render(request, "base.html")

# /geulssung/write로 연결 되는 글쓰기 페이지 입니다.
@login_required
def write_post_view(request):
    if request.method == 'POST':
        post = Post(
            author=request.user,
            title=request.POST['title'],
            category=request.POST['category'],
            genre=request.POST['genre'],
            step1=request.POST.get('step1', ''),
            step2=request.POST.get('step2', ''),
            step3=request.POST.get('step3', ''),
            final_content=request.POST.get('final_text', ''),
            is_public='is_public' in request.POST
        )
        post.save()
        return redirect('post_detail', post_id=post.id)
    return render(request, 'post/write_form.html')

def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post/post_detail.html', {'post': post})

