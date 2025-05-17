const button = document.getElementById("toggle");

chrome.storage.local.get("enabled", (data) => {
  button.textContent = data.enabled ? "Turn Off" : "Turn On";
});

button.addEventListener("click", () => {
  chrome.storage.local.get("enabled", (data) => {
    const newState = !data.enabled;
    chrome.storage.local.set({ enabled: newState }, () => {
      button.textContent = newState ? "Turn Off" : "Turn On";
      chrome.runtime.sendMessage({ toggle: newState });
    });
  });
});