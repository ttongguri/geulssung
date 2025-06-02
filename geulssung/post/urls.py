from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('toggle_visibility/<int:post_id>/', views.toggle_post_visibility, name='toggle_post_visibility'),
    path('geulssunglog/<str:nickname>/', views.public_posts_by_user, name='public_user_posts'),
    path('update-cover-image/<int:post_id>/', views.update_cover_image, name='update_cover_image'),
    path('delete/<int:post_id>/', views.delete_post_view, name='delete_post'),
    path('geulssung/chat', views.chat_view, name='chat'),
    ]

# ✅ 디버그 모드에서만 미디어 파일 서빙 허용
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
