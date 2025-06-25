import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPTS = {
    "generator": "넌 글쓰기 글감을 제시하는 AI야. 주제에 맞는 글감을 짧게 제시해줘. 인사도 하지말고 딱 글감만 공백 제외 30byte 내외로 제시해줘. 시, 에세이는 배경이랑 관계 없어도 돼.",
    #"companion": "넌 섬세하고 감성적인 글쓰기 친구야. 사용자에게 감정을 묻고, 이슈에 대한 자기 생각이나 경험을 자연스럽게 나누며 대화해."
}

def ask_gemini(messages, role="generator"):
    system_prompt = SYSTEM_PROMPTS.get(role, "")
    prompt = f"{system_prompt}\n\n" + "\n".join([msg["content"] for msg in messages])
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text.strip()
