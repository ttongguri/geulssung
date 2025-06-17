"""
URL configuration for 글썽글썽 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from post import views
from django.conf import settings
from django.conf.urls.static import static
from post.views import chat_view
from django.views.generic import RedirectView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', RedirectView.as_view(url='/geulssung/', permanent=False)),
    path("geulssung/", views.home_view, name="home"),
    # path("geulssung/test/", views.test_page_view, name="test"),
    path("geulssung/write/", views.write_post_view, name="write"),
    path("geulssung/explore/", views.explore_view, name="explore"),
    path("geulssung/accounts/", include("accounts.urls")),      # 사용자 계정 관련 URL
    path("geulssung/accounts/auth/", include("allauth.urls")),  # allauth 소셜 로그인 URL
    path("geulssung/post/", include("post.urls")),
    path("prompts/", include("prompts.urls")),
    path("geulssung/chat", chat_view, name="chat"),
    path("like/<int:post_id>/", views.like, name="like"),
    path('my-items/', include('customizing.urls')),  # 너가 만든 앱의 URL 연결
    path('geulssung/customizing/', include('customizing.urls')),
    path('geulssung/suggestion/', include('suggestion.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)