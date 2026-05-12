# Kongying Map Implementation Rundown

Generated from the current official public Kongying snapshot in `tools/kongying_sync/data/webapp.json` and the API probe report in `tools/kongying_sync/reports/live_map_sync_report.md`.

For quick status edits, use `tools/kongying_sync/reports/map_implementation_checklist.md`. Flip `[ ]` to `[x]` when an item is implemented.

## Current Status

This repo now has Kongying's latest public map shell:

- 36 tile configs.
- 33 plugin configs.
- Public base maps, event maps, region maps, and layered-map overlay metadata.
- Official public coverage for 5.8, 6.0, 6.2, 6.3, and 6.5 layered resources.

This repo does not yet have Kongying's live marker database:

- Chest pins.
- Oculus pins.
- Resource pins.
- Item/type/category definitions.
- Marker detail docs/images/videos.
- Icon metadata.
- Authenticated area/item/marker exports.

The missing live marker pieces are not public in `webapp.json`. The live Kongying API endpoints currently return `401 requires authorization` without an official bearer token or client cache/export.

## Present Public Map Areas

These map entries are present in `data/webapp.json`.

| Key | Public label | Notes |
| --- | --- | --- |
| `提瓦特-base0` | 提瓦特 | Main Teyvat base tile set. |
| `提瓦特-base1` | unnamed base | Secondary/special base tile set. |
| `金苹果-base0` | unnamed base | Golden Apple base tile set. |
| `A:APPLE:1_6` | 金苹果群岛(1.6) | Event map with overlay states. |
| `A:APPLE:2_8` | 金苹果群岛(2.8) | Event map with overlay states. |
| `A:VELURIYAM:3_8` | 琉形蜃境 | Event map, underground-capable. |
| `A:SIMULANKA:4_8` | 希穆兰卡 | Event map with 4.8 underground overlays. |
| `A:MD:MENGDE` | Mondstadt region entry | Public tile config present. |
| `A:MD:XUESHAN` | Dragonspine region entry | Public tile config present. |
| `A:MD:FENGXISHAN` | Favonius Knights ruin area | 6.5 underground overlays present. |
| `A:MD:SHENDIAN` | 空之神殿 | 6.5 underground overlays present. |
| `A:LY:LIYUE` | Liyue region entry | Public tile config present. |
| `A:LY:CENGYAN` | The Chasm surface entry | Public tile config present. |
| `A:LY:CENGYAN_UG` | 地下矿区 | Underground Chasm entry present. |
| `A:LY:CHENYUGU` | Chenyu Vale entry | 4.4 underground overlays present. |
| `A:DQ:1` | Inazuma entry | 4.0 underground overlays present. |
| `A:DQ:2` | Inazuma entry | Public tile config present. |
| `A:DQ:HEGUAN` | Tsurumi Island entry | 4.0 underground overlays present. |
| `A:DQ:YUANXIAGONG` | 渊下宫/三界路飨祭 | Enkanomiya entry present. |
| `A:DQ:SANJIE` | 渊下宫/三界路飨祭 | Three Realms Gateway Offering entry present. |
| `A:XM:FOREST` | Sumeru forest entry | 4.0 underground overlays present. |
| `A:XM:DESERT` | Sumeru desert entry | 4.0 underground overlays present. |
| `A:XM:DESERT2` | Sumeru desert entry | 4.0 underground overlays present. |
| `A:XM:DESERT3` | Sumeru desert entry | 4.0 underground overlays present. |
| `A:FD:FENGDAN` | Fontaine entry | 4.0 underground overlays present. |
| `A:FD:FENGDAN2` | Fontaine entry | 4.1 underground overlays present. |
| `A:FD:FENGDAN3` | Fontaine entry | 4.2 underground overlays present. |
| `A:FD:FENGDAN4` | Fontaine entry | 4.6 underground overlays present. |
| `A:FD:ANCIENT_SEA` | 旧日之海 | 4.6 underground overlays present. |
| `A:NT:NATA` | Natlan entry | 5.0 underground overlays present. |
| `A:NT:NATA2` | Natlan entry | 5.2 underground overlays present. |
| `A:NT:NATA3` | Natlan entry | 5.5 underground overlays present. |
| `A:NT:NATA4` | 远古圣山 | 5.5 underground overlays present. |
| `A:NT:NATA5` | Natlan 5.8 entry | 5.8 underground overlays present. |
| `A:NDKL:NDKL` | Nod-Krai 6.0 entry | Lempo, Hiisi, Paha, and 6.0 overlays present. |
| `A:NDKL:NDKL2` | Nod-Krai 6.3 entry | 6.3 overlays present. |

## Present Layered Map Coverage

The public config includes layered/underground metadata for these newer areas:

- 6.5: `A:MD:FENGXISHAN`, `A:MD:SHENDIAN`.
- 6.3: `A:NDKL:NDKL2`.
- 6.2: at least one public underground resource referenced in the 6.0 Nod-Krai overlay data.
- 6.0: `A:NDKL:NDKL`, including `LEMPO_ISLAND`, `HIISI_ISLAND`, and `PAHA_ISLE`.
- 5.8: `A:NT:NATA5`.
- 5.5: `A:NT:NATA3`, `A:NT:NATA4`.
- 5.2: `A:NT:NATA2`.
- 5.0: `A:NT:NATA`.
- 4.8: `A:SIMULANKA:4_8`.
- 4.6: `A:FD:FENGDAN4`, `A:FD:ANCIENT_SEA`.
- 4.4: `A:LY:CHENYUGU`.
- 4.2: `A:FD:FENGDAN3`.
- 4.1: `A:FD:FENGDAN2`.
- 4.0: Inazuma, Sumeru, and Fontaine layered resources.

## Missing Or Not Yet Implemented

### Missing Because Official APIs Are Auth-Gated

These should not be guessed from GitHub or scraped from unofficial mirrors:

- Area tree from `/area/get/list`.
- Item type list from `/item_type/get/list_all`.
- Item list from `/item/get/list`.
- Icon list from `/icon/get/list`.
- Marker document hashes/data from `/marker_doc/list_page_bin_md5`.
- Full chest, oculus, challenge, resource, quest, teleport, and special marker coordinates.
- Marker detail text, images, route links, and video links.
- Live item counts by region and category.

Implementation need: add a local-only importer that accepts either an official authenticated export or a local Kongying client cache. Do not store account data or tokens in the repo.

### Missing In Our Tooling

The repo has the data snapshot, but these runtime features are not implemented yet:

- Tile downloader/cache for the public tile URL templates.
- Map-region index that resolves `areaKey -> tile config -> overlay config`.
- Layer selector model for normal map, underground map, and overlay variants.
- Pin schema for normalized chest/oculus/resource marker data.
- Authenticated/local cache importer for Kongying marker data.
- Marker dedupe and migration logic across Kongying data refreshes.
- Nearest-pin index backed by live Kongying pins instead of smoke-test pins.
- Chest/oculus category mapping from Kongying item types to reward-detector candidates.
- Confidence rules that combine reward detection, current position, active layer, and nearby candidate pins.
- Review queue UI/file for uncertain detections.
- Map update command that regenerates the snapshot and compares it against the previous snapshot.

## What To Implement Next

1. Add a Kongying marker import path.
   - Input: local JSON/cache/export only.
   - Output: normalized `pins.json` or sqlite table.
   - Must include `id`, `areaKey`, `itemType`, `itemName`, `x`, `y`, optional `layer`, `isRespawnable`, and `sourceVersion`.

2. Add a marker schema validator.
   - Validate coordinates are numeric.
   - Validate `areaKey` exists in `data/map_summary.json`.
   - Validate chest/oculus categories map to reward-detector candidate types.
   - Reject files containing session tokens, cookies, or account identifiers.

3. Build a nearest-pin index from imported pins.
   - Replace smoke-test pins with imported Kongying pins.
   - Filter by current `areaKey` and active/nearby layer.
   - Prefer chest pins after Primogem reward detection.
   - Prefer oculus pins after oculus/reward-like pickup detection.

4. Integrate map position and layer context.
   - Use screenshot/cvAutoTrack-style position only.
   - Store current `areaKey`, coordinates, and optional layer.
   - Never read game memory or automate gameplay.

5. Add a local review queue.
   - High confidence: suggest completion, but keep it local and reversible.
   - Medium/low confidence: write `needs_review`.
   - Include cropped reward screenshot, candidate pin list, position, layer, and score.

6. Add snapshot diff tooling.
   - Compare old/new `webapp.json`.
   - Report added/removed tile keys.
   - Report added/removed overlay labels/values.
   - Report changed tile URL templates and layer resource versions.

7. Add smoke tests for imported real marker shape.
   - Loads sample imported pins.
   - Rejects token/account fields.
   - Maps chest/oculus item types correctly.
   - Nearest-pin query respects area and layer.
   - Low confidence still does not auto-mark.

## Practical Definition Of "100% Updated"

Use this checklist before claiming the helper is current:

- Public `webapp.json` refreshed from Kongying official assets.
- Public map summary regenerated.
- Official changelog/hot-update entries cross-referenced.
- API probes recorded.
- Auth-gated marker data imported from an allowed local source.
- Chest/oculus/item categories normalized.
- Nearest-pin smoke tests pass on imported data.
- Reward detector smoke tests pass.
- Debug logs/screenshots are written locally.
- No game memory, DLL injection, game-file modification, gameplay automation, token storage, or account upload.

Current state: public map/layer shell is current; live pins/items/markers still need the authenticated/local import path.
