/* Sorted's service worker (v133). It shows a reminder that arrives by Web Push, and opens the right case when it is
   tapped. It caches nothing, so the page is always the latest one. A message carries no case details: a title, a line
   of fixed text, the case link, and the answer buttons.
   v142: it also receives Android's share sheet. The manifest posts shared words to /share-target; they are handed to
   the page in the address's # part (/#new=…), so they never reach a server or its logs. Nothing else is touched.
   v145: if an open Sorted window can't be sent to the case (a window this worker doesn't control refuses navigate()),
   the case opens in a new window instead of the tap doing nothing. */
self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (e) { e.waitUntil(self.clients.claim()); });

self.addEventListener("fetch", function (e) {
  var r = e.request;
  if (r.method !== "POST") return;
  var u = new URL(r.url);
  if (u.origin !== self.location.origin || u.pathname !== "/share-target") return;
  e.respondWith(r.formData().then(function (f) {
    var t = [f.get("st"), f.get("sx"), f.get("su")].filter(function (x) { return typeof x === "string" && x.trim(); }).join("\n").slice(0, 4000);
    return Response.redirect(self.location.origin + "/" + (t ? "#new=" + encodeURIComponent(t) : "#start"), 303);
  }, function () { return Response.redirect(self.location.origin + "/#start", 303); }));
});

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
      if (c.url.indexOf(self.location.origin) === 0 && "navigate" in c) return c.navigate(url).then(function (w) { if (!w) return self.clients.openWindow(url); return w.focus ? w.focus() : null; }, function () { return self.clients.openWindow(url); });
    }
    return self.clients.openWindow(url);
  }));
});
