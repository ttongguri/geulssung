from django.urls import path
from .views import suggestion_board_view, delete_suggestion_view, vote_suggestion_view

urlpatterns = [
    path('', suggestion_board_view, name='suggestion_board'),
    path('delete/<int:suggestion_id>/', delete_suggestion_view, name='delete_suggestion'),
    path('vote/<int:suggestion_id>/', vote_suggestion_view, name='vote_suggestion'),

]
