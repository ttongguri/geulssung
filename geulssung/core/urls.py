from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),  # /geulssung/
    path("test/", views.test_page_view, name="test"),  # /test/
]
