# English Localization Plan

Goal: keep the tracker and map usable in English while preserving KongYing as the upstream data source.

## Scope

Translate these layers:

- Map UI text: buttons, filters, panels, settings, error messages, tooltips.
- Map regions and tile groups: `MainMap`, Chasm, event maps, overlays, underground maps.
- Marker/item/category names: chests, specialties, materials, ores, monsters, activities, food, housing, lore.
- Debug/tracker labels: region names, match status, confidence messages, setup errors.
- Source metadata that appears in Chinese, such as KongYing app names or category labels.

Do not rename raw imported files in `data/kongying/raw/` or processed PNG files in `data/kongying/processed/`. Those should stay source-faithful so manifests and hashes remain reproducible.

## Recommended Structure

Add translation dictionaries as data, not hardcoded strings:

```text
data/localization/
  english/
    map_regions.json
    marker_categories.json
    item_names.json
    ui_strings.json
    source_terms.json
```

Suggested dictionary shape:

```json
{
  "zh-CN source text": {
    "en-US": "English text",
    "notes": "Where this appears or ambiguity notes"
  }
}
```

For known internal IDs, prefer ID keys:

```json
{
  "MainMap": {
    "en-US": "Teyvat Surface Map"
  },
  "DXKQMap": {
    "en-US": "The Chasm"
  }
}
```

## Frontend Notes

`external/map_front_v3` already has a Vue i18n layout:

```text
external/map_front_v3/src/i18n/en-US/index.js
external/map_front_v3/src/i18n/zh-CN/index.js
external/map_front_v3/src/i18n/index.js
```

For new map UI work:

- Add English text to `en-US`.
- Keep Chinese source text in `zh-CN` if the old UI still needs it.
- Do not put visible Chinese strings directly in Vue components.
- Make `en-US` the default locale for the custom tracker/map app.

## Tracker Notes

Python tracker output should stay English. Current JSON fields are already English:

```json
{
  "accepted": false,
  "confidence": 0.851,
  "rejection_reason": "low_confidence:0.851<0.880"
}
```

If a matched asset has a region code, display a translated label from `data/localization/english/map_regions.json`.

## Translation Workflow

1. Extract or collect Chinese strings from source metadata and frontend code.
2. Store mappings in `data/localization/english/*.json`.
3. Add a small loader utility for Python and frontend import/export if needed.
4. Render English labels in UI, while keeping raw source IDs in debug fields.
5. Add a missing-translation report that lists untranslated Chinese strings.

Useful search commands:

```powershell
rg "[\u4e00-\u9fff]" external data tracker_core tools docs
rg "zh-CN|en-US|i18n" external/map_front_v3/src
```

## Initial Region Translations

Use these as seed labels:

```json
{
  "MainMap": "Teyvat Surface Map",
  "DXKQMap": "The Chasm",
  "JRZHMap": "Veluriyam Mirage / Bottleland",
  "LXSJMap": "Penumbra Event Map",
  "XMLK": "Simulanka",
  "QD28": "Event Island Map",
  "YXGMap": "Enkanomiya",
  "XMOverlay": "Underground / Overlay Map"
}
```

Some event map names need manual confirmation against Genshin naming because KongYing bundle abbreviations are not self-documenting.

