/**
 * Shopee Scout - Core Extractor
 */
const SELECTOR_STRATEGIES = [
  { name: 'data-sqe', selector: 'div[data-sqe="item"]' },
  { name: 'search-item', selector: '.shopee-search-item-result__item' },
  { name: 'product-id', selector: '[data-shopee-product-id]' },
  { name: 'col-xs', selector: '.col-xs-2-4' },
  { name: 'class-fuzzy', selector: '[class*="card"], [class*="item"], [class*="product"]' },
  { name: 'product-link', selector: 'a[href*="/product/"]' },
];
function checkHealth() {
  const report = { pageType: 'unknown', hasItems: false, matchingSelectors: [], itemCount: 0, timestamp: Date.now() };
  const url = window.location.href;
  if (url.includes('shopee.')) report.pageType = 'shopee';
  for (const s of SELECTOR_STRATEGIES) {
    const items = document.querySelectorAll(s.selector);
    if (items.length > 0) report.matchingSelectors.push({ name: s.name, count: items.length });
  }
  const best = findItems();
  report.hasItems = best.length > 0;
  report.itemCount = best.length;
  return report;
}
function findItems() {
  for (const s of SELECTOR_STRATEGIES) {
    const items = document.querySelectorAll(s.selector);
    if (items.length >= 3) return items;
  }
  const productLinks = document.querySelectorAll('a[href*="/product/"]');
  const candidates = [];
  const seen = new Set();
  productLinks.forEach((a) => {
    let el = a;
    for (let i = 0; i < 5; i++) {
      el = el.parentElement;
      if (!el) break;
      if (el.innerText && /[$\u20B1\u0E3FRM]\s*\d/.test(el.innerText)) {
        if (!seen.has(el)) { seen.add(el); candidates.push(el); }
        break;
      }
    }
  });
  return candidates.slice(0, 60);
}
function extractPrice(text) {
  const m = text.match(/([$\u20B1\u0E3FRM]?)\s*(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)/);
  return m ? m[2].replace(/,/g, '') : '0';
}
function extractSold(text) {
  const m = text.match(/(\d[\d,.]*)\s*(k\s*)?sold/i) || text.match(/已[售卖]\s*(\d[\d,.]*)/i) || text.match(/(\d[\d,.]*)\s*[件笔单]/);
  if (m) { let v = m[1].replace(/,/g, ''); if (m[2] && m[2].toLowerCase().includes('k')) v = String(parseFloat(v) * 1000); return v; }
  return '0';
}
function extractTitle(lines, text) {
  for (const line of lines) {
    const l = line.trim();
    if (l && !l.match(/^[$\u20B1\u0E3FRM]/) && !l.match(/sold|已[售卖]/i) && !l.match(/^[\d.]+$/) && !l.match(/^[\u2B50\u2605]/) && l.length > 3) return l.slice(0, 120);
  }
  return (lines[0] || text).slice(0, 80);
}
function extractRating(text) {
  const m = text.match(/(\d\.\d)\s*[\u2B50\u2605]/) || text.match(/[\u2B50\u2605]\s*(\d\.\d)/) || text.match(/(\d\.\d)\s*[分]/);
  return m ? m[1] : '';
}
function extractShop(lines) {
  for (const line of lines) {
    if (line.match(/shop|store|mall|店铺|卖家/i) && !line.match(/sold|price|[$\u20B1\u0E3FRM]/i)) return line.trim().slice(0, 40);
  }
  return '';
}
function extractUrl(el) {
  if (el.tagName === 'A' && el.href) return el.href;
  const inner = el.querySelector('a[href*="/product/"]') || el.querySelector('a');
  if (inner && inner.href) return inner.href;
  let parent = el.parentElement;
  for (let i = 0; i < 5; i++) {
    if (!parent) break;
    if (parent.tagName === 'A' && parent.href) return parent.href;
    parent = parent.parentElement;
  }
  return '';
}
function extractProducts() {
  const items = findItems();
  const results = [];
  const seen = new Set();
  items.forEach((item, index) => {
    try {
      const text = item.innerText.trim();
      if (!text || text.length < 20) return;
      const lines = text.split('\n').filter(l => l.trim());
      const title = extractTitle(lines, text);
      const price = extractPrice(text);
      const key = `${title.slice(0, 30)}_${price}`;
      if (seen.has(key)) return;
      seen.add(key);
      results.push({ rank: index + 1, title, price, sold: extractSold(text), rating: extractRating(text), shop: extractShop(lines), url: extractUrl(item) });
    } catch (err) { console.warn('[Shopee Scout] skip:', err.message); }
  });
  return results;
}
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  switch (request.type) {
    case 'EXTRACT_PRODUCTS': sendResponse({ success: true, data: extractProducts() }); break;
    case 'CHECK_HEALTH': sendResponse({ success: true, data: checkHealth() }); break;
  }
  return true;
});
if (typeof window !== 'undefined') {
  window.__shopeeScoutExtract = extractProducts;
  window.__shopeeScoutHealth = checkHealth;
  let _timer = null;
  const _obs = new MutationObserver(() => {
    clearTimeout(_timer);
    _timer = setTimeout(() => { chrome.runtime.sendMessage({ type: 'DOM_UPDATED' }).catch(() => {}); }, 800);
  });
  _obs.observe(document.body, { childList: true, subtree: true });
}
