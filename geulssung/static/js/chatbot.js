// chatbot.js

document.addEventListener("DOMContentLoaded", function () {
  // ┌────────────────────────────────────────────────────────────────┐
  // │ 1. 챗봇 래퍼(wrapper) 요소 가져오기                            │
  // └────────────────────────────────────────────────────────────────┘
  const wrapper = document.getElementById("chat-box-wrapper");
  if (!wrapper) {
    console.error("❌ chat-box-wrapper가 HTML에 존재하지 않습니다.");
    return;
  }

  // ┌────────────────────────────────────────────────────────────────┐
  // │ 2. 챗봇 박스(DOM) 생성 및 wrapper에 추가                         │
  // └────────────────────────────────────────────────────────────────┘
  const chatBox = document.createElement("div");
  chatBox.id = "chat-box";
  chatBox.classList.add("hidden"); // 기본 상태는 숨김
  chatBox.innerHTML = `
    <div style="
      width: 100%;
      max-width: 400px;
      background: white;
      border: 1px solid #ccc;
      border-radius: 0 0 10px 10px;
      box-shadow: 0 0 10px rgba(0,0,0,0.2);
      max-height: 500px;
      display: flex;
      flex-direction: column;
    ">
      <!-- 챗봇 헤더 -->
      <div style="padding: 10px; border-bottom: 1px solid #eee;">
        📚 글쓰기 도우미
      </div>

      <!-- 대화 로그 영역 -->
      <div id="chat-log" style="flex: 1; overflow-y: auto; padding: 10px;"></div>

      <!-- 입력창과 전송 버튼 영역 -->
      <div style="
        padding: 10px;
        border-top: 1px solid #eee;
        display: flex;
        gap: 8px;
        align-items: flex-end;
      ">
        <textarea
          id="chat-input"
          placeholder="도움을 받아보세요!"
          rows="2"
          style="
            flex: 1;
            resize: none;
            overflow-y: auto;
            max-height: 100px;
            line-height: 1.4;
            padding: 6px;
            border: 1px solid #ccc;
            border-radius: 4px;
          "
        ></textarea>
        <button
          id="chat-send-btn"
          style="padding: 6px 12px; height: fit-content;"
        >
          전송
        </button>
      </div>
    </div>
  `;
  wrapper.appendChild(chatBox);

  // ┌────────────────────────────────────────────────────────────────┐
  // │ 3. 주요 DOM 요소 참조                                           │
  // └────────────────────────────────────────────────────────────────┘
  const input   = document.getElementById("chat-input");   // 채팅 입력창
  const sendBtn = document.getElementById("chat-send-btn"); // 전송 버튼
  const log     = document.getElementById("chat-log");      // 대화 로그
  let chatHistory = [];                                     // 대화 기록 저장소

  // ┌────────────────────────────────────────────────────────────────┐
  // │ 4. 입력창 활성/비활성 결정 함수                                  │
  // │   - write_form.html에서만 작동하도록: category, genre 라디오 존재 여부 │
  // │   - 두 라디오 모두 체크해야만 입력 활성화; 아니면 disabled 상태로 유지 │
  // └────────────────────────────────────────────────────────────────┘
  function checkChatActivation() {
    const hasCategoryInputs = document.querySelectorAll('input[name="category"]').length > 0;
    const hasGenreInputs    = document.querySelectorAll('input[name="genre"]').length > 0;

    if (hasCategoryInputs && hasGenreInputs) {
      // write_form.html: 라디오 버튼이 둘 다 있어야 활성/비활성 로직 적용
      const selectedCategory = document.querySelector('input[name="category"]:checked');
      const selectedGenre    = document.querySelector('input[name="genre"]:checked');

      if (selectedCategory && selectedGenre) {
        // 둘 다 체크된 경우: 입력창, 버튼 활성화
        input.disabled       = false;
        sendBtn.disabled     = false;
        input.placeholder    = "도움을 받아보세요!";
      } else {
        // 하나라도 체크되지 않은 경우: 입력창, 버튼 비활성화
        input.disabled       = true;
        sendBtn.disabled     = true;
        input.placeholder    = "⚠️ 글쓰기 도우미와 형식을 선택해 주세요.";
      }
    } else {
      // 다른 페이지(라디오 버튼이 없는 경우): 항상 활성화
      input.disabled       = false;
      sendBtn.disabled     = false;
      input.placeholder    = "도움을 받아보세요!";
    }
  }

  // ┌────────────────────────────────────────────────────────────────┐
  // │ 5. 키보드/버튼 이벤트 설정                                        │
  // └────────────────────────────────────────────────────────────────┘
  // 엔터 입력(Shift+Enter 제외) 시 sendChat() 호출
  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendChat();
    }
  });
  // 전송 버튼 클릭 시 sendChat() 호출
  sendBtn.addEventListener("click", sendChat);

  // ┌────────────────────────────────────────────────────────────────┐
  // │ 6. 라디오 버튼 변경 시 활성/비활성 재판단                          │
  // └────────────────────────────────────────────────────────────────┘
  // (1) “글쓰기 도우미”(category) 라디오 그룹
  document.querySelectorAll('input[name="category"]').forEach(radio => {
    radio.addEventListener("change", () => {
      checkChatActivation();
    });
  });

  // (2) “형식”(genre) 라디오 그룹
  document.querySelectorAll('input[name="genre"]').forEach(radio => {
    radio.addEventListener("change", () => {
      // 인트로 메시지 출력 (장르 선택 시)
      const genre     = radio.value;
      const character = document.getElementById("character-input")?.value || "default";
      const introMap  = {
        emotion: {
          poem:   "🌸 글썽이가 시 쓰기를 도와드려요.",
          essay:  "💖 글썽이와 에세이 쓰기를 도와드려요."
        },
        logic: {
          column:   "📢 말썽이가 칼럼 쓰기를 도와줄게요.",
          analysis: "📊 말썽이가 분석글 쓰기를 도와줄게요."
        }
      };
      const introText = introMap[character]?.[genre] || "✍️ 챗봇이 준비되었습니다.";
      log.innerHTML += `<div style="color: gray;"><em>${introText}</em></div>`;
      log.scrollTop = log.scrollHeight;

      // 선택 상태가 바뀔 때마다 입력창 활성/비활성 재판단
      checkChatActivation();
    });
  });

  // ┌────────────────────────────────────────────────────────────────┐
  // │ 7. 페이지 로드 직후 입력창 초기 상태 설정                          │
  // └────────────────────────────────────────────────────────────────┘
  checkChatActivation();

  // ┌────────────────────────────────────────────────────────────────┐
  // │ 8. 메시지 전송 처리 함수(sendChat)                                 │
  // │   - 입력값이 비어 있으면 종료                                         │
  // │   - 선택된 category, genre 정보와 함께 서버로 POST 요청             │
  // └────────────────────────────────────────────────────────────────┘
  function sendChat() {
    const message = input.value.trim();
    if (!message) return;

    const character = document.getElementById("character-input")?.value || "default";
    const genre     = document.querySelector('input[name="genre"]:checked')?.value || "default";

    // 사용자 메시지를 로그에 추가
    log.innerHTML += `<div><strong>👩‍💻 나:</strong> ${message}</div>`;
    log.scrollTop = log.scrollHeight;

    // 대화 기록에 사용자 메시지 저장
    chatHistory.push({ role: "user", content: message });
    input.value = "";

    // 서버로 fetch 요청 (예: /geulssung/chat)
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
        // 서버 응답을 로그에 추가
        log.innerHTML += `<div><strong>🤖 챗봇:</strong> ${data.reply}</div>`;
        log.scrollTop = log.scrollHeight;
        sessionStorage.setItem("chat-log-html", log.innerHTML);
      })
      .catch(error => {
        log.innerHTML += `<div style="color:red;"><strong>⚠️ 오류:</strong> ${error.message}</div>`;
        sessionStorage.setItem("chat-log-html", log.innerHTML);
      });
  }

  // ┌────────────────────────────────────────────────────────────────┐
  // │ 9. CSRF 토큰을 쿠키에서 꺼내오는 헬퍼 함수                         │
  // └────────────────────────────────────────────────────────────────┘
  function getCSRFToken() {
    const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }

  // ┌────────────────────────────────────────────────────────────────┐
  // │ 10. 토글 버튼(“챗봇 열기/닫기”) 클릭 시 실행되는 함수               │
  // │    - 챗봇을 보이거나 숨김 상태로 전환                                  │
  // │    - write_form.html인 경우(라디오 존재) 재검토 후 경고문 삽입          │
  // └────────────────────────────────────────────────────────────────┘
  window.toggleChat = function () {
    const box = document.getElementById("chat-box");
    const log = document.getElementById("chat-log");
    if (!box || !log) return;

    // 챗봇 보이기/숨기기 토글
    box.classList.toggle("hidden");

    // write_form.html인 경우 
    // 챗봇이 보이게 된 직후에만 실행
    const isNowVisible = !box.classList.contains("hidden");
    if (isNowVisible) {
      checkChatActivation();

      // write_form.html인 경우: 두 라디오가 모두 선택되지 않으면 경고문 출력
      const hasCategoryInputs = document.querySelectorAll('input[name="category"]').length > 0;
      const hasGenreInputs    = document.querySelectorAll('input[name="genre"]').length > 0;

      if (hasCategoryInputs && hasGenreInputs) {
        const selectedCategory = document.querySelector('input[name="category"]:checked');
        const selectedGenre    = document.querySelector('input[name="genre"]:checked');
        if (!selectedCategory || !selectedGenre) {
          // 이미 경고문이 있다면 중복 방지
          if (!document.getElementById("chat-warning")) {
            log.innerHTML = `
              <div id="chat-warning"
                   style="
                     color: #b23b3b;
                     padding: 8px;
                     border-radius: 4px;
                     font-weight: bold;
                     margin-bottom: 8px;
                   ">
                ⚠️ 글쓰기 도우미와 형식을 선택해 주세요.
              </div>
            ` + log.innerHTML;
            log.scrollTop = log.scrollHeight;
          }
        }
      }
      // 다른 페이지라면 경고문 관련 로직은 실행되지 않으며, 입력창은 활성화 상태로 유지됩니다.
    }
  };
});
