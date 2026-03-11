# 📱 PWA Setup Guide — VoiceSense

VoiceSense is now a **Progressive Web App (PWA)**! Users can install it on their phones, tablets, and desktops for a native app-like experience.

## ✨ Features Enabled

- **Installable**: Add to home screen on iOS/Android and desktop
- **Offline Support**: Core UI cached; graceful fallback for API calls
- **Fast Loading**: Service worker enables instant startup
- **App Shortcuts**: Quick actions from the home screen
- **File Sharing**: Share audio files directly with VoiceSense via system share menu

---

## 📲 How Users Install VoiceSense

### Android

1. Open VoiceSense in Chrome or Edge
2. Tap the menu (⋮) → "Install app"
3. Confirm installation
4. App now appears on home screen as a native app

### iOS (iPhone/iPad)

1. Open VoiceSense in Safari
2. Tap Share (↑)
3. Tap "Add to Home Screen"
4. Name the shortcut (default: "VoiceSense")
5. Tap "Add" — app now appears on home screen

### Desktop (Windows/Mac/Linux)

1. Open VoiceSense in Chrome, Edge, or Brave
2. Click the install icon in the address bar (or menu)
3. Confirm installation
4. App launches as a standalone window

---

## 🔧 What's Been Added

### Files Created

| File | Purpose |
|---|---|
| `static/manifest.json` | PWA configuration (name, icons, description) |
| `static/js/service-worker.js` | Offline caching, network-first strategy for API |
| `static/icons/icon-192.png` | App icon (192×192) |
| `static/icons/icon-512.png` | App icon (512×512) for splash screen |
| `static/icons/icon-192-maskable.png` | Maskable icon for adaptive display |
| `static/icons/icon-512-maskable.png` | Maskable icon for adaptive display |
| `static/screenshots/screenshot-540.png` | Mobile screenshot (install preview) |
| `static/screenshots/screenshot-1280.png` | Desktop screenshot (install preview) |

### Files Modified

| File | Changes |
|---|---|
| `templates/index.html` | Added PWA meta tags, manifest link, service worker registration |
| `app.py` | Added CORS support, `/manifest.json` route |
| `requirements.txt` | Added `flask-cors>=4.0.0` |

---

## 🚀 Deployment Checklist

### Before Going Live

- [ ] Test on Android (Chrome)
- [ ] Test on iOS (Safari)
- [ ] Test on desktop (Chrome/Edge)
- [ ] Use **HTTPS** (PWAs require secure context)
- [ ] Verify `/manifest.json` loads correctly
- [ ] Check service worker in DevTools (Application → Service Workers)
- [ ] Test offline mode (DevTools → Network → offline)

### HTTPS Requirement

PWAs **only work over HTTPS** (except `localhost`). Before deploying:

```bash
# Render / Railway / Vercel automatically use HTTPS
# For local testing with HTTPS:
python -m pip install pyopenssl
flask run --cert=adhoc
```

---

## 📊 Caching Strategy

### Static Assets (Cache-First)
Files are cached on first load and updated periodically:
- `style.css`
- `manifest.json`
- App icons

### API Calls (Network-First)
Real-time data prioritizes fresh results:
- `/analyze` — Analysis requests
- `/health` — Server health checks

### Fallback
If the network is unavailable and there's no cache:
- Returns a friendly "Network error" message
- Users can retry when back online

---

## 🔌 Service Worker Features

### Automatic Updates

The service worker automatically activates new versions when the app is updated. No manual intervention needed.

### Background Sync (Future Enhancement)

The service worker is prepared for background sync. In a future update, users could:
- Queue audio uploads while offline
- Sync when connectivity returns

### Share Target (Native Share)

Users can share audio files from their device directly with VoiceSense:

```
Share Menu → VoiceSense → Audio file uploaded
```

---

## 🧪 Testing Locally

### 1. Enable Service Worker Registration

```bash
# For HTTPS testing (required for SW registration):
# On macOS/Linux
pip install pyopenssl
flask run --cert=adhoc

# Or use a local HTTPS proxy like mkcert
```

### 2. Check Service Worker Status

1. Open DevTools (F12)
2. Go to **Application** tab
3. Click **Service Workers** in left sidebar
4. Should show: ✅ `service-worker.js` — active and running

### 3. Test Offline Mode

1. In DevTools → **Network** tab
2. Check **"Offline"** checkbox
3. Try uploading (will show "Network error" gracefully)
4. Uncheck "Offline" to reconnect

### 4. Test Installation

1. Open DevTools → **Application** tab
2. Click **Manifest** in left sidebar
3. Verify manifest data loads correctly
4. Look for "Install" button prompt in address bar

---

## 🎨 Customizing Icons

To create custom icons:

1. Design a 512×512 PNG or SVG
2. Use an icon generator (e.g., [PWA Asset Generator](https://tomayac.github.io/pwa-asset-generator/))
3. Replace the icon files in `static/icons/`
4. Update `manifest.json` if needed

For **maskable icons** (adaptive shapes on different devices):
- Keep important content in center ✓
- Extend artwork to edges for flexibility ✓
- Use solid colors for consistency ✓

---

## 🐛 Troubleshooting

### Service Worker Not Registering

```
❌ "Service Worker registration failed"
```

**Solutions:**
- Ensure HTTPS (or localhost)
- Check `/static/js/service-worker.js` loads (200 status)
- Clear cache: DevTools → Application → Clear site data
- Restart the Flask server

### Manifest Not Found

```
❌ 404 on manifest.json
```

**Solutions:**
- Verify file exists: `/static/manifest.json`
- Check Flask route is configured
- Try hard-refresh (Ctrl+Shift+R)

### Icons Not Showing After Install

**Solutions:**
- Use PNG format with transparency
- Ensure icons are exactly 192×192 and 512×512
- Test with maskable icons for better adaptive display
- Clear app cache before reinstalling

### Offline Page Shows Error Instead of UI

**Solutions:**
- Service worker needs HTTPS
- Check DevTools → Application → Cache Storage
- Manually clear all caches and re-register

---

## 📚 Learn More

- [MDN — Progressive Web Apps](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps)
- [Google — PWA Checklist](https://web.dev/pwa-checklist/)
- [Web.dev — Service Workers](https://web.dev/service-workers/)
- [Apple — Web Apps](https://developer.apple.com/library/archive/documentation/AppleApplications/Reference/SafariWebContent/ConfiguringWebApplications/ConfiguringWebApplications.html)

---

## 🎉 Done!

Your VoiceSense app is now a full PWA. Users can install it just like a native app!

**Next Steps:**
1. Deploy to HTTPS (Vercel, Render, Railway, etc.)
2. Share the link with users
3. Users tap "Install" and enjoy the app offline-ready experience

---

*VoiceSense PWA Support — Built for mobile, tablet, and desktop.* 🚀
