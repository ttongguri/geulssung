// static/js/chatbot_mobile.js (수정: 캐릭터 클릭 시만 챗봇 열림, 자동 열림 제거)

function checkChatActivation() {
  const input   = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send-btn");

  if (!input || !sendBtn) return;

  const selectedCategory = document.querySelector('input[name="category"]:checked');
  const selectedGenre    = document.querySelector('input[name="genre"]:checked');

  if (selectedCategory && selectedGenre) {
    input.disabled    = false;
    sendBtn.disabled  = false;
    input.placeholder = "도움을 받아보세요!";
  } else {
    input.disabled    = true;
    sendBtn.disabled  = true;
    input.placeholder = "⚠️ 글쓰기 도우미와 형식을 선택해 주세요.";
  }
}

window.checkChatActivation = checkChatActivation;

document.addEventListener("DOMContentLoaded", function () {
  const wrapper = document.getElementById("chat-box-wrapper");
  if (!wrapper) return;

  const input   = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send-btn");
  const log     = document.getElementById("chat-log");
  const chatBox = document.getElementById("chat-box");
  let chatHistory = [];

  if (input && sendBtn) {
    input.addEventListener("keydown", function (event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendChat();
      }
    });
    sendBtn.addEventListener("click", sendChat);
  }

  document.querySelectorAll('input[name="category"]').forEach(radio => {
    radio.addEventListener("change", () => {
      // 입력창 상태만 업데이트
      checkChatActivation();
    });
  });

  document.querySelectorAll('input[name="genre"]').forEach(radio => {
    radio.addEventListener("change", () => {
      const genre     = radio.value;
      const character = document.getElementById("character-input")?.value || "default";
      const introMap  = {
        emotion: {
          poem:   "🌸 글썽이가 시 쓰기를 도와드려요.",
          essay:  "💖 글썽이가 에세이 쓰기를 도와드려요."
        },
        logic: {
          column:   "📢 말썽이가 칼럼 쓰기를 도와줄게요.",
          analysis: "📊 말썽이가 분석글 쓰기를 도와줄게요."
        }
      };
      const introText = introMap[character]?.[genre] || "✍️ 챗봇이 준비되었습니다.";
      if (log) {
        log.innerHTML += `<div style="color: gray;"><em>${introText}</em></div>`;
        log.scrollTop = log.scrollHeight;
      }
      checkChatActivation();
    });
  });

  checkChatActivation();

  function sendChat() {
    const message = input?.value.trim();
    if (!message) return;

    const character = document.getElementById("character-input")?.value || "default";
    const genre     = document.querySelector('input[name="genre"]:checked')?.value || "default";

    if (log) {
      log.innerHTML += `<div><strong>👩‍💻 나:</strong> ${message}</div>`;
      log.scrollTop = log.scrollHeight;
    }

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
        if (log) {
          log.innerHTML += `<div><strong>🤖 챗봇:</strong> ${data.reply}</div>`;
          log.scrollTop = log.scrollHeight;
          sessionStorage.setItem("chat-log-html", log.innerHTML);
        }
      })
      .catch(error => {
        if (log) {
          log.innerHTML += `<div style="color:red;"><strong>⚠️ 오류:</strong> ${error.message}</div>`;
          sessionStorage.setItem("chat-log-html", log.innerHTML);
        }
      });
  }

  function getCSRFToken() {
    const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }

  // 캐릭터 클릭 시만 챗봇 열기 (자동 열림 제거)
  const charCont = document.getElementById("character-container");
  let isDragging = false, startX, startY, origRight, origBottom;

  wrapper.addEventListener("mousedown", e => {
    isDragging = true;
    startX     = e.clientX;
    startY     = e.clientY;
    const rect = wrapper.getBoundingClientRect();
    origRight  = window.innerWidth  - rect.right;
    origBottom = window.innerHeight - rect.bottom;
    wrapper.style.cursor = "grabbing";
    e.preventDefault();
  });

  document.addEventListener("mousemove", e => {
    if (!isDragging) return;
    const dx = e.clientX - startX;
    const dy = e.clientY - startY;
    wrapper.style.right  = `${origRight - dx}px`;
    wrapper.style.bottom = `${origBottom - dy}px`;
  });

  document.addEventListener("mouseup", () => {
    if (!isDragging) return;
    isDragging = false;
    wrapper.style.cursor = "grab";
  });

  if (charCont) {
    charCont.style.cursor = "pointer";
    charCont.addEventListener("click", () => {
      const chatBoxEl = document.getElementById("chat-box");
      if (chatBoxEl) chatBoxEl.classList.toggle("hidden");
    });
  }
}); 