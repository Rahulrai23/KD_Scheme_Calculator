const CACHE_NAME = "kc-scheme-v3";

/*
  Only STATIC & SAFE assets here
  ❌ Do NOT cache /scheme directly
*/
const STATIC_ASSETS = [
  "/",
  "/scheme",
  "/static/pwa/manifest.json",
  "/static/pwa/offline.html",

  // PDFs (offline access)
  "/static/pdfs/haryana.pdf",
  "/static/pdfs/karnataka.pdf",
  "/static/pdfs/rajasthan.pdf"
];

// -------------------------
// INSTALL
// -------------------------
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// -------------------------
// ACTIVATE
// -------------------------
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k))
      )
    )
  );
  self.clients.claim();
});

// -------------------------
// FETCH STRATEGY
// -------------------------
self.addEventListener("fetch", event => {
  const req = event.request;

  // Always try NETWORK FIRST for /scheme
  if (req.url.includes("/scheme")) {
    event.respondWith(
      fetch(req).catch(() =>
        caches.match("/static/pwa/offline.html")
      )
    );
    return;
  }

  // Cache-first for everything else
  event.respondWith(
    caches.match(req).then(res => {
      return res || fetch(req);
    })
  );
});
