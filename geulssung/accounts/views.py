from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Follow
from django.http import JsonResponse
from .models import CustomUser
from django.contrib.auth import logout


User = get_user_model()

#회원가입 기능
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        nickname = request.POST['nickname']
        email = request.POST['email']

        # 유효성 검사
        if User.objects.filter(username=username).exists():
            return render(request, 'accounts/signup.html', {'error': '중복된 아이디입니다.'})
        if User.objects.filter(nickname=nickname).exists():
            return render(request, 'accounts/signup.html', {'error': '중복된 닉네임입니다.'})
        if User.objects.filter(email=email).exists():
            return render(request, 'accounts/signup.html', {'error': '중복된 이메일입니다.'})

        user = User.objects.create(
            username=username,
            nickname=nickname,
            email=email,
            password=make_password(password),
        )
        login(request, user)
        return redirect('login')

    return render(request, 'accounts/signup.html')

#로그인 기능
def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')  # 이미 로그인 상태면 홈으로 보내기
        
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if not user.nickname:
                return redirect('set_nickname')
            return redirect('home')  # 로그인 후 홈으로 이동
        else:
            return render(request, 'accounts/login.html', {'error': '아이디 또는 비밀번호가 올바르지 않습니다.'})

    return render(request, 'accounts/login.html')

#로그아웃 기능
def logout_view(request):
    logout(request)
    return redirect('login')  # 로그아웃 후 로그인 페이지로 이동

#팔로우 기능
@require_POST
@login_required
def follow(request):
    target_id = request.POST.get('user_id')
    target_user = User.objects.get(id=target_id)

    if request.user == target_user:
        return JsonResponse({'error': '자기 자신은 팔로우할 수 없습니다.'}, status=400)

    follow, created = Follow.objects.get_or_create(
        follower=request.user, following=target_user
    )

    if not created:
        follow.delete()
        return JsonResponse({'status': 'unfollowed'})
    return JsonResponse({'status': 'followed'})

#닉네임 설정 기능
@login_required
def set_nickname(request):
    if request.user.nickname and request.user.nickname.strip():
        return redirect('home')  # 이미 있으면 홈으로

    if request.method == 'POST':
        nickname = request.POST.get('nickname')
        if CustomUser.objects.filter(nickname=nickname).exists():
            return render(request, 'accounts/set_nickname.html', {'error': '이미 사용 중인 닉네임입니다.'})
        request.user.nickname = nickname
        request.user.save()
        return redirect('home')  # 닉네임 설정 완료 후 홈으로 이동

    return render(request, 'accounts/set_nickname.html')


#로그인 후 닉네임 설정 여부 확인
def login_redirect_view(request):
    if not request.user.nickname:
        return redirect('set_nickname')
    return redirect('home')