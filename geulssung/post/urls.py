from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.my_posts_view, name='my_posts'),  # ✅ 루트 경로
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('geulssunglog/<str:nickname>/', views.public_posts_by_user, name='public_user_posts'),
    path('geulssung/', views.write_view, name='write'),
    path('geulssung/chat', views.chat_view, name='chat'),
]

# ✅ 디버그 모드에서만 미디어 파일 서빙 허용
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
