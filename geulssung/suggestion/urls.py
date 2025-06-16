from django.urls import path
from .views import suggestion_board_view

urlpatterns = [
    path('', suggestion_board_view, name='suggestion_board'),
]
