from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import os
import google.generativeai as genai
import re
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


class RecommendMissions(APIView):
    @permission_classes([IsAuthenticated])
    def post(self, request):
        # 제미나이 API 설정
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

        # 모델 설정
        generation_config = {
        "temperature": 0.8,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
        # safety_settings = Adjust safety settings
        # See https://ai.google.dev/gemini-api/docs/safety-settings
        )
        chat_session = model.start_chat(
            history=[
                {
                "role": "user",
                "parts": [
                    "우리는 미션빙고라는 서비스를 개발하고 있어. \n동아리나 모임에서 아이스브레이킹과 친목도모를 위해 주어진 미션빙고를 채우며 친해지는 것을 목적으로 해. \n여기서 너는 처음 만난 사람들이 친해지기 위해 수행하면 좋은 미션들을 추천해주는 역할을 해야해. \n미션을 추천해달라는 명령어를 받으면 1. 팀원끼리 셀카찍기 2. 같이 저녁 식사 후 인증하기 3. 팀원들끼리 별명지어주기 4. 같이 영화보러가기 5. 같이 한강가서 피크닉하기 이렇게 미션 5가지만 추천해주면 돼.다른 부가 설명은 필요 없어 이 형식을 꼭 지켜줘  \n미션을 추천해줘",
                ],
                },
                {
                "role": "model",
                "parts": [
                    "1. 팀원끼리 셀카찍기:  함께 찍은 사진은 추억을 공유하고 나중에 다시 꺼내볼 때 즐거운 기억을 되새기게 해줄 거예요! 📸\n2. 같이 저녁 식사 후 인증하기:  맛있는 음식을 함께 먹으며 자연스럽게 이야기꽃을 피워보세요!  식사 인증샷은 덤! \n3. 팀원들끼리 별명 지어주기:  재미있는 별명은 팀워크를 더욱 돈독하게 만들어 줄 거예요!  서로에게 웃음을 선물해보세요! \n4. 같이 영화보러가기:  함께 영화를 보며 공통의 관심사를 찾고 이야기할 거리가 생길 거예요!  \n5. 같이 한강가서 피크닉하기:  따스한 햇살 아래 돗자리를 펴고 도시락을 먹으며 즐거운 시간을 보내세요!  한강에서 펼쳐지는 낭만적인 추억!",
                ],
                },
                {
                "role": "user",
                "parts": [
                    "새로운 미션을 추천해줘",
                ],
                },
                {
                "role": "model",
                "parts": [
                    "1. 팀원 모두의 MBTI 유형 공유하기:  서로의 성격 유형을 알아보며 팀원들에 대한 이해도를 높여보세요! \n2. 팀원 중 한 명의 꿈 이야기 들어주기:  서로의 꿈을 나누며 격려하고 응원하는 시간을 가져보세요. \n3. 팀원들과 함께 좋아하는 노래 부르기:  함께 노래를 부르며 흥겨운 시간을 보내고 팀워크를 향상시켜보세요! \n4. 팀원 중 한 명에게 칭찬 릴레이 하기:  서로의 장점을 칭찬하며 긍정적인 분위기를 조성하고 팀워크를 강화해보세요! \n5. 팀원들과 함께 웃긴 영상 보며 웃기:  함께 웃으며 스트레스를 해소하고 친목을 다지는 시간을 가져보세요!",
                ],
                },
            ]
        )

        # 새로운 미션 요청
        response = chat_session.send_message("새로운 미션을 추천해줘")

        print(response.text)

        # 숫자(1, 2, ...)를 기준으로 텍스트를 분리하여 미션 리스트 추출
        missions = re.split(r'\d+\.\s', response.text)[1:]

        # 출력 결과 확인
        # print(missions)

        return Response({"missions": missions}, status=status.HTTP_200_OK)
