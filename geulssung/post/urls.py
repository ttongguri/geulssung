from django.urls import path
from . import views

urlpatterns = [
    path('<int:post_id>/', views.post_detail, name='post_detail'),
    path('/', views.my_posts_view, name='my_posts'),
    path('geulssunglog/<str:nickname>/', views.public_posts_by_user, name='public_user_posts'),
]
