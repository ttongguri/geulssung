document.addEventListener("DOMContentLoaded", function () {
  const chatBox = document.createElement("div");
  chatBox.id = "chat-box";
  chatBox.innerHTML = `
    <div style="position: fixed; bottom: 80px; right: 20px; width: 320px; background: white; border: 1px solid #ccc; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.2); z-index: 9999;">
      <div style="padding: 10px; border-bottom: 1px solid #eee;">📚 글도우미 챗봇</div>
      <div id="chat-log" style="height: 200px; overflow-y: auto; padding: 10px;"></div>
      <div style="padding: 10px; border-top: 1px solid #eee;">
        <input id="chat-input" type="text" placeholder="도움을 받아보세요!" style="width: 70%;" />
        <button id="chat-send-btn">전송</button>
      </div>
    </div>
  `;
  document.body.appendChild(chatBox);

  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send-btn");

  input.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      event.preventDefault();
      sendChat();
    }
  });

  sendBtn.addEventListener("click", sendChat);

  // ✅ 장르 변경 시 환영 메시지 추가
  document.querySelectorAll('input[name="genre"]').forEach(radio => {
    radio.addEventListener("change", () => {
      const genre = radio.value;
      const log = document.getElementById("chat-log");
      const introMap = {
        poem: "✍️ 시 쓰기를 도와드릴게요. 어떤 감정이 떠오르시나요?",
        essay: "📝 에세이 작성에 필요한 생각을 나눠보세요.",
        column: "🗞️ 칼럼 주제에 대한 의견을 말씀해보세요.",
        analysis: "📊 분석글에 필요한 통계나 관점을 도와드릴게요."
      };
      if (log) {
        log.innerHTML += `<div style="color: gray;"><em>${introMap[genre] || "챗봇이 준비되었습니다."}</em></div>`;
        log.scrollTop = log.scrollHeight;
      }
    });
  });
});

function sendChat() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (!message) return;

  const log = document.getElementById("chat-log");
  log.innerHTML += `<div><strong>👩‍💻 나:</strong> ${message}</div>`;
  log.scrollTop = log.scrollHeight;

  input.value = '';

  // ✅ 현재 선택된 장르를 같이 보냄
  const genre = document.querySelector('input[name="genre"]:checked')?.value || 'default';

  fetch('/geulssung/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message, genre })
  })
    .then(response => {
      if (!response.ok) throw new Error("서버 응답 실패");
      return response.json();
    })
    .then(data => {
      log.innerHTML += `<div><strong>🤖 챗봇:</strong> ${data.reply}</div>`;
      log.scrollTop = log.scrollHeight;
    })
    .catch(error => {
      log.innerHTML += `<div style="color:red;"><strong>⚠️ 오류:</strong> ${error.message}</div>`;
    });
}
