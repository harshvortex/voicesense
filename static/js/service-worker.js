const CACHE_NAME = 'voicesense-v1';
const URLS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  '/static/js/service-worker.js',
  '/static/manifest.json',
  '/health',
];

// ── Install event ────────────────────────────────────────────────────────────
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Installing...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] Caching core assets');
      return cache.addAll(URLS_TO_CACHE).catch((error) => {
        console.warn('[ServiceWorker] Cache addAll error:', error);
      });
    })
  );
  self.skipWaiting();
});

// ── Activate event ───────────────────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activating...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME)
          .map((cacheName) => {
            console.log('[ServiceWorker] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          })
      );
    })
  );
  self.clients.claim();
});

// ── Fetch event ──────────────────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip cross-origin requests
  if (url.origin !== self.location.origin) {
    return;
  }

  // Network-first strategy for API calls
  if (url.pathname === '/analyze' || url.pathname === '/health') {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.status === 200) {
            const clonedResponse = response.clone();
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, clonedResponse);
            });
          }
          return response;
        })
        .catch(() => {
          return caches.match(request).then((response) => {
            return response || new Response(
              JSON.stringify({ error: 'Network error. Please try again.' }),
              { status: 503, headers: { 'Content-Type': 'application/json' } }
            );
          });
        })
    );
    return;
  }

  // Cache-first strategy for static assets
  event.respondWith(
    caches.match(request).then((response) => {
      if (response) {
        return response;
      }
      return fetch(request)
        .then((response) => {
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          const clonedResponse = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(request, clonedResponse);
          });
          return response;
        })
        .catch(() => {
          return new Response(
            'Network error. Please try again.',
            { status: 503 }
          );
        });
    })
  );
});

// ── Background sync for offline support ───────────────────────────────────────
self.addEventListener('sync', (event) => {
  console.log('[ServiceWorker] Background sync event:', event.tag);
  if (event.tag === 'sync-audio-analysis') {
    event.waitUntil(syncAudioAnalysis());
  }
});

async function syncAudioAnalysis() {
  try {
    console.log('[ServiceWorker] Syncing pending audio analysis...');
    // In a real app, you would retrieve queued requests from IndexedDB
    // and retry them here
  } catch (error) {
    console.error('[ServiceWorker] Sync error:', error);
  }
}

// ── Message handler ──────────────────────────────────────────────────────────
self.addEventListener('message', (event) => {
  console.log('[ServiceWorker] Message received:', event.data);
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
