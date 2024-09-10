
import os
import google.generativeai as genai

# 제미나이 API 키 설정
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# 생성 설정: 다양성을 높이기 위해 temperature 값을 높게 설정
generation_config = {
    "temperature": 0.8,  # 높일수록 더 창의적이고 다양하게 추천
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 1000,
    "response_mime_type": "text/plain",
}

# 제미나이 모델 호출
model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

def recommend_missions():
    # 미션 추천 요청
    response = model.generate_content(
        prompt="동아리나 모임에서 팀원끼리 친해질 수 있는 5가지 미션을 추천해줘. 간단한 형식으로 부탁해.",
    )
    
    # 응답 출력 (텍스트 필드만 출력)
    return response.text

# 사용자가 '추천'을 누를 때마다 다른 답변을 받기 위한 호출
def get_new_recommendation():
    print("새로운 미션 추천:")
    print(recommend_missions())

# 테스트 실행
get_new_recommendation()

# 사용자가 다시 추천을 누를 때마다 동일한 방식으로 다른 세션을 시작
get_new_recommendation()

