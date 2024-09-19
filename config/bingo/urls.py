from django.urls import path
from .views import CreateBingoView, BingoJoinView, JoinTeamView, BingoBoardView, TeamDetailView, CreatorView, MyBingoBoardView, EndTimeView, DeleteBingoView,UpdateProgressView

urlpatterns = [
    path('create/', CreateBingoView.as_view(), name='create_bingo'),
    path('join/', BingoJoinView.as_view(), name='join_bingo'),
    path('join/team/', JoinTeamView.as_view(), name='join_team'),
    path('bingoboard/detail/', BingoBoardView.as_view(), name='bingoboard_detail'),
    path('team/detail/', TeamDetailView.as_view(), name='team_detail'),
    path('creator/detail/', CreatorView.as_view(), name='creator_detail'),
    path('list/', MyBingoBoardView.as_view(), name='my_bingo_list'),  
    path('end_date/', EndTimeView.as_view(), name='bingo_end_time'),
    path('delete/', DeleteBingoView.as_view(), name='delete_bingo'),
    path('complete/cell/', UpdateProgressView.as_view(), name='perform_bingo'),
]