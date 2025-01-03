from openai import OpenAI
import os

# API Key 삭제

def generate_dalle_prompt(user_prompt):
    # GPT 모델을 사용하여 DALL-E용 프롬프트로 변환하는 로직
    return f"DALL-E prompt generated from: {user_prompt}"

def create_dalle_image(prompt):
    # DALL-E API 호출하여 이미지를 생성하고 Base64로 인코딩된 이미지 데이터를 반환
    response = openai.images.generate(model="dall-e-3", prompt=prompt, n=1, size="1024x1024",response_format='b64_json')
    image_data = response.data[0].b64_json  # base64 인코딩된 이미지 데이터
    
    return image_data

# 카테고리를 통한 DALL-E 모델 이미지 생성 로직 추가 필요, 호출은 마찬가지로 create_dalle_image를 이용해서 이미지 생성
def generate_dalle_category(category, topic):
    
    # 카테고리별 프롬프트의 기본 문구 설정
    category_prompts = {
        "logo": "a professional logo design of",
        "photo": "a high-resolution photograph of",
        "illustration": "an artistic illustration of"
    }

    # 선택한 카테고리의 프롬프트 문구 가져오기
    prompt_base = category_prompts.get(category, "an image of")

    # 프롬프트 문장 생성
    prompt = f"{prompt_base} {topic}"
    return prompt
