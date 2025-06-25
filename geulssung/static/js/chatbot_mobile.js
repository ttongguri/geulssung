// ✅ 입력창/버튼 활성화 여부 확인 함수
function checkChatActivation() {
  const input   = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send-btn");

  if (!input || !sendBtn) return;

  const selectedCategory = document.querySelector('input[name="category"]:checked');
  const selectedGenre    = document.querySelector('input[name="genre"]:checked');
  
  // 두 항목이 모두 선택되어야 입력 가능
  if (selectedCategory && selectedGenre) {
    input.disabled    = false;
    input.readOnly    = false;
    input.placeholder = "도움을 받아보세요!";
    sendBtn.disabled  = false;
  } else {
    input.disabled    = true;
    input.placeholder = "⚠️ 글쓰기 도우미와 형식을 선택해 주세요.";
    sendBtn.disabled  = true;
  }
}

// 다른 곳에서도 호출 가능하도록 전역 등록
window.checkChatActivation = checkChatActivation;

document.addEventListener("DOMContentLoaded", function () {
  // 📦 주요 요소들 가져오기
  const wrapper  = document.getElementById("chat-box-wrapper"); // 챗봇 전체 박스
  if (!wrapper) return;

  const input    = document.getElementById("chat-input");
  const sendBtn  = document.getElementById("chat-send-btn");
  const log      = document.getElementById("chat-log");
  const chatBox  = document.getElementById("chat-box");
  let chatHistory = []; // 챗봇 대화 기록 저장 (GPT API 연동용)

  // ⌨️ 사용자 입력 이벤트 처리 (Enter 또는 버튼 클릭 시 전송)
  if (input && sendBtn) {
    input.addEventListener("keydown", function (event) {
      if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendChat();
      }
    });
    sendBtn.addEventListener("click", sendChat);
  }

  // 📌 도우미(category) 선택 시 입력창 활성화 여부 갱신
  document.querySelectorAll('input[name="category"]').forEach(radio => {
    radio.addEventListener("change", () => {
      checkChatActivation();
    });
  });

  // 🧠 장르(genre) 선택 시: 캐릭터별 인트로 메시지 출력 + 입력창 활성화
  document.querySelectorAll('input[name="genre"]').forEach(radio => {
    radio.addEventListener("change", () => {
      const genre     = radio.value;
      const character = document.getElementById("character-input")?.value || "default";

      // 캐릭터별 장르 대응 인트로 문구
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

      // ✅ 안내 문구는 유효한 경우에만 출력 (기본값 제거됨)
      const introText = introMap[character]?.[genre];
      if (introText && log) {
        log.innerHTML += `<div style="color: gray;"><em>${introText}</em></div>`;
        log.scrollTop = log.scrollHeight;
      }
      checkChatActivation();
    });
  });

  // 초기화 시 입력창 상태 확인
  checkChatActivation();

  // 📤 사용자 메시지 전송 함수 (서버에 fetch POST)
  function sendChat() {
    const message = input?.value.trim();
    if (!message) return;

    const character = document.getElementById("character-input")?.value || "default";
    const genre     = document.querySelector('input[name="genre"]:checked')?.value || "default";

    // 사용자 메시지 출력
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
          sessionStorage.setItem("chat-log-html", log.innerHTML); // 새로고침 대비
        }
      })
      .catch(error => {
        if (log) {
          log.innerHTML += `<div style="color:red;"><strong>⚠️ 오류:</strong> ${error.message}</div>`;
          sessionStorage.setItem("chat-log-html", log.innerHTML);
        }
      });
  }

  // 📥 CSRF 토큰 추출 함수 (Django용)
  function getCSRFToken() {
    const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }

  // 🧲 챗봇 드래그 기능
  let isDragging = false, startX, startY, origRight, origBottom;

  wrapper.addEventListener("mousedown", e => {
    isDragging = true;
    startX     = e.clientX;
    startY     = e.clientY;
    const rect = wrapper.getBoundingClientRect();
    origRight  = window.innerWidth  - rect.right;
    origBottom = window.innerHeight - rect.bottom;
    wrapper.style.cursor = "grabbing";
    e.preventDefault(); // 드래그 중 텍스트 선택 방지
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

  // 🧑‍🎤 캐릭터 클릭 시 챗봇 토글 (자동 열림 제거)
  const charCont = document.getElementById("character-container");
  if (charCont) {
    charCont.style.cursor = "pointer";
    charCont.addEventListener("click", () => {
      const chatBoxEl = document.getElementById("chat-box");
      if (chatBoxEl) chatBoxEl.classList.toggle("hidden");
    });
  }
});
