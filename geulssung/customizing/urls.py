from django.urls import path
from .views import user_owned_items_view, store_view

urlpatterns = [
    path('my-items/', user_owned_items_view, name='user_owned_items'),
    path('store/', store_view, name='store'),
]