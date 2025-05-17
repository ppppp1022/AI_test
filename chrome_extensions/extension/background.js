let port = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.toggle === true) {
    if (!port) {
      port = chrome.runtime.connectNative("com.example.nativehost");
      port.onMessage.addListener((nativeMessage) => {
        chrome.runtime.sendMessage(nativeMessage);
      });
    }
  } else if (message.toggle === false && port) {
    port.disconnect();
    port = null;
  }

  if ((message.type === "user_input" || message.type === "url" || message.type == "disscus") && port) {
    port.postMessage(message);
  }

  return true;
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  chrome.storage.local.get("enabled", (data) => {
    if (data.enabled && changeInfo.url) {
      if (!port) {
        port = chrome.runtime.connectNative("com.example.nativehost");
        port.onMessage.addListener((nativeMessage) => {
          chrome.runtime.sendMessage(nativeMessage);
        });
      }

      port.postMessage({
        type: "url",
        url: changeInfo.url,
        timestamp: new Date().toISOString()
      });
    }
  });
});
