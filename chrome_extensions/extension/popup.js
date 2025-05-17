const button = document.getElementById("toggle");

chrome.storage.local.get("enabled", (data) => {
  button.textContent = data.enabled ? "Turn Off" : "Turn On";
});

button.addEventListener("click", () => {
  chrome.storage.local.get("enabled", (data) => {
    const newState = !data.enabled;
    chrome.storage.local.set({ enabled: newState }, () => {
      button.textContent = newState ? "Turn Off" : "Turn On";
      //chrome.runtime.sendMessage({ toggle: newState });
    });
  });
});
let messages = [];

// DOM 요소 참조
const messageContainer = document.getElementById('messageContainer');
const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const nameInput = document.getElementById('nameInput');
const clearButton = document.getElementById('clearButton');
const sampleButton = document.getElementById('sampleButton');
const bigSizeButton = document.getElementById('changeSize');

// 현재 시간 포맷팅 함수
function formatTimestamp() {
    const now = new Date();
    const options = { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit', 
        minute: '2-digit',
        hour12: false
    };
    return now.toLocaleString('ko-KR', options);
}

// 메시지 추가 함수
function addMessage(name, message, timestamp = formatTimestamp()) {
    // 새 메시지 객체 생성
    const newMessage = { name, message, timestamp };
    
    // 메시지 배열에 추가
    messages.push(newMessage);
    
    // UI에 메시지 표시
    displayMessages();
}

// 메시지 렌더링 함수
function displayMessages() {
    // 기존 메시지 컨테이너 내용 지우기
    messageContainer.innerHTML = '';
    
    // 모든 메시지 렌더링
    messages.forEach(msg => {
        const messageElement = document.createElement('div');
        messageElement.className = 'message';
        
        const headerElement = document.createElement('div');
        headerElement.className = 'message-header';
        
        const nameElement = document.createElement('span');
        nameElement.className = 'message-name';
        nameElement.textContent = msg.name;
        
        const timestampElement = document.createElement('span');
        timestampElement.className = 'message-timestamp';
        timestampElement.textContent = msg.timestamp;
        
        headerElement.appendChild(nameElement);
        headerElement.appendChild(timestampElement);
        
        const contentElement = document.createElement('div');
        contentElement.className = 'message-content';
        contentElement.textContent = msg.message;
        
        messageElement.appendChild(headerElement);
        messageElement.appendChild(contentElement);
        
        messageContainer.appendChild(messageElement);
    });
    
    // 스크롤을 가장 아래로 이동
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

// 폼 제출 이벤트 처리
messageForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const message = messageInput.value.trim();
    const name = nameInput.value.trim() || '사용자';
    
    if (message) {
        addMessage(name, message);
        messageInput.value = '';
    }
});

// 모든 메시지 지우기
clearButton.addEventListener('click', () => {
    messages = [];
    displayMessages();
});

// 예제 메시지 추가
sampleButton.addEventListener('click', () => {
    addMessage('dd');
    addMessage('김철수', '네, 안녕하세요. 오늘 날씨가 좋네요.', '2025-05-18 14:32');
    addMessage('이영희', '맞아요. 정말 화창한 날이에요!', '2025-05-18 14:35');
});

// 초기 예제 메시지 표시
addMessage('시스템', '메시지 표시 시스템에 오신 것을 환영합니다.', '2025-05-18 14:00');

bigSizeButton.addEventListener('click',() => {
  document.body.style.width = '150%';
  document.body.style.height = '90vh';
  document.body.style.fontSize = '1.5rem';
});