# macOS Single-App Roadmap

English client target: one macOS app that opens into the interactive Genshin map and can optionally attach to the running Genshin Impact window for live position tracking.

This roadmap uses the Kongying Tavern Interactive Map app and web version as the product reference. Use the reference for feature behavior and UX expectations only. Do not ship Kongying Tavern names, logos, landing images, or branding assets unless explicit written permission exists; `external/docs/COPYING.md` says those branding elements are prohibited in forks.

## Product Goal

- [x] Use `external/map_front_v3` as the user-facing map base.
- [x] Use the English app/web experience as the target, not the admin/back-office tooling.
- [x] Treat `external/map_register_v3` as an internal marker management app; do not bundle it in the first macOS client.
- [x] Treat `external/docs` as reference documentation; do not bundle the docs site in the first macOS client.
- [ ] Ship `Genshin Live Tracker & Map.app` as one app bundle.
- [ ] App launches directly into the English interactive map.
- [ ] App contains the local native tracker, cache data, and web assets.
- [ ] User should not need to run terminal scripts after install, except during developer builds.
- [ ] First-run UI explains macOS Screen Recording permission and tracker readiness in English.

## Current Status

- [x] `bash build-macos.sh --install-vcpkg --run-smoke-test` builds the native tracker stack on this Mac.
- [x] `external/cvAutoTrack/build-macos/lib/libcvAutoTrack.dylib` exists.
- [x] `external/cvAutoTrack/build-macos/bin/macos_capture_probe` exists.
- [x] `external/cvAutoTrack/build-macos/bin/genshin_tracker_macos` exists as a runnable tracker CLI.
- [x] `script/build_and_run.sh` builds and runs the tracker CLI status check.
- [x] The macOS probe can enumerate windows through Core Graphics when run outside the sandbox.
- [x] The probe found a `Genshin Impact` window during local testing.
- [ ] Screen Recording permission still needs to be granted to the terminal or app doing capture.
- [ ] The probe has not yet saved a valid Genshin capture after permission approval.
- [ ] `cvAutoTrack_Cache.dat` is not present in this repository; full tracking will fail until the cache is bundled or downloaded.
- [ ] The web map is not yet wrapped into a macOS app shell.
- [ ] The web map is not yet connected to `cvAutoTrack`.

## What Ships In The First App

| Component | Source | Ship in app? | Purpose |
| --- | --- | --- | --- |
| English map UI | `external/map_front_v3` | Yes | Interactive map, layers, markers, completion UI |
| Native tracker | `external/cvAutoTrack` | Yes | Capture game window and compute player position |
| Tracker host | New app-side module | Yes | Stable bridge between UI and `libcvAutoTrack.dylib` |
| Tracker cache | `cvAutoTrack_Cache.dat` or downloaded asset | Yes | Required matching data for cvAutoTrack |
| App shell | New Tauri or native wrapper | Yes | Single `.app`, menus, permissions, packaging |
| Admin marker editor | `external/map_register_v3` | No | Back-office marker authoring, not end-user app |
| Java backend | `external/genshin-map-cloud` if needed | No for v1 | Cloud sync/login server, not local app core |
| Python tools | `external/*_detector`, sync scripts | No for v1 | Optional tooling, not needed for single app launch |
| Docs site | `external/docs` | No | Reference docs and feature model |

## App Shell Decision

- [ ] Pick the wrapper before frontend integration. Recommended: Tauri.
- [ ] Use Tauri because it produces a smaller native macOS bundle, can call Rust commands, can ship sidecars/resources, and has normal macOS signing/notarization paths.
- [ ] Keep Electron as fallback only if the web map depends on browser APIs that Tauri WebView cannot support.
- [ ] Set bundle identity, app name, icon, and version for the English app.
- [ ] Configure bundled resources:
  - `external/map_front_v3/dist/spa`
  - `libcvAutoTrack.dylib`
  - tracker host executable or Tauri Rust commands
  - `cvAutoTrack_Cache.dat`
  - any required map/static assets
- [ ] Configure runtime paths so native code can load bundled dylibs from inside the `.app`.
- [ ] Add hardened runtime/signing settings before public distribution.
- [ ] Notarize only for distributable builds; local debug builds do not need notarization.

## Step 0: Prove macOS Capture First

Do this before building the app shell. If capture does not work, the app can still show the map, but live tracking cannot work.

- [x] Build native artifacts:

```bash
bash build-macos.sh --install-vcpkg --run-smoke-test
```

- [x] Confirm probe binary exists:

```bash
external/cvAutoTrack/build-macos/bin/macos_capture_probe --list
```

- [x] Confirm tracker CLI binary exists:

```bash
external/cvAutoTrack/build-macos/bin/genshin_tracker_macos --status
```

- [x] Developer run wrapper:

```bash
script/build_and_run.sh
```

- [ ] Grant Screen Recording permission to the terminal or app running the probe:

```bash
external/cvAutoTrack/build-macos/bin/genshin_tracker_macos --request-permission
```

- [ ] If macOS opens System Settings, enable Screen Recording or Screen & System Audio Recording for the current terminal app, then quit and reopen that terminal/app.
- [ ] Capture a real frame:

```bash
external/cvAutoTrack/build-macos/bin/genshin_tracker_macos --capture Capture-macos.png
```

- [ ] Verify `Capture-macos.png` shows the game window and minimap clearly.
- [ ] If capture is blank, re-check permission, window selection, fullscreen mode, and Retina scaling.

## Step 1: Build The English Web Map

- [ ] Install frontend dependencies:

```bash
cd external/map_front_v3
corepack enable
pnpm install
```

- [ ] Build the production web app:

```bash
pnpm build
```

- [ ] Verify the build output, expected from Quasar as `external/map_front_v3/dist/spa`.
- [ ] Set English as the default locale using `external/map_front_v3/src/i18n/en-US/index.js` and the app i18n boot path.
- [ ] Replace product name, favicon, icons, and visible branding with this app's English branding.
- [ ] Audit API endpoints in `external/map_front_v3/src/service` and `external/map_front_v3/src/api`.
- [ ] Decide for v1 whether login/cloud sync is disabled, local-only, or connected to a hosted service.
- [ ] Keep map features that already exist in the web app: layers, marker filters, completion state, batch actions, route/planning tools if present.

## Step 2: Create The Single macOS App

- [ ] Create a new app wrapper project, recommended path: `apps/macos`.
- [ ] Configure it to load `external/map_front_v3/dist/spa` in production.
- [ ] Configure dev mode to load the Quasar dev server for fast UI iteration.
- [ ] Set the app name to `Genshin Live Tracker & Map`.
- [ ] Add app menu items: About, Settings, Check for Tracker, Quit.
- [ ] Add settings storage under macOS Application Support.
- [ ] Bundle native resources inside the app, not beside it:
  - `Contents/Frameworks/libcvAutoTrack.dylib`
  - `Contents/Resources/cvAutoTrack_Cache.dat`
  - tracker host if implemented as a sidecar executable
- [ ] Add a first-run tracker setup screen inside the app.
- [ ] Add a debug action to open the latest capture/log folder.

## Step 3: Build The Tracker Host API

The web map should not call `cvAutoTrack` directly. Add a small native bridge that owns permissions, window handles, logging, and library calls.

- [ ] Load `libcvAutoTrack.dylib` from the app bundle.
- [ ] Set log path with `SetLogFilePath` into Application Support.
- [ ] Set cache path/name with `SetTrackCachePath` and `SetTrackCacheName`.
- [ ] Initialize resources with `InitResource`.
- [ ] Select capture mode for macOS through the new Core Graphics/ScreenCaptureKit path.
- [ ] Bind selected Genshin window using `SetCaptureHandle`.
- [ ] Provide app-facing commands:
  - `tracker.status`
  - `tracker.listWindows`
  - `tracker.requestScreenPermission`
  - `tracker.selectWindow`
  - `tracker.debugCapture`
  - `tracker.getPosition`
  - `tracker.getAllInfo`
  - `tracker.getLastError`
- [ ] Return English error messages for common failures:
  - Screen Recording permission missing
  - Genshin window not found
  - tracker cache missing
  - minimap not visible
  - capture produced a blank frame
- [ ] Poll position through `GetAllInfo` or use `StartServer` and `SetServerCallback` if the callback path is stable.
- [ ] Stop cleanly with `StopServer` and `UnInitResource` when the app exits.

## Step 4: Connect Tracker To The Map UI

- [ ] Add a compact tracker panel to the map UI.
- [ ] Show permission state, selected game window, cache state, and last tracker error.
- [ ] Add an `Enable Live Tracking` toggle.
- [ ] Add a `Capture Test` button that calls `tracker.debugCapture`.
- [ ] Add a live player marker layer on the map.
- [ ] Update marker position from tracker coordinates and `mapId`.
- [ ] Show UID/direction/rotation only after the native tracker returns valid values.
- [ ] Keep tracking optional so the map remains useful when Genshin is closed.
- [ ] Store tracker preferences locally.

## Step 5: Add Overlay And Always-On-Top Later

Overlay mode is part of the Kongying-style client experience, but it should come after normal app-window tracking works.

- [ ] Add a second transparent or compact overlay window.
- [ ] Support always-on-top behavior.
- [ ] Let the user toggle overlay from the main app.
- [ ] Keep overlay controls minimal: show/hide, opacity, lock, quit.
- [ ] Verify overlay does not break capture permissions or game focus.

## Step 6: Package, Sign, And Notarize

- [ ] Build frontend assets.
- [ ] Build `libcvAutoTrack.dylib` for the target architecture.
- [ ] Copy all native libraries and cache data into the `.app` bundle.
- [ ] Validate bundle structure:

```bash
find "Genshin Live Tracker & Map.app" -maxdepth 4 -type f
```

- [ ] Verify linked libraries:

```bash
otool -L "Genshin Live Tracker & Map.app/Contents/Frameworks/libcvAutoTrack.dylib"
```

- [ ] Sign nested dylibs, sidecars, and the main app.
- [ ] Enable hardened runtime for distribution builds.
- [ ] Test a signed app before notarization.
- [ ] Notarize and staple for public distribution.
- [ ] Package as `.dmg` or `.zip`.

## Step 7: Test Matrix

- [ ] Apple Silicon debug build launches.
- [ ] Intel build or universal build decision is documented.
- [ ] App launches without terminal scripts.
- [ ] English map loads from bundled assets.
- [ ] User can grant Screen Recording permission to the app bundle.
- [ ] App lists running windows.
- [ ] App finds Genshin Impact.
- [ ] Capture test saves a visible game screenshot.
- [ ] Tracker cache is found.
- [ ] Live marker moves on the map.
- [ ] App handles game not running without crashing.
- [ ] App handles permission denied without crashing.
- [ ] Signed app launches on a clean macOS user account.
- [ ] Notarized package opens without Gatekeeper warnings.

## Immediate Next Build Order

1. Finish Screen Recording permission and prove `genshin_tracker_macos --capture Capture-macos.png`.
2. Add or fetch `cvAutoTrack_Cache.dat`; verify `genshin_tracker_macos --once --cache /path/to/cvAutoTrack_Cache.dat` can initialize with it.
3. Build `external/map_front_v3` and force English defaults.
4. Create `apps/macos` Tauri wrapper and load the map build.
5. Add tracker host commands around `libcvAutoTrack.dylib`.
6. Add the tracker panel and live marker to the map UI.
7. Package the app bundle and run signing/notarization checks.

## Not Ready To Ship Until

- [ ] A real Genshin capture succeeds from the app bundle, not just from a terminal.
- [ ] `cvAutoTrack_Cache.dat` is present and loaded from Application Support or bundled resources.
- [ ] `GetAllInfo` or equivalent returns real coordinates on macOS.
- [ ] The English map UI can run fully from bundled static assets.
- [ ] The app has clear permission, missing-cache, and no-window states.
- [ ] Branding has been replaced or explicitly authorized.

**Last Updated**: May 14, 2026  
**Status**: Native build works; single-app integration not started.
