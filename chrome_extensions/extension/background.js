let port = null;

chrome.runtime.onMessage.addListener((message) => {
  if (message.toggle === true) {
    port = chrome.runtime.connectNative("com.example.nativehost");
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