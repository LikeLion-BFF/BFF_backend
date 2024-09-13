from django.urls import path
from contentAPI.views import *

urlpatterns = [
    path('recommend/',RecommendMissions.as_view(), name='recommend_missions'),
]