document.getElementById('toggleButton').addEventListener('click', function() {
  chrome.storage.local.get('isOn', function(data) {
    let newState = !data.isOn;
    chrome.storage.local.set({ isOn: newState });
    document.getElementById('toggleButton').innerText = newState ? 'Turn Off' : 'Turn On';
  });
});
