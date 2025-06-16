from django.urls import path
<<<<<<< HEAD
from .views import suggestion_board_view

urlpatterns = [
    path('', suggestion_board_view, name='suggestion_board'),
=======
from .views import suggestion_board_view, delete_suggestion_view, vote_suggestion_view

urlpatterns = [
    path('', suggestion_board_view, name='suggestion_board'),
    path('delete/<int:suggestion_id>/', delete_suggestion_view, name='delete_suggestion'),
    path('vote/<int:suggestion_id>/', vote_suggestion_view, name='vote_suggestion'),

>>>>>>> 5a73aed7ff6a5d0aa3907574986505c02b7c2e24
]
