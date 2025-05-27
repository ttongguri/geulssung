from django.urls import path
from . import views

urlpatterns = [
    path('<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('toggle_visibility/<int:post_id>/', views.toggle_post_visibility, name='toggle_post_visibility'),
    path('geulssunglog/<str:nickname>/', views.public_posts_by_user, name='public_user_posts'),
    path('update-cover-image/<int:post_id>/', views.update_cover_image, name='update_cover_image'),
    path('delete/<int:post_id>/', views.delete_post_view, name='delete_post'),
]

# 미디어 파일 접근 경로 추가(디버그 모드에서만 작동)
#if settings.DEBUG:
#    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)