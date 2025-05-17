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
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  chrome.storage.local.get("enabled", (data) => {
    if (data.enabled && port && changeInfo.url) {
      port.postMessage({ url: changeInfo.url });
    }
  });
});
