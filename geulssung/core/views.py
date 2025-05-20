from django.shortcuts import render

# /test로 연결 되는 테스트 페이지 입니다.
def test_page_view(request):
    return render(request, "test.html")

# /geulssung으로 연결 되는 메인 페이지 입니다.
def home_view(request):
    return render(request, "base.html")

# /write로 연결 되는 글쓰기 페이지 입니다.
def write_post_view(request):
    return render(request, 'post/write_form.html')



