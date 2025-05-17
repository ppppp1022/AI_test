chrome.storage.local.get('isOn', function(data) {
  if (data.isOn && window.location.hostname === "www.youtube.com") {
    alert("YouTube에 접속했습니다");
  }
});
