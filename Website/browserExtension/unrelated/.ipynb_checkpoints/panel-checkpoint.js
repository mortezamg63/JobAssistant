// background.js
chrome.action.onClicked.addListener(async (tab) => {
  if (!tab?.id) return;

  // Toggle the panel by first injecting a small toggler script that checks for the panel
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: checkPanel
  });

  // If not present, inject panel.js
  // (You also need a way to remove the panel if it's already present, etc.)
});

function checkPanel() {
  const existing = document.getElementById('jobSaverContainer');
  return !!existing;
}
