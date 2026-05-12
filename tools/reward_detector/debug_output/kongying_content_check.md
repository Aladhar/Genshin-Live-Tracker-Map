# Kongying Content Check

## Sources
- Kongying docs: https://yuanshen.site/docs/en/ (official product/docs source)
- Client hot update log: https://yuanshen.site/docs/en/blog/posts/hotupdatelog-client (official client/map/resource hot updates)
- Client release notes: https://yuanshen.site/docs/en/blog/posts/changelog-client (official client release notes)
- Kongying GitHub org: https://github.com/kongying-tavern (source/dev reference only)
- cvAutoTrack: https://github.com/GengGode/cvAutoTrack (source/dev reference for screenshot-only tracking)

## Local Term Scan
- Hiisi Island: present (2025-09-10-35 hot update)
- Lempo Isle: present (2025-09-10-35 hot update)
- Paha Isle: present (2025-09-10-35 hot update)
- Easybreeze Holiday Resort: present (2025-07-29-848 hot update)
- version 5.6: present (2025-05-07-118 hot update)
- layered map: present (web/client logs)
- chest: present (map item categories)
- oculus: present (map item categories)

## Update Checklist
- Fetch/export live Kongying area, item, icon, marker, and tile/plugin config data from official endpoints or client cache.
- Compare live export against local source tree before editing vendored repos.
- Verify newest areas include maps, layered maps, resources, chests, oculi, and hot-update metadata.
- Use GitHub repositories only to understand schemas and source behavior; do not treat repo age as live-data freshness.
- Keep any marker completion writes local/reviewable unless detection confidence is high.
