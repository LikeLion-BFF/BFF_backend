from django.shortcuts import redirect 
import urllib 
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter

# code 요청
def kakao_login(request):
    app_rest_api_key = "0cb9512f98ed066d53f1ebb06723aeef"
    redirect_uri = "http://127.0.0.1:8000/accounts/kakao/login/callback/"

    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    )
    
# # 카카오에서 전달받은 인증 코드를 포함한 URL로 리다이렉트
# def kakao_callback(request):                                                                  
#     params = urllib.parse.urlencode(request.GET)                                      
#     return redirect(f'http://127.0.0.1:8000/account/login/kakao/callback?{params}')   

# 카카오 로그인 뷰
class KakaoLogin(SocialLoginView):
    adapter_class = KakaoOAuth2Adapter
    callback_url = 'http://127.0.0.1:8000/accounts/kakao/login/callback/'

