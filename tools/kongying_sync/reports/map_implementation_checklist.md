# Kongying Map Implementation Checklist

Edit one character to update status:

- `[x]` = implemented
- `[ ]` = not implemented yet

Keep this checklist boring and literal. If a feature only works with smoke-test fixtures, mark the fixture/prototype line as done and keep the real-data line unchecked.

## Official Map Sync

- [x] Fetch latest public Kongying `webapp.json` from `https://assets.yuanshen.site/webapp.json`.
- [x] Save public map snapshot to `tools/kongying_sync/data/webapp.json`.
- [x] Generate compact map/layer summary at `tools/kongying_sync/data/map_summary.json`.
- [x] Generate official source/probe report at `tools/kongying_sync/reports/live_map_sync_report.md`.
- [x] Cross-reference official Kongying docs, changelog, web changelog, and hot-update logs.
- [x] Treat Kongying GitHub as source/dev reference only, not guaranteed live data.
- [x] Record API probe results for official live endpoints.
- [x] Clearly report `401 requires authorization` for auth-gated marker/item/icon APIs.

## Public Map Areas Present

- [x] Main Teyvat base tile config.
- [x] Secondary/special base tile config.
- [x] Golden Apple base tile config.
- [x] Golden Apple 1.6 event map.
- [x] Golden Apple 2.8 event map.
- [x] Veluriyam Mirage 3.8 event map.
- [x] Simulanka 4.8 event map.
- [x] Mondstadt public region entry.
- [x] Dragonspine public region entry.
- [x] Favonius Knights ruin / 6.5 public region entry.
- [x] Sky Temple / `A:MD:SHENDIAN` public region entry.
- [x] Liyue public region entry.
- [x] The Chasm surface public region entry.
- [x] The Chasm underground public region entry.
- [x] Chenyu Vale public region entry.
- [x] Inazuma public region entries.
- [x] Tsurumi Island public region entry.
- [x] Enkanomiya public region entry.
- [x] Three Realms Gateway Offering public region entry.
- [x] Sumeru forest public region entry.
- [x] Sumeru desert public region entries.
- [x] Fontaine public region entries.
- [x] Sea of Bygone Eras / Ancient Sea public region entry.
- [x] Natlan 5.0 public region entry.
- [x] Natlan 5.2 public region entry.
- [x] Natlan 5.5 public region entries.
- [x] Ancient Sacred Mountain public region entry.
- [x] Natlan 5.8 public region entry.
- [x] Nod-Krai 6.0 public region entry.
- [x] Nod-Krai 6.3 public region entry.

## Public Layered Map Coverage Present

- [x] 6.5 layered metadata for `A:MD:FENGXISHAN`.
- [x] 6.5 layered metadata for `A:MD:SHENDIAN`.
- [x] 6.3 layered metadata for `A:NDKL:NDKL2`.
- [x] 6.2 public underground resource reference in Nod-Krai overlay data.
- [x] 6.0 Nod-Krai layered metadata.
- [x] `LEMPO_ISLAND` layered metadata.
- [x] `HIISI_ISLAND` layered metadata.
- [x] `PAHA_ISLE` layered metadata.
- [x] 5.8 Natlan layered metadata.
- [x] 5.5 Natlan layered metadata.
- [x] 5.2 Natlan layered metadata.
- [x] 5.0 Natlan layered metadata.
- [x] 4.8 Simulanka layered metadata.
- [x] 4.6 Fontaine/Ancient Sea layered metadata.
- [x] 4.4 Chenyu Vale layered metadata.
- [x] 4.2 Fontaine layered metadata.
- [x] 4.1 Fontaine layered metadata.
- [x] 4.0 Inazuma/Sumeru/Fontaine layered metadata.

## Auth-Gated Kongying Data

- [ ] Import official area tree from `/area/get/list`.
- [ ] Import official item type list from `/item_type/get/list_all`.
- [ ] Import official item list from `/item/get/list`.
- [ ] Import official icon list from `/icon/get/list`.
- [ ] Import official marker document hashes/data from `/marker_doc/list_page_bin_md5`.
- [ ] Import full chest coordinates.
- [ ] Import full oculus coordinates.
- [ ] Import full resource coordinates.
- [ ] Import challenge, quest, teleport, and special marker coordinates.
- [ ] Import marker detail text, images, route links, and video links.
- [ ] Import live item counts by region/category.
- [ ] Add a local-only authenticated export or client-cache importer.
- [ ] Add safeguards that reject token, cookie, session, or account fields from imported files.

## Runtime Map Tooling

- [ ] Public tile downloader/cache for tile URL templates.
- [ ] Map-region index from `areaKey` to tile config.
- [ ] Overlay/layer index from `areaKey` to underground/variant metadata.
- [ ] Layer selector model for normal map, underground map, and overlay variants.
- [ ] Snapshot diff tool for old/new `webapp.json`.
- [ ] Report added/removed tile keys during map updates.
- [ ] Report added/removed overlay labels/values during map updates.
- [ ] Report changed tile URL templates and layer resource versions.

## Marker And Pin Tooling

- [ ] Normalized pin schema for real Kongying markers.
- [ ] Marker schema validator.
- [ ] Coordinate validation.
- [ ] `areaKey` validation against `data/map_summary.json`.
- [ ] Chest/oculus category normalization from Kongying item types.
- [ ] Marker dedupe across Kongying data refreshes.
- [ ] Marker migration logic for changed Kongying ids or categories.
- [ ] Nearest-pin index backed by imported Kongying pins.
- [ ] Nearest-pin filter by current `areaKey`.
- [ ] Nearest-pin filter by active or nearby layer.
- [x] Nearest-pin smoke-test fixture logic.
- [x] Low-confidence nearest-pin result stays `needs_review`.

## Screenshot Reward Detector

- [x] Screenshot-only capture module.
- [x] Center/middle reward ROI crop.
- [x] Configurable/scalable ROI.
- [x] Primogem/reward template loading.
- [x] Blank image returns no detection.
- [x] Saved synthetic Primogem/reward sample returns positive detection.
- [x] Debug `last_detection.json` output.
- [x] Debug reward ROI screenshot output.
- [x] Safety note: no game memory reads.
- [x] Safety note: no DLL injection.
- [x] Safety note: no game-file modification.
- [x] Safety note: no gameplay automation.
- [x] Safety note: no account upload.

## Detector Plus Map Position

- [x] One-shot detector accepts explicit `--position`.
- [x] One-shot detector accepts `--position-json`.
- [x] One-shot detector combines detection with smoke-test pins.
- [x] High-confidence result becomes `auto_mark_candidate`, not direct irreversible marking.
- [x] Low-confidence result becomes `needs_review`.
- [ ] Live cvAutoTrack/Kongying position bridge.
- [ ] Live active `areaKey` detection.
- [ ] Live active layer detection.
- [ ] Real imported Kongying pins connected to detector.
- [ ] Chest reward detection prefers nearby chest pins from real data.
- [ ] Oculus pickup/reward-like detection prefers nearby oculus pins from real data.
- [ ] Review queue file or UI for uncertain detections.
- [ ] Local reversible marker update workflow.

## Smoke Tests

- [x] Kongying sync smoke test passes.
- [x] Reward detector smoke tests pass.
- [x] Detector loads templates.
- [x] Detector returns no detection on blank image.
- [x] Detector returns positive on saved Primogem/reward sample image.
- [x] Nearest-pin fixture chooses closest chest/oculus candidate.
- [x] Low confidence does not auto-mark.
- [x] Debug logs/screenshots are saved.
- [ ] Imported real-marker schema tests.
- [ ] Token/account-field rejection tests.
- [ ] Nearest-pin real-data area/layer tests.
- [ ] Snapshot diff tests.

## Knowledge Gaps To Resolve

Check these only when the unknown is answered and documented.

- [ ] Exact authenticated response schema for `/area/get/list` is known.
- [ ] Exact authenticated response schema for `/item_type/get/list_all` is known.
- [ ] Exact authenticated response schema for `/item/get/list` is known.
- [ ] Exact authenticated response schema for `/icon/get/list` is known.
- [ ] Exact authenticated response schema for `/marker_doc/list_page_bin_md5` is known.
- [ ] Safe local source for Kongying marker data is chosen: official export, local client cache, or allowed local token flow.
- [ ] Kongying Windows client cache/export file locations are known.
- [ ] Kongying Windows client cache/export file formats are known.
- [ ] Kongying marker coordinate system is mapped to our `MapPosition` coordinates.
- [ ] Coordinate transforms are verified per major map family: Teyvat, event maps, underground maps, and layered overlays.
- [ ] Active `areaKey` source is known for live use.
- [ ] Active layer source is known for live use.
- [ ] Pin id stability across Kongying hot updates is known.
- [ ] Marker completion/update format is known if we later want to write reversible local suggestions back to a map file.
- [ ] Chest item type ids/names are known from official data.
- [ ] Oculus item type ids/names are known from official data.
- [ ] Reward-bearing non-chest item categories are known from official data.
- [ ] Respawnable versus one-time marker rules are known from official data.
- [ ] Live item counts by region/category are available from an allowed source.
- [ ] Exact meaning of 2026-01-14 "Moon IV" resource update is known.
- [ ] Whether "Moon IV" resources are public tile/layer data or auth-gated marker/item data is known.
- [ ] Reward popup visual variants are collected for common resolutions.
- [ ] Reward popup visual variants are collected for supported UI languages.
- [ ] Oculus pickup/reward visual pattern is verified from screenshot/video references.
- [ ] Primogem reward crop bounds are calibrated with real gameplay screenshots, not only synthetic fixtures.
- [ ] Kongying API rate limits and acceptable local use constraints are known.
- [ ] Importer redaction rules are verified against real export/cache samples without storing account data.
- [ ] Minimum data needed for 100% map parity is documented as a concrete file/table list.

## Current Claim

- [x] Public Kongying map/layer shell is current from official public config.
- [ ] Live Kongying pins/items/markers are 100% current.
- [ ] Full chest/oculus completion helper is ready for real imported Kongying marker data.
- [ ] Make the Chest/ Anemo Primogem Detector working with the new map implementation.