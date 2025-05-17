let isOn = false;  // 기본 상태는 off

// 확장 프로그램이 설치되었을 때 기본 상태 설정
chrome.runtime.onInstalled.addListener(() => {
  chrome.storage.local.set({ isOn: false });
});

// 확장 프로그램 아이콘 클릭 시 on/off 상태 전환
chrome.action.onClicked.addListener((tab) => {
  isOn = !isOn;
  chrome.storage.local.set({ isOn: isOn });

  // 서버를 자동 실행
  if (isOn) {
    startPythonServer();
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      function: notifyUserOnYouTube
    });
  }
});

// Python 서버가 실행 중인지 확인 후, 실행
function startPythonServer() {
  chrome.storage.local.get('pythonServerRunning', function(data) {
    if (!data.pythonServerRunning) {
      chrome.storage.local.set({ pythonServerRunning: true });
      fetch('http://localhost:5000/start', { method: 'POST' })  // Python 서버를 시작하는 API 호출
        .catch(error => console.log('서버 시작 중 오류 발생:', error));
    }
  });
}

function notifyUserOnYouTube() {
  if (window.location.hostname === "www.youtube.com") {
    alert("YouTube에 접속했습니다");
  }
}
