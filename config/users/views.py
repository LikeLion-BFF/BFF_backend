import os
import requests
import jwt

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from django.shortcuts import redirect

from users.models import User
from users.serializers import KakaoLoginRequestSerializer, KakaoRegisterRequestSerializer, TempUserResponseSerializer

class KakaoAccessTokenException(Exception):
    pass

class KakaoOIDCException(Exception):
    pass

class KakaoDataException(Exception):
    pass

class GoogleAccessTokenException(Exception):
    pass

class GoogleOIDCException(Exception):
    pass

class GoogleDataException(Exception):
    pass

def exchange_kakao_access_token(access_code):
    response = requests.post(
        'https://kauth.kakao.com/oauth/token',
        headers={
            'Content-type': 'application/x-www-form-urlencoded;charset=utf-8',
        },
        data={
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('KAKAO_REST_API_KEY'),
            'redirect_uri': os.environ.get('KAKAO_REDIRECT_URI'),
            'code': access_code,
        },
    )
    if response.status_code >= 300:
        raise KakaoAccessTokenException()
    return response.json()

def extract_kakao_nickname(kakao_data):
    id_token = kakao_data.get('id_token', None)
    if id_token is None:
        raise KakaoDataException()
    
    jwks_client = jwt.PyJWKClient(os.environ.get('KAKAO_OIDC_URI'))
    signing_key = jwks_client.get_signing_key_from_jwt(id_token)
    signing_algol = jwt.get_unverified_header(id_token)['alg']
    try:
        payload = jwt.decode(
            id_token,
            key=signing_key.key,
            algorithms=[signing_algol],
            audience=os.environ.get('KAKAO_REST_API_KEY'),
        )
    except jwt.InvalidTokenError:
        raise KakaoOIDCException()
    return payload['nickname']

def exchange_google_access_token(access_code):
    response = requests.post(
        'https://oauth2.googleapis.com/token',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
            'client_secret': os.environ.get('GOOGLE_CLIENT_SECRET'),
            'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI'),
            'code': access_code,
        },
    )
    if response.status_code >= 300:
        raise GoogleAccessTokenException(f"Failed to exchange token. Status: {response.status_code}, Response: {response.text}")
    return response.json()

def extract_google_user_info(google_data):
    id_token = google_data.get('id_token', None)
    if id_token is None:
        raise GoogleDataException("No id_token in Google data")
    
    try:
        # JWT 라이브러리를 사용하여 토큰 디코딩
        decoded_token = jwt.decode(id_token, options={"verify_signature": False})
        return decoded_token
    except jwt.DecodeError as e:
        raise GoogleOIDCException(f"Failed to decode token: {str(e)}")

def exchange_naver_access_token(access_code):
    response = requests.post(
        'https://nid.naver.com/oauth2.0/token',
        headers={
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        data={
            'grant_type': 'authorization_code',
            'client_id': os.environ.get('NAVER_CLIENT_ID'),
            'client_secret': os.environ.get('NAVER_CLIENT_SECRET'),
            'redirect_uri': os.environ.get('NAVER_REDIRECT_URI'),
            'code': access_code,
            'state': 'random_state_string',  # CSRF 방지를 위한 문자열
        },
    )

    print(response.status_code)
    print(response.json())

    if response.status_code >= 300:
        raise Exception(f"Failed to exchange token with Naver. Status: {response.status_code}, Response: {response.text}")
    
    return response.json()

def extract_naver_user_info(naver_data):
    access_token = naver_data.get('access_token', None)
    if access_token is None:
        raise Exception('No access token in Naver data')

    response = requests.get(
        'https://openapi.naver.com/v1/nid/me',
        headers={
            'Authorization': f'Bearer {access_token}',
        }
    )

    if response.status_code >= 300:
        raise Exception(f"Failed to fetch user info from Naver. Status: {response.status_code}, Response: {response.text}")

    user_data = response.json()
    if user_data['resultcode'] != '00':
        raise Exception(f"Failed to verify Naver user info. Response: {user_data}")
    
    return user_data['response']

@api_view(['POST'])
@permission_classes([AllowAny])
def kakao_login(request):
    serializer = KakaoLoginRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        kakao_data = exchange_kakao_access_token(data['access_code'])
        nickname = extract_kakao_nickname(kakao_data)
    except KakaoAccessTokenException:
        return Response({'detail': 'Access token 교환에 실패했습니다.'}, status=401)
    except KakaoDataException:
        return Response({'detail': 'OIDC token 정보를 확인할 수 없습니다.'}, status=401)
    except KakaoOIDCException:
        return Response({'detail': 'OIDC 인증에 실패했습니다.'}, status=401)

    try:
        user = User.objects.get(nickname=nickname)
    except User.DoesNotExist:
        return Response({'detail': '존재하지 않는 사용자입니다.'}, status=404)

    refresh = RefreshToken.for_user(user)
    return Response({
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    })

@api_view(['POST'])
@permission_classes([AllowAny])
def kakao_register(request):
    serializer = KakaoRegisterRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    try:
        kakao_data = exchange_kakao_access_token(data['access_code'])
        nickname = extract_kakao_nickname(kakao_data)
    except KakaoAccessTokenException:
        return Response({'detail': 'Access token 교환에 실패했습니다.'}, status=401)
    except KakaoDataException:
        return Response({'detail': 'OIDC token 정보를 확인할 수 없습니다.'}, status=401)
    except KakaoOIDCException:
        return Response({'detail': 'OIDC 인증에 실패했습니다.'}, status=401)

    ok = False
    try:
        user = User.objects.get(nickname=nickname)
    except User.DoesNotExist:
        ok = True

    if not ok:
        return Response({'detail': '이미 등록 된 사용자를 중복 등록할 수 없습니다.'}, status=400)

    user = User.objects.create_user(nickname=nickname, description=data['description'])
    refresh = RefreshToken.for_user(user)
    return Response({
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh)
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def google_login(request):
    print("Client ID:", os.environ.get('GOOGLE_CLIENT_ID'))
    print("Redirect URI:", os.environ.get('GOOGLE_REDIRECT_URI'))
    params = {
        'client_id': os.environ.get('GOOGLE_CLIENT_ID'),
        'redirect_uri': os.environ.get('GOOGLE_REDIRECT_URI'),
        'response_type': 'code',
        'scope': 'openid email profile',
    }
    base_url = 'https://accounts.google.com/o/oauth2/v2/auth'
    auth_url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    return redirect(auth_url)

@api_view(['GET'])
@permission_classes([AllowAny])
def google_callback(request):
    print("Client ID:", os.environ.get('GOOGLE_CLIENT_ID'))
    print("Client Secret:", os.environ.get('GOOGLE_CLIENT_SECRET'))
    print("Redirect URI:", os.environ.get('GOOGLE_REDIRECT_URI'))
    print("OIDC URI:", os.environ.get('GOOGLE_OIDC_URI'))

    code = request.GET.get('code')
    if not code:
        return Response({'detail': 'Google 인증에 실패했습니다.'}, status=400)

    try:
        google_data = exchange_google_access_token(code)
        user_info = extract_google_user_info(google_data)
        email = user_info.get('email')
        name = user_info.get('name', '')
    except GoogleAccessTokenException as e:
        print(f"GoogleAccessTokenException: {str(e)}")
        return Response({'detail': 'Access token 교환에 실패했습니다.'}, status=401)
    except GoogleDataException as e:
        print(f"GoogleDataException: {str(e)}")
        return Response({'detail': 'OIDC token 정보를 확인할 수 없습니다.'}, status=401)
    except GoogleOIDCException as e:
        print(f"GoogleOIDCException: {str(e)}")
        return Response({'detail': 'OIDC 인증에 실패했습니다.'}, status=401)

    user, created = User.objects.get_or_create(
        email=email,
        defaults={'nickname': name, 'description': f'Google: {name}'}
    )

    refresh = RefreshToken.for_user(user)
    response_data = {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'user_created': created
    }

    frontend_redirect_url = os.environ.get('FRONTEND_REDIRECT_URL', '')
    if frontend_redirect_url:
        redirect_url = f"{frontend_redirect_url}?{'&'.join(f'{k}={v}' for k, v in response_data.items())}"
        return redirect(redirect_url)
    else:
        return Response(response_data)

@api_view(['GET'])
@permission_classes([AllowAny])
def naver_login(request):
    params = {
        'client_id': os.environ.get('NAVER_CLIENT_ID'),
        'redirect_uri': os.environ.get('NAVER_REDIRECT_URI'),
        'response_type': 'code',
        'state': 'random_state_string',  
    }
    base_url = 'https://nid.naver.com/oauth2.0/authorize'
    auth_url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
    return redirect(auth_url)


@api_view(['GET'])
@permission_classes([AllowAny])
def naver_callback(request):
    code = request.GET.get('code')
    state = request.GET.get('state')
    
    if not code or not state:
        return Response({'detail': 'Naver 인증에 실패했습니다.'}, status=400)

    try:
        naver_data = exchange_naver_access_token(code)
        user_info = extract_naver_user_info(naver_data)
    except Exception as e:
        return Response({'detail': str(e)}, status=401)

    # 이메일을 기반으로 사용자 조회 혹은 생성
    user, created = User.objects.get_or_create(
        email=user_info['email'],
        defaults={'nickname': user_info['name'], 'description': f'Naver: {user_info["name"]}'}
    )

    # JWT 토큰 발급
    refresh = RefreshToken.for_user(user)
    response_data = {
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
        'user_created': created
    }

    frontend_redirect_url = os.environ.get('FRONTEND_REDIRECT_URL', '')
    if frontend_redirect_url:
        redirect_url = f"{frontend_redirect_url}?{'&'.join(f'{k}={v}' for k, v in response_data.items())}"
        return redirect(redirect_url)
    else:
        return Response(response_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify(request):
    return Response({'detail': 'Token is verified.'}, status=200)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_detail(request):
    serializer = TempUserResponseSerializer(request.user)
    return Response(serializer.data)
