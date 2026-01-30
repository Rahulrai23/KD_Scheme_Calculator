const CACHE_NAME = "kc-scheme-v1";

const OFFLINE_ASSETS = [
  "/scheme",
  "/static/pwa/manifest.json",
  "/static/pdfs/haryana.pdf",
  "/static/pdfs/karnataka.pdf",
  "/static/pdfs/rajasthan.pdf"
];

// INSTALL
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(OFFLINE_ASSETS))
  );
});

// FETCH
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      return response || fetch(event.request);
    })
  );
});

