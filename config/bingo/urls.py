from django.urls import path
from .views import CreateBingoView, JoinTeamView, BingoBoardView, MyBingoBoardView, DeleteBingoView, TeamDetailView

urlpatterns = [
    path('create/', CreateBingoView.as_view(), name='create_bingo'),
    path('join/', JoinTeamView.as_view(), name='join_bingo'),
    path('bingoboard/detail/', BingoBoardView.as_view(), name='bingoboard_detail'),
    path('team/detail/', TeamDetailView.as_view(), name='team_detail'),
    path('list/', MyBingoBoardView.as_view(), name='my_bingo_list'),  
    path('delete/', DeleteBingoView.as_view(), name='delete_bingo')
]