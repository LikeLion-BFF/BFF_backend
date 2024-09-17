from django.urls import path
from .views import TokenRefreshView, verify, user_detail

urlpatterns = [
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('verify/', verify),
    path('detail/', user_detail),
]