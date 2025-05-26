import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPEN_API_KEY")

# 기본 system 프롬프트 정의
SYSTEM_PROMPTS = {
    "generator": "넌 사회 이슈를 바탕으로 글쓰기 아이디어를 생성하는 AI야. 형식(칼럼, 분석글, 에세이, 시)에 맞춰 구체적 글감을 생성하고 배경도 짧게 덧붙여.",
    "companion": "넌 섬세하고 인간적인 글쓰기 친구야. 사용자에게 감정을 묻거나 자기 이야기를 이끌어내듯 대화해.",
}

def ask_chatgpt(messages, model="gpt-4o", role="generator", temperature=0.8):
    system_prompt = SYSTEM_PROMPTS.get(role, "")
    full_messages = [{"role": "system", "content": system_prompt}] + messages

    response = openai.ChatCompletion.create(
        model=model,
        messages=full_messages,
        temperature=temperature
    )
    return response.choices[0].message.content.strip()
