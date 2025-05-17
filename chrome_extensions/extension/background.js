let port = null;

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  switch(message.type){
    case "init":
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
      break;
    case "user_input":
      if(message.prompt){
        port.onMessage.addListener((message)=>{
          chrome.runtime.sendMessage({type: "user_input", prompt:message.prompt});
        });
      }
      break;
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  chrome.storage.local.get("enabled", (data) => {
    if (data.enabled && port && changeInfo.url) {
      port.postMessage({ url: changeInfo.url });
    }
  });
});
