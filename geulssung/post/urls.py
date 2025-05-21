from django.urls import path
from . import views

urlpatterns = [
    path('write/', views.write_post_view, name='write_post'),
    path('<int:post_id>/', views.post_detail_view, name='post_detail'),
]