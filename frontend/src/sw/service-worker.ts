// Service worker: offline caching
// Owner: Member 6 (Backend, Integration, QA & Deployment)
//
// Built by the `crew-vitals-service-worker` plugin in vite.config.ts into dist/sw.js. At build time
// the plugin replaces the two constants below with the real file list and a hash of its contents,
// so the cache name changes whenever any shipped file changes (no manual version bumps).
//
// Strategy
//   install    precache the whole app shell (HTML, JS, CSS, fonts, images, data snapshot)
//   navigation network first (3 s), then the cached index.html. Opens offline, fresh when online.
//   data/*.json stale-while-revalidate: answer from cache, refresh in the background
//   other GET  cache first (hashed assets never change), fall back to network and remember it
//   cross-origin and non-GET requests are never touched (NASA links, POSTs go straight through).

declare const __PRECACHE__: string[];
declare const __CACHE_VERSION__: string;

interface ExtendableEventLike { waitUntil(p: Promise<unknown>): void }
interface FetchEventLike extends ExtendableEventLike { request: Request; respondWith(r: Promise<Response> | Response): void }
interface SwScope {
  location: Location;
  skipWaiting(): Promise<void>;
  clients: { claim(): Promise<void> };
  addEventListener(type: "install" | "activate", l: (e: ExtendableEventLike) => void): void;
  addEventListener(type: "fetch", l: (e: FetchEventLike) => void): void;
}

const sw = self as unknown as SwScope;
const PREFIX = "crew-vitals-";
const CACHE = `${PREFIX}${__CACHE_VERSION__}`;
const abs = (u: string) => new URL(u, sw.location.href).href;
const INDEX = abs("./index.html");

sw.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE)
      .then((cache) => cache.addAll(__PRECACHE__.map((u) => new Request(abs(u), { cache: "reload" }))))
      .then(() => sw.skipWaiting()),
  );
});

sw.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k.startsWith(PREFIX) && k !== CACHE).map((k) => caches.delete(k))))
      .then(() => sw.clients.claim()),
  );
});

function withTimeout(p: Promise<Response>, ms: number): Promise<Response> {
  return new Promise((resolve, reject) => {
    const t = setTimeout(() => reject(new Error("timeout")), ms);
    p.then((r) => { clearTimeout(t); resolve(r); }, (e) => { clearTimeout(t); reject(e); });
  });
}

async function remember(req: Request, res: Response): Promise<void> {
  if (res.ok && res.type === "basic") await (await caches.open(CACHE)).put(req, res.clone());
}

async function handleNavigation(req: Request): Promise<Response> {
  try {
    const res = await withTimeout(fetch(req), 3000);
    if (res.ok) { void remember(new Request(INDEX), res.clone()); return res; }
  } catch { /* offline or slow: fall through to the cached shell */ }
  const cached = await caches.match(INDEX);
  return cached ?? new Response("Offline and the app has not been cached yet. Open it once while online.", { status: 503, headers: { "Content-Type": "text/plain" } });
}

async function staleWhileRevalidate(req: Request): Promise<Response> {
  const cached = await caches.match(req);
  const refresh = fetch(req).then(async (res) => { await remember(req, res); return res; });
  if (cached) { refresh.catch(() => {}); return cached; }
  return refresh;
}

async function cacheFirst(req: Request): Promise<Response> {
  const cached = await caches.match(req);
  if (cached) return cached;
  try {
    const res = await fetch(req);
    await remember(req, res);
    return res;
  } catch {
    return new Response("Offline and not cached.", { status: 503, headers: { "Content-Type": "text/plain" } });
  }
}

sw.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== sw.location.origin) return;
  if (req.mode === "navigate") event.respondWith(handleNavigation(req));
  else if (url.pathname.includes("/data/") && url.pathname.endsWith(".json")) event.respondWith(staleWhileRevalidate(req).catch(() => new Response("Offline and not cached.", { status: 503 })));
  else event.respondWith(cacheFirst(req));
});

export {};
