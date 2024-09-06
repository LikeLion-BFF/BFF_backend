from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
import requests
from django.conf import settings
# from dj_rest_auth.registration.views import SocialLoginView
# from allauth.socialaccount.providers.kakao.views import KakaoOAuth2Adapter
from allauth.socialaccount.models import SocialAccount, SocialToken, SocialLogin
from allauth.socialaccount.helpers import complete_social_login
from django.contrib.auth import get_user_model
from allauth.socialaccount.providers.kakao.provider import KakaoProvider
from allauth.account.adapter import get_adapter
from allauth.socialaccount import app_settings
from django.views.decorators.csrf import csrf_exempt

# code 요청
def kakao_login(request):
    app_rest_api_key = "0cb9512f98ed066d53f1ebb06723aeef"
    redirect_uri = "http://127.0.0.1:8000/accounts/kakao/login/callback/"

    return redirect(
        f"https://kauth.kakao.com/oauth/authorize?client_id={app_rest_api_key}&redirect_uri={redirect_uri}&response_type=code"
    )

@csrf_exempt
def kakao_callback(request):
    code = request.GET.get('code')
    app_rest_api_key = "0cb9512f98ed066d53f1ebb06723aeef"
    redirect_uri = "http://127.0.0.1:8000/accounts/kakao/login/callback/"

    # 카카오 API에 액세스 토큰 요청
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': app_rest_api_key,
        'redirect_uri': redirect_uri,
        'code': code,
    }

    token_headers = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    }

    response = requests.post(token_url, data=token_data, headers=token_headers)
    token_response = response.json()

    access_token = token_response.get('access_token')

    if not access_token:
        return JsonResponse({'status': 'fail', 'message': 'Access token not found'}, status=400)

    # 사용자 정보 요청
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    user_info_headers = {
        'Authorization': f'Bearer {access_token}',
    }

    user_info_response = requests.get(user_info_url, headers=user_info_headers)
    user_info = user_info_response.json()

    if not user_info.get('id'):
        return JsonResponse({'status': 'fail', 'message': 'Failed to retrieve user info'}, status=400)

    # 사용자 정보에서 필요한 데이터 추출
    kakao_id = user_info.get('id')
    properties = user_info.get('properties', {})
    user_name = properties.get('nickname', 'Unknown User')

    # User 모델 생성 또는 조회
    User = get_user_model()
    user, created = User.objects.get_or_create(username=str(kakao_id))
    if created:
        user.first_name = user_name
        user.save()

    # SocialAccount 및 SocialToken 저장
    try:
        social_account, _ = SocialAccount.objects.get_or_create(user=user, provider=KakaoProvider.id, uid=str(kakao_id))
        
        # SocialToken 저장
        SocialToken.objects.update_or_create(
            account=social_account,
            defaults={'token': access_token}
        )

        # 로그인 완료
        sociallogin = SocialLogin()
        sociallogin.state = SocialLogin.state_from_request(request)
        sociallogin.account = social_account
        sociallogin.token = SocialToken(account=social_account, token=access_token)
        sociallogin.user = user

        get_adapter(request).complete_login(request, sociallogin, app_settings.LOGIN_ON_GET)
        complete_social_login(request, sociallogin)
        
    except Exception as e:
        return JsonResponse({'status': 'fail', 'message': str(e)}, status=500)

    return JsonResponse({
        'status': 'success',
        'kakao_id': kakao_id,
        'nickname': user_name,
    })


