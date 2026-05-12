# Kongying Live Map Sync

This folder stores a reproducible snapshot of Kongying's official public map
configuration.

```bash
python3 -m tools.kongying_sync.sync_live_map
python3 -m pytest tools/kongying_sync/smoke_tests -q
```

What is synced:

- `data/webapp.json`: latest public `https://assets.yuanshen.site/webapp.json`.
- `data/map_summary.json`: compact list of tile regions, plugin configs, layered maps, and latest-term coverage.
- `reports/live_map_sync_report.md`: source/coverage/blocker report.
- `reports/map_implementation_rundown.md`: present/missing map areas and the implementation checklist.
- `reports/map_implementation_checklist.md`: checkbox-only implementation status list.

The report cross-references Kongying's official docs/changelogs first:

- Chinese client changelog and hot-update log for current resource/layer notes.
- Chinese web changelog for web map point/icon API changes.
- English docs/home page as general product documentation.
- Kongying GitHub only as source/dev reference, not as guaranteed live data.

Important limit:

The official marker/item/icon API endpoints require a Kongying bearer token.
Without an official authenticated export or local client cache, this repo can
sync public map/layer config but cannot honestly claim 100% live marker/pin
parity.
