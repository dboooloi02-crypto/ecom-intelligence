let idx = {};
chrome.runtime.onInstalled.addListener(() => {});
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.type === 'DOWNLOAD_JSON') {
    const url = URL.createObjectURL(new Blob([msg.data], { type: 'application/json' }));
    chrome.downloads.download({ url, filename: msg.filename || 'data.json', saveAs: true });
  }
});
