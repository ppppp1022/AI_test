const button = document.getElementById("slider");
const slider_text = document.getElementById("isToggle");
const summatinoDiv = document.getElementById("after_summation");
var summationpage = false;


chrome.storage.local.get("enabled", (data) => {
  button.textContent = data.enabled ? "Turn Off" : "Turn On";
}); 

button.addEventListener("click", () => {
  
  if(!summationpage) {
    summatinoDiv.style.display = 'block';
    slider_text.textContent = "On";
    summationpage = true;
  }else {
    summatinoDiv.style.display = 'none';
    slider_text.textContent = "Off";
    summationpage = false;
  }

  chrome.storage.local.get("enabled", (data) => {
    const newState = !data.enabled;
    
    chrome.storage.local.set({ enabled: newState }, () => {
    chrome.runtime.sendMessage({ toggle: newState });
    });
  });
});
let messages = [];

// DOM 요소 참조
const messageContainer = document.getElementById('messageContainer');
const messageForm = document.getElementById('messageForm');
const messageInput = document.getElementById('messageInput');
const SizeButton = document.getElementById('changeSize');

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
  const newMessage = { name, message, timestamp };

  if(name === "You")
  {
    chrome.runtime.sendMessage({
    type: "user_input",
    prompt: message,
    sender: name,
    timestamp: timestamp
    });
  }
  messages.push(newMessage);
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
    const name = 'You';
    
    if (message) {
        addMessage(name, message);
        messageInput.value = '';
    }
});

SizeButton.addEventListener('click',() => {
  chrome.runtime.sendMessage({type: "disscus"});
});

chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "chunk") {
    addMessage(msg.from, msg.data);
  }
});
