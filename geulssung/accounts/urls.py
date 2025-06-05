from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('follow/', views.follow, name='follow'),
    path('set_nickname/', views.set_nickname, name='set_nickname'),
    path('login/redirect/', views.login_redirect_view, name='login_redirect'),
]
