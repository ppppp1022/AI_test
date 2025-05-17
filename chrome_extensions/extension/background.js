let port = null;
 
chrome.runtime.onMessage.addListener((message) => {
  if (message.toggle === true) {
    port = chrome.runtime.connectNative("com.example.nativehost");

    // Native Host 메시지 수신 시 popup으로 전달
    port.onMessage.addListener((nativeMessage) => {
      chrome.runtime.sendMessage(nativeMessage);
    });

  } else if (message.toggle === false && port) {
    port.disconnect();
    port = null;
  }else if (message.type === "newMessage") {
    // storage가 활성화되어 있고 port가 존재하는 경우에만 전송
    chrome.storage.local.get("enabled", (data) => {
      if (data.enabled && port) {
        // 메시지 내용을 네이티브 호스트에 전송
        port.postMessage({ 
          prompt: message.prompt.message,
          sender: message.prompt.name,
          timestamp: message.prompt.timestamp
        });
      }
    });
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  chrome.storage.local.get("enabled", (data) => {
    if (data.enabled && port && changeInfo.url) {
      port.postMessage({ url: changeInfo.url });
    }
  });
});
