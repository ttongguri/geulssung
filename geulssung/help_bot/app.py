from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv

# .env 파일 불러오기 (있다면)
load_dotenv()

# 🔐 Gemini API 키 설정
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "여기에_직접_API_키_입력해도_가능"))

# ✅ 정확한 템플릿 경로 지정 (write_form.html이 들어 있는 폴더)
app = Flask(__name__)

# 시스템 프롬프트 맵
genre_prompts = {
    "poem": "당신은 시를 잘 쓰도록 도와주는 시 전문 작문 도우미입니다.",
    "essay": "당신은 감성적이고 따뜻한 에세이를 도와주는 작문 도우미입니다.",
    "column": "당신은 논리적이고 시사적인 칼럼을 잘 쓰도록 돕는 전문가입니다.",
    "analysis": "당신은 데이터와 통계 기반의 분석글을 쓰도록 도와주는 분석 전문가입니다.",
    "default": "당신은 사용자 글쓰기를 돕는 친절한 도우미입니다."
}

@app.route("/")
def index():
    return render_template("write_form.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "")
    genre = data.get("genre", "default")
    system_prompt = genre_prompts.get(genre, genre_prompts["default"])
    response_text = generate_gemini_reply(system_prompt, user_input)
    return jsonify({"reply": response_text})

def generate_gemini_reply(system_prompt, user_input):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        chat = model.start_chat(history=[
            {"role": "user", "parts": [system_prompt]}
        ])
        response = chat.send_message(user_input)
        return response.text
    except Exception as e:
        return f"오류 발생: {e}"

if __name__ == "__main__":
    app.run(debug=True)