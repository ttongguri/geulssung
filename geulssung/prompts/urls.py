from django.urls import path
from . import views

urlpatterns = [
    path('api/random-prompts/', views.random_prompts, name='random_prompts'),
] 