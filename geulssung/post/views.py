import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from django.http import HttpResponseForbidden, HttpResponseNotAllowed, JsonResponse
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as gemini
from dotenv import load_dotenv
from .models import Post, PostImage
from django.urls import reverse
from prompts.models import GeneratedPrompt

load_dotenv()
gemini.configure(api_key=os.getenv("GEMINI_API_KEY"))

User = get_user_model()

# chatbot
genre_prompts = {
    "poem": "당신은 시를 잘 쓰도록 도와주는 시 전문 작문 도우미입니다.",
    "essay": "당신은 감성적이고 따뜻한 에세이를 도와주는 작문 도우미입니다.",
    "column": "당신은 논리적이고 시사적인 칼럼을 잘 쓰도록 돕는 전문가입니다.",
    "analysis": "당신은 데이터와 통계 기반의 분석글을 쓰도록 도와주는 분석 전문가입니다.",
    "default": "당신은 사용자 글쓰기를 돕는 친절한 도우미입니다."
}

def write_view(request):
    return render(request, "write_form.html")

@csrf_exempt
def chat_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_input = data.get("message", "")
        genre = data.get("genre", "default")
        system_prompt = genre_prompts.get(genre, genre_prompts["default"])
        reply = generate_gemini_reply(system_prompt, user_input)
        return JsonResponse({"reply": reply})
    return JsonResponse({"error": "Invalid method"}, status=405)

def generate_gemini_reply(system_prompt, user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat(history=[{"role": "user", "parts": [system_prompt]}])
        response = chat.send_message(user_input)
        return response.text
    except Exception as e:
        return f"오류 발생: {e}"

# /test로 연결 되는 테스트 페이지 입니다.
def test_page_view(request):
    return render(request, "test.html")

# /geulssung으로 연결 되는 메인 페이지 입니다.
def home_view(request):
    return render(request, "hj_main_test.html")

# /geulssung/write로 연결 되는 글쓰기 페이지 입니다.
@login_required
def write_post_view(request):
    if request.method == 'POST':
        genre = request.POST['genre']
        if genre == 'column':
            step1 = request.POST.get('column_step1', '')
            step2 = request.POST.get('column_step2', '')
            step3 = request.POST.get('column_step3', '')
        elif genre == 'analysis':
            step1 = request.POST.get('analysis_step1', '')
            step2 = request.POST.get('analysis_step2', '')
            step3 = request.POST.get('analysis_step3', '')
        elif genre == 'essay':
            step1 = request.POST.get('essay_step1', '')
            step2 = request.POST.get('essay_step2', '')
            step3 = request.POST.get('essay_step3', '')
        elif genre == 'poem':
            step1 = request.POST.get('poem_step1', '')
            step2 = request.POST.get('poem_step2', '')
            step3 = request.POST.get('poem_step3', '')
        else:
            step1 = step2 = step3 = ''
        # 필수값 누락 등으로 저장 실패 시 기존 값 유지
        if not request.POST.get('title') or not genre or not request.POST.get('category'):
            return render(request, 'post/write_form.html', {
                'selected_category': request.POST.get('category', ''),
                'selected_genre': genre,
                'topic': request.POST.get('topic', ''),
                'title': request.POST.get('title', ''),
                'final_text': request.POST.get('final_text', ''),
                'step1': step1,
                'step2': step2,
                'step3': step3,
            })
        prompt_id = request.POST.get('prompt_id')
        prompt_obj = None
        if prompt_id:
            try:
                prompt_obj = GeneratedPrompt.objects.get(id=prompt_id)
            except GeneratedPrompt.DoesNotExist:
                prompt_obj = None
        post = Post(
            author=request.user,
            title=request.POST['title'],
            category=request.POST['category'],
            genre=genre,
            step1=step1,
            step2=step2,
            step3=step3,
            final_content=request.POST.get('final_text', ''),
            is_public='is_public' in request.POST,
            prompt=prompt_obj
        )
        post.save()
        # 이미지가 첨부된 경우 PostImage 저장
        if 'cover_image' in request.FILES:
            PostImage.objects.create(post=post, image=request.FILES['cover_image'])
        return redirect('post_detail', post_id=post.id)
    return render(request, 'post/write_form.html')

# 글 상세 페이지입니다.
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post/post_detail.html', {'post': post})

# 유저 글 보기 페이지입니다.
def public_posts_by_user(request, nickname):
    author = get_object_or_404(User, nickname=nickname)
    # 로그인한 사용자가 해당 nickname의 주인일 때는 모든 글, 아니면 공개글만
    if request.user.is_authenticated and request.user.nickname == nickname:
        posts = Post.objects.filter(author=author).order_by('-created_at')
    else:
        posts = Post.objects.filter(author=author, is_public=True).order_by('-created_at')
    return render(request, 'post/public_user_posts.html', {
        'author': author,
        'posts': posts,
    })

# 커버 이미지 업데이트 기능입니다
@login_required
def update_cover_image(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return HttpResponseForbidden()
    if request.method == 'POST' and request.FILES.get('cover_image'):
        image_file = request.FILES['cover_image']
        post_image, created = PostImage.objects.get_or_create(post=post)
        post_image.image = image_file
        post_image.save()
        return redirect('public_user_posts', nickname=post.author.nickname)
    return HttpResponseNotAllowed(['POST'])

def explore_view(request):
    return render(request, 'post/explore.html')  # templates/explore.html 위치에 파일이 있어야 함
# 글 삭제 기능입니다
@login_required
def delete_post_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return HttpResponseForbidden()
    if request.method == 'POST':
        post.delete()
        return redirect('public_user_posts', nickname=post.author.nickname)
    return render(request, 'post/confirm_delete.html', {'post': post})
