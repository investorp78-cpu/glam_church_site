// Service Worker — Fountain of Grace Church
const CACHE = 'fog-v1';

self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil(clients.claim()); });

self.addEventListener('push', e => {
  if (!e.data) return;
  let data;
  try { data = e.data.json(); } catch { data = { title: 'Fountain of Grace', body: e.data.text() }; }
  e.waitUntil(
    self.registration.showNotification(data.title || 'Fountain of Grace Church', {
      body:    data.body    || 'You have a new update.',
      icon:    data.icon    || '/static/icon-192.png',
      badge:   data.badge   || '/static/icon-72.png',
      data:    data.url     || '/',
    })
  );
});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(clients.openWindow(e.notification.data || '/'));
});
