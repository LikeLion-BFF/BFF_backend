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
from .views import KakaoLogin ,kakao_login
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('accounts/', include('allauth.urls')),
    path('auth/', include('dj_rest_auth.urls')),
    # path('auth/', include('dj_rest_auth.urls')), 
    path('auth/registration/', include('dj_rest_auth.registration.urls')), 
    path('', include('django.contrib.auth.urls')),

    #소셜로그인(카카오)
    path('accounts/login/kakao/', kakao_login, name='kakao_login'),
    path('accounts/login/kakao/callback/', KakaoLogin.as_view(), name='kakao_callback'),

    #토큰
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
