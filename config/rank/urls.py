from django.urls import path
from rank.views import *

urlpatterns = [
    path('getOurRank/',BingoProgressView.as_view(), name='getTotalRank'),
    path('getTotalRank/',BingoProgressTotalView.as_view(), name='getTotalRank'),
]