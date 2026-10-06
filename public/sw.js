/* Sorted's service worker (v133). It does one thing: show a reminder that arrives by Web Push, and open the right
   case when it is tapped. It caches nothing and never touches the network, so the page is always the latest one.
   A message carries no case details: a title, a line of fixed text, the case link, and the answer buttons. */
self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (e) { e.waitUntil(self.clients.claim()); });

self.addEventListener("push", function (e) {
  var m = {};
  try { m = e.data ? e.data.json() : {}; } catch (err) { m = {}; }
  var title = String(m.t || "Sorted").slice(0, 80);
  var opts = {
    body: String(m.b || "Something in Sorted needs a look.").slice(0, 160),
    tag: String(m.g || "sorted").slice(0, 64),
    renotify: true,
    data: { u: typeof m.u === "string" && /^\/(?![\/\\])/.test(m.u) ? m.u : "/", a: m.a && typeof m.a === "object" ? m.a : {} },
    actions: Array.isArray(m.x) ? m.x.slice(0, 2).map(function (x) { return { action: String(x[0]).slice(0, 12), title: String(x[1]).slice(0, 30) }; }) : []
  };
  e.waitUntil(self.registration.showNotification(title, opts));
});

self.addEventListener("notificationclick", function (e) {
  e.notification.close();
  var d = e.notification.data || {}, path = d.u || "/";
  if (e.action && d.a && typeof d.a[e.action] === "string" && /^\/(?![\/\\])/.test(d.a[e.action])) path = d.a[e.action];
  var url = new URL(path, self.location.origin).href;
  e.waitUntil(self.clients.matchAll({ type: "window", includeUncontrolled: true }).then(function (list) {
    for (var i = 0; i < list.length; i++) {
      var c = list[i];
      if (c.url.indexOf(self.location.origin) === 0 && "navigate" in c) return c.navigate(url).then(function (w) { return w && w.focus ? w.focus() : null; });
    }
    return self.clients.openWindow(url);
  }));
});
