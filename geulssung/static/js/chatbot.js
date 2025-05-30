document.addEventListener("DOMContentLoaded", function () {
  // 새로고침 시 채팅 히스토리 삭제
  sessionStorage.removeItem("chatHistory");
  sessionStorage.removeItem("chat-log-html");
  localStorage.removeItem("chatHistory"); 

  // 📦 chat-box-wrapper 존재 확인
  const wrapper = document.getElementById("chat-box-wrapper");

  if (!wrapper) {
    console.error("❌ chat-box-wrapper가 HTML에 존재하지 않습니다.");
    return;
  }

  // 💬 채팅창 생성 및 삽입
  const chatBox = document.createElement("div");
  chatBox.id = "chat-box";
  chatBox.classList.add("hidden");  // 시작 시 숨김
  chatBox.innerHTML = `
    <div style="width: 100%; max-width:400px; background: white; border: 1px solid #ccc; border-radius: 0 0 10px 10px; box-shadow: 0 0 10px rgba(0,0,0,0.2); max-height: 500px; display: flex; flex-direction: column;">
      <div style="padding: 10px; border-bottom: 1px solid #eee;">📚 글도우미 챗봇</div>
      <div id="chat-log" style="flex: 1; overflow-y: auto; padding: 10px;"></div>
      <div style="padding: 10px; border-top: 1px solid #eee; display: flex; gap: 8px; align-items: flex-end;">
        <textarea id="chat-input" placeholder="도움을 받아보세요!" rows="2" style="flex: 1; resize: none; overflow-y: auto; max-height: 100px; line-height: 1.4; padding: 6px; border: 1px solid #ccc; border-radius: 4px;"></textarea>
        <button id="chat-send-btn" style="padding: 6px 12px; height: fit-content;">전송</button>
      </div>
    </div>
  `;

  wrapper.appendChild(chatBox);

    // ✋ HTML 안에 있는 입력창, 버튼, 채팅 기록 창을 가져오기
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send-btn");
  const log = document.getElementById("chat-log");
  let chatHistory = [];

  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendChat();
    }
  });

  sendBtn.addEventListener("click", sendChat);

  document.querySelectorAll('input[name="genre"]').forEach(radio => {
    radio.addEventListener("change", () => {
      const genre = radio.value;
      const character = document.getElementById("character-input")?.value || "default";

      const introMap = {
        emotion: {
          poem: "🌸 글썽이가 시 쓰기를 도와드려요.",
          essay: "💖 글썽이와 에세이 쓰기를 도와드려요.",
        },
        logic: {
          column: "📢 말썽이가 칼럼 쓰기를 도와줄게요.",
          analysis: "📊 말썽이가 분석글 쓰기를 도와줄게요.",
        }
      };

      const introText = introMap[character]?.[genre] || "✍️ 챗봇이 준비되었습니다.";

      if (log) {
        log.innerHTML += `<div style="color: gray;"><em>${introText}</em></div>`;
        log.scrollTop = log.scrollHeight;
      }
    });
  });  


  function sendChat() {
    const message = input.value.trim();
    if (!message) return;

    const character = document.getElementById("character-input")?.value || "default";
    const genre = document.querySelector('input[name="genre"]:checked')?.value || "default";

    log.innerHTML += `<div><strong>👩‍💻 나:</strong> ${message}</div>`;
    log.scrollTop = log.scrollHeight;

    // 히스토리에 사용자 메시지 추가
    chatHistory.push({ role: "user", content: message });    
    input.value = "";

    fetch("/geulssung/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken()
      },
      body: JSON.stringify({ message, genre, character, history: chatHistory })
    })
    .then(response => {
      if (!response.ok) throw new Error("서버 응답 실패");
      return response.json();
    })
    .then(data => {
      log.innerHTML += `<div><strong>🤖 챗봇:</strong> ${data.reply}</div>`;
      log.scrollTop = log.scrollHeight;
      sessionStorage.setItem("chat-log-html", log.innerHTML); // ✅ 대화내용 저장
    })
    .catch(error => {
      log.innerHTML += `<div style="color:red;"><strong>⚠️ 오류:</strong> ${error.message}</div>`;
      sessionStorage.setItem("chat-log-html", log.innerHTML); // ✅ 대화내용 저장
    });
  }

  function getCSRFToken() {
    const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }

  // ✅ 외부에서 토글할 수 있도록 전역 함수 등록
  window.toggleChat = function () {
    const box = document.getElementById("chat-box");
    if (box) {
      box.classList.toggle("hidden");
    }
  };
});
