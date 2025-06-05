from django.urls import path
from .views import user_owned_items_view, customize_avatar_view

urlpatterns = [
    path('my-items/', user_owned_items_view, name='user_owned_items'),
    path('customize-avatar/', customize_avatar_view, name='item_customization'),
]