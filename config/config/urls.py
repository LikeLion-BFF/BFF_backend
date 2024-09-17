"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django.http import HttpResponse

from users.views import (
    kakao_login, 
    kakao_callback,
    google_login,
    google_callback,
    naver_login,
    naver_callback,
    verify, 
    user_detail
)

def home(request):
    return HttpResponse("Main Page")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),

    # Kakao Login
    path('kakao/login/', kakao_login, name='kakao_login'),
    path('accounts/kakao/login/callback/', kakao_callback), 

    # Google Login
    path('google/login/', google_login, name='google_login'),
    path('accounts/google/login/callback/', google_callback), 

    # Naver Login
    path('naver/login/', naver_login, name='naver_login'),
    path('accounts/naver/login/callback/', naver_callback), 

    path('users/verify/', verify),
    path('users/', user_detail),

    path('contentAPI/', include('contentAPI.urls')),
    path('bingo/', include('bingo.urls')),
    path('rank/', include('rank.urls')),
]
