# Kongying Live Map Sync Report

## Official Sources
- Public webapp config: https://assets.yuanshen.site/webapp.json
- Live API base: https://cloud.yuanshen.site/api
- Docs EN: https://yuanshen.site/docs/en/
- Docs ZH: https://yuanshen.site/docs/
- Client changelog: https://yuanshen.site/docs/blog/posts/changelog-client
- Hot update log: https://yuanshen.site/docs/blog/posts/hotupdatelog-client
- Web changelog: https://yuanshen.site/docs/blog/posts/changelog-web
- GitHub org: https://github.com/kongying-tavern (source/dev reference only)

## Synced Public Config
- Tiles: 36
- Plugin configs: 33

## Latest-Term Coverage
- A:MD:SHENDIAN: present
- A:MD:FENGXISHAN: present
- 空之神殿: present
- 远古圣山: present
- FAVONIUS_KNIGHT_RUIN: present
- https://tiles.yuanshen.site/d/underground/6.5/: present
- https://tiles.yuanshen.site/d/underground/6.3/: present
- https://tiles.yuanshen.site/d/underground/6.2/: present
- https://tiles.yuanshen.site/d/underground/6.0/: present
- 伦波岛: present
- 希汐岛: present
- 帕哈岛: present
- HIISI_ISLAND: present
- LEMPO_ISLAND: present
- PAHA_ISLE: present
- A:NDKL:NDKL: present
- A:NDKL:NDKL2: present

## Official Log Cross-Reference
- 2026-04-07 hotfix-2026-04-07-6.5: covered
  - Source: https://yuanshen.site/docs/blog/posts/hotupdatelog-client
  - Note: Kongying hot update says 6.5 resources and some base-map resources were updated.
- 2026-04-08 hotfix-2026-04-08-sky-temple-library: covered
  - Source: https://yuanshen.site/docs/blog/posts/hotupdatelog-client
  - Note: Kongying hot update says Sky Temple library layered resources were updated.
- 2026-04-09 hotfix-2026-04-09-ancient-sacred-mountain: covered
  - Source: https://yuanshen.site/docs/blog/posts/hotupdatelog-client
  - Note: Kongying hot update references Ancient Sacred Mountain cloud/resource fixes.
- 2025-12-03 client-2025-12-03-6.2-layer: covered
  - Source: https://yuanshen.site/docs/blog/posts/changelog-client
  - Note: Kongying client changelog says one 6.2 underground layer was added.
- 2025-09-10 hotfix-2025-09-10-6.0-nod-krai: covered
  - Source: https://yuanshen.site/docs/blog/posts/hotupdatelog-client
  - Note: Kongying hot update says 6.0 regions/resources were added.
- 2025-09-10 web-2025-09-10-nod-krai-icon: covered
  - Source: https://yuanshen.site/docs/blog/posts/changelog-web
  - Note: Kongying web changelog says the Nod-Krai icon was added.
- 2025-07-29 hotfix-2025-07-29-5.8: covered
  - Source: https://yuanshen.site/docs/blog/posts/hotupdatelog-client
  - Note: Kongying hot update says 5.8 regions/resources were added.

## Auth-Gated Map/Item Signals
- 2026-01-06 web-2026-01-06-new-point-api: needs authenticated export/API access
  - Source: https://yuanshen.site/docs/blog/posts/changelog-web
  - Note: Kongying web changelog says point acquisition now supports the new point data API.
- 2026-01-14 hotfix-2026-01-14-moon-four-resources: needs authenticated export/API access
  - Source: https://yuanshen.site/docs/blog/posts/hotupdatelog-client
  - Note: Kongying hot update says Moon IV related resources were updated; these are not exposed in public webapp tile config.
- latest live-marker-item-icon-export: needs authenticated export/API access
  - Source: https://cloud.yuanshen.site/api
  - Note: Chest, oculus, item, icon, and marker parity requires official marker/item/icon endpoints or an official client cache/export.

## API Probe Results
- area.list POST /area/get/list: 401 (requires authorization)
- item_type.list_all POST /item_type/get/list_all: 401 (requires authorization)
- item.list POST /item/get/list: 401 (requires authorization)
- icon.list POST /icon/get/list: 401 (requires authorization)
- marker_doc.md5 GET /marker_doc/list_page_bin_md5: 401 (requires authorization)

## Verification Limit
Public webapp tile/layer config was synced. Full item/pin/marker parity cannot be claimed without an official authenticated export or client cache, because live API read endpoints returned authorization errors without a bearer token.

## Update Checklist
- Treat `data/webapp.json` as the latest public official tile/layer config snapshot.
- Use `data/map_summary.json` for region/layer comparison in tools.
- For 100% marker/item/pin parity, import an official authenticated export or local client cache; do not infer live pins from GitHub alone.
- Re-run this tool with `KONGYING_TOKEN` only if you have an official token you are allowed to use locally.
- After importing authenticated marker data, rerun nearest-pin smoke tests against the exported chest/oculus candidate set.
