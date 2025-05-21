from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model, login, authenticate
from django.contrib.auth.hashers import make_password

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
            return redirect('home')  # 로그인 후 홈으로 이동
        else:
            return render(request, 'accounts/login.html', {'error': '아이디 또는 비밀번호가 올바르지 않습니다.'})

    return render(request, 'accounts/login.html')

from django.contrib.auth import logout

#로그아웃 기능
def logout_view(request):
    logout(request)
    return redirect('login')  # 로그아웃 후 로그인 페이지로 이동
