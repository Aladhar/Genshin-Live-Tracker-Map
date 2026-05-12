# GitHub Copilot Instructions

This document guides AI coding agents working in this monorepo. It documents architecture, critical workflows, integration points, and project-specific conventions.

## Project Overview

**Genshin Live Tracker & Map**: A multi-component Genshin Impact assistant combining:
- **`tools/`**: Python screenshot-based reward detector & Kongying live map sync
- **`external/map_register_v3/`**: Vue 3 / TypeScript map point marker system (admin/content panel)
- **`external/map_front_v3/`**: Quasar/Vue map frontend for players
- **`external/docs/`**: VitePress documentation site (Chinese/English/Japanese)
- **`external/cvAutoTrack/`**: C++ Windows DLL for screenshot-based position/reward detection
- **`external/genshin-map-cloud/`**: Java backend (marked as reference only; this repo is frontend/tooling-focused)

## Critical Architecture & Data Flows

### 1. Map System: Kongying Official Data → Live Marker Display

**Data source**: Kongying official public API (`https://assets.yuanshen.site/webapp.json`).

- **Location**: `tools/kongying_sync/data/webapp.json` (official snapshot, never edit by hand).
- **Generated files**: 
  - `data/map_summary.json` (compact region/layer/tile index).
  - `reports/live_map_sync_report.md` (coverage status, blockers).
  - `reports/map_implementation_checklist.md` (checkbox tracker for real pin integration).

**Workflow**:
1. Run `python3 -m tools.kongying_sync.sync_live_map` to fetch latest public config.
2. Sync validates tile configs, plugin configs, and layered/underground metadata.
3. Cross-reference official Kongying docs, not GitHub (GitHub is dev reference only).
4. Report authentication blockers: marker/item/icon APIs require bearer token (missing).

**Key limitation**: Full chest/oculus/resource marker parity blocked until authenticated Kongying export or local client cache available. Current state tracks public map/layer shell only.

### 2. Reward Detection: Screenshot → Position + Template Match → Pin Suggestion

**Platform**: Windows 11 (captured via cvAutoTrack DLL or screenshot tools on Windows).

**Components**:
- **`tools/reward_detector/`**: Python module for Primogem/reward detection (cross-platform in dev, Windows 11 target in production).
  - `reward_tracker.py`: Main entry point; accepts screenshot + position + optional ROI.
  - `primogem_detector.py`: Template matching on normalized reward popup region (handles variable UI resolutions).
  - `nearest_pin.py`: Suggests closest chest/oculus pin from imported pins.
  - Safety: captures pixels only; no game memory, DLL injection, gameplay automation, or account upload.

**Data Structures** (minimal memory footprint):
- **`MapPosition`**: `{x: float, y: float, map_id: int | null}` - current location on map.
- **`MapPin`**: `{id: str, x: float, y: float, kind: str, map_id: int | null, title: str, completed: bool}` - stores chest/oculus coordinates and state.
- **`DetectionResult`**: `{detected: bool, confidence: float, kind: str, roi: PixelRegion, match: Match, amount: int}` - parsed from templates.
- **`PinInference`**: `{pin: MapPin, distance: float, confidence: float, action: str, reason: str}` - final suggestion with reasoning.
- **ROI**: Normalized relative region `{start_x, start_y, width, height}` as percentage of screen (default: `0.48, 0.20, 0.42, 0.58` for reward stack).

**Workflow**:
```bash
# Generate synthetic test assets
python3 -m tools.reward_detector.scripts.generate_synthetic_assets

# One-shot detector call
python3 -m tools.reward_detector.reward_tracker \
  --image path/to/screenshot.png \
  --pins pins.json \
  --position 1234,5678,1 \
  --roi x,y,width,height  # optional; default is normalized broad region

# Smoke tests
python3 -m pytest tools/reward_detector/smoke_tests -q
```

**Output**: Local JSON suggestion with:
- Detection confidence (high/medium/low).
- Cropped reward screenshot.
- Nearby candidate pin list (filtered by area + layer).
- Current position (screenshot coordinates).
- No auto-marking; low/medium confidence → `needs_review` file.

### 3. Map UI: Vue 3 + TypeScript + Deck.GL

**Admin/marker panel**: `external/map_register_v3/`
- **Tech**: Vue 3, TypeScript, Vite, Tailwind, Element Plus, Deck.GL for large point sets.
- **Data layer**: Alova (HTTP client), Socket.io (real-time sync), Dexie (IndexedDB for offline markers).
- **Build**: `pnpm dev` (local), `pnpm build` (production).
- **Entry**: `src/main.ts`; routes in `src/router/`.
- **Key stores** (Pinia): `src/stores/` for global state (user, markers, layers).
- **Schemas**: Protobuf for network serialization (`src/api/protobuf/`).
- **Styling**: Tailwind + UnoCSS; no hardcoded pixel values.

**Player frontend**: `external/map_front_v3/`
- **Tech**: Quasar (Vue 3 wrapper), also Tailwind-based.
- **Build**: `quasar dev`, `quasar build`.
- **Routes**: Router guard checks Gitee OAuth2 token; falls back to guest mode.

### 4. Documentation Site: VitePress (Multi-Language)

**Location**: `external/docs/`
- **Tech**: VitePress + Vue 3, with custom components for forums/team pages.
- **Locales**: `src/zh/`, `src/en/`, `src/ja/` (mirror structure across languages).
- **Data**: `src/_data/` for shared JSON (member lists, blog metadata).
- **Build commands**:
  - `pnpm dev` → hot reload.
  - `pnpm build` → static HTML in `dist/`.
  - `pnpm build-data` → refresh member/blog metadata before build.
- **Import paths**: `@/` (theme), `~/` (content in `src/`).
- **Quality gates**: `pnpm lint`, `pnpm typecheck`, `pnpm lint:zh` (Chinese text linting).

### 5. Desktop Windows Client: C++ + OpenCV

**Location**: `external/cvAutoTrack/`
- **Platform**: Windows 11 (primary deployment environment).
- **Build**: `.\\ build-windows-exe.ps1 -InstallVcpkg -RunSmokeTest` (PowerShell, Windows only).
- **Dependencies**: Managed via vcpkg (`external/vcpkg/`); includes OpenCV for real-time screenshot capture and position detection.
- **Outputs**: `cvAutoTrack.dll` (screenshot DLL for reward detector) + `test_impl_cpp.exe` (test harness).
- **Purpose**: Real-time game screenshot capture, coordinates → position inference, and integration with reward detector pipeline.

## Developer Workflows & Commands

### Python Tools (Reward Detector + Kongying Sync)

```bash
# Setup (once)
python3 -m venv .venv
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows
pip install -r tools/reward_detector/requirements.txt
pip install -r tools/chest_detector/requirements.txt

# Run sync
python3 -m tools.kongying_sync.sync_live_map

# Run reward detector smoke tests
python3 -m pytest tools/reward_detector/smoke_tests -q

# One-shot detector
python3 -m tools.reward_detector.reward_tracker --image test.png --pins pins.json --position 100,100,1
```

### Vue/TypeScript (map_register_v3, map_front_v3, docs)

```bash
# Setup
corepack enable  # enable pnpm/yarn version management
cd external/map_register_v3
pnpm install

# Development
pnpm dev              # Vite dev server with HMR
pnpm typecheck        # TypeScript validation
pnpm lint             # ESLint + style check
pnpm lint:fix         # Auto-fix style issues

# Build & deploy
pnpm build            # Production bundle
pnpm preview          # Test production build locally
```

### Documentation Site

```bash
cd external/docs
pnpm build-data      # Refresh member/blog metadata
pnpm dev             # Live reload
pnpm build           # Static site to dist/
pnpm lint:zh         # Check Chinese text spacing
pnpm lint:zh-fix     # Auto-fix Chinese issues
```

## Project-Specific Conventions

### 1. Import Path Mapping

- **Vue/TS projects** define `@/` → theme, `~/` → source. Honor these aliases.
- **Incorrect**: `import { X } from 'src/components/X'` → **Correct**: `import { X } from '~/components/X'`.

### 2. Data & Coordinates

- **`areaKey`**: Unique Kongying identifier for region/tile (stored in `map_summary.json` tiles array). Examples: `A:MD:MENGDE` (Mondstadt), `A:NT:NATA5` (Natlan 5.8), `提瓦特-base0` (Teyvat base).
- **Coordinates**: Numeric `(x, y)` pairs. Validate against `map_summary.json` → `tiles[areaKey].size` to ensure within bounds.
- **Map Pin Schema**: `{id: str, x: float, y: float, kind: "chest"|"oculus", map_id: int|null, title: str, completed: bool}`.
  - `kind`: Always one of `"chest"` or `"oculus"` for reward detector context.
  - `completed`: Optional flag for UI state; detector always emits `false`.
  - `title`: Human-readable name (e.g., "Common Chest", "Pyroculus") from Fandom wiki source.
- **No hardcoding**: Tile URLs, overlay configs, layer metadata come from `map_summary.json` snapshot only.

### 3. Commit Conventions

- **Scope tags**: Limited to `i18n`, `forum`, `blog`, `theme`, `map`, `reward`, `sync`.
- **Format**: Imperative mood (`feat(map): add layer selector`).
- **Tool**: Use `pnpm commit` (Commitizen) for guided prompts across all Vue projects.

### 4. Safety Boundaries (Reward Detector)

- ✅ **Allowed**: Screenshot capture, template matching, position inference from screenshots.
- ❌ **Forbidden**: Game memory reads, DLL injection, game file modification, gameplay automation, token/account storage.
- **Output**: Local JSON suggestions with confidence levels; human review required for low/medium.

### 5. Localization & Multi-Language Content

- **Mirror structure**: Any content in `src/zh/` must have equivalents in `src/en/` and `src/ja/`.
- **Shared data**: Use `src/_data/` for JSON that's reused across languages (members, blog metadata).
- **Text linting**: `pnpm lint:zh` catches missing punctuation, spacing in Chinese; run before PR.

## Integration Points & External Dependencies

### Data Sources

**Genshin Impact Game Data**: Source from [Genshin Impact Fandom Wiki](https://genshin-impact.fandom.com/wiki/Genshin_Impact_Wiki).
- **Chest types & rewards**: [Chest (Genshin Impact) wiki page](https://genshin-impact.fandom.com/wiki/Chest) lists all chest types (Common, Exquisite, Precious, Luxurious, Remarkable, Seelies, etc.) with reward tables by region.
- **Oculus types & distribution**: [Oculus pages](https://genshin-impact.fandom.com/wiki/Anemoculus), [Geoculus](https://genshin-impact.fandom.com/wiki/Geoculus), [Electroculus](https://genshin-impact.fandom.com/wiki/Electroculus), [Dendroculus](https://genshin-impact.fandom.com/wiki/Dendroculus), etc., with location counts per region.
- **Item names & categories**: Item pages reference IDs, rarities, drop sources. For reward detector: focus on Primogem, Mora, Experience, weapon/artifact materials.
- **Region progression**: [Regions wiki page](https://genshin-impact.fandom.com/wiki/Region) maps story chapters to available areas.

**Do NOT use**: Game memory reads, reverse-engineered APIs, or unofficial data aggregators. Keep data imports transparent and audited.

### Official Kongying Data

- **Public snapshot**: `tools/kongying_sync/data/webapp.json` (fetched from `https://assets.yuanshen.site/webapp.json`).
- **Map summary**: `tools/kongying_sync/data/map_summary.json` contains all tile/region keys, sizes, centers, tile offsets for coordinate validation.
- **Auth-gated endpoints** (currently inaccessible without bearer token):
  - `/area/get/list` — region tree.
  - `/item_type/get/list_all` — chest/oculus/resource categories.
  - `/item/get/list` — individual marker coordinates and metadata.
  - `/icon/get/list` — icon URLs.
  - `/marker_doc/list_page_bin_md5` — marker document hashes.

### Git/Version Control

- **Conventional commits**: Enforced via commitlint (scope whitelist: `i18n`, `forum`, `blog`, `theme`, `map`, `reward`, `sync`).
- **CI/CD**: `.github/workflows/` (not detailed here; see repo for specifics).

### Package Managers

- **JavaScript/TypeScript**: `pnpm` (monorepo with workspace).
- **Python**: `pip` + `requirements.txt` (each tool specifies deps).
- **C++**: `vcpkg` (locked in `external/vcpkg/`, managed by build script).

## Testing & Validation

### Python (Reward Detector & Sync)

- **Smoke tests** in `smoke_tests/` folder; run with `pytest`.
- **Fixtures**: Synthetic Primogem sample, test pin JSON, sample screenshots.
- **No integration tests** with real game; use screenshots only.

### JavaScript/TypeScript

- **No unit test runner** in the docs site; quality via linting, type checks, and manual page verification via `pnpm dev`.
- **Type safety**: Enforce via `pnpm typecheck` and ESLint.
- **Manual QA**: After editing generated content (member data, blog), regenerate with `pnpm build-data` and verify output in `pnpm dev`.

### Validation Rules

- **Markers**: Validate `areaKey` exists in `map_summary.json`, coordinates are numeric, no auth tokens in imported files.
- **Imports**: Ensure no unused imports; run `source.unusedImports` refactoring.
- **Builds**: `pnpm build` must complete without warnings; check `dist/` exists.

## Key Files to Understand

- `tools/kongying_sync/sync_live_map.py` — Official map snapshot fetch & validation.
- `tools/reward_detector/reward_tracker.py` — One-shot detector entry.
- `tools/reward_detector/primogem_detector.py` — Template matching logic.
- `external/map_register_v3/src/main.ts` — Admin panel entry.
- `external/docs/.vitepress/config.ts` — Documentation site config.
- `tools/kongying_sync/reports/map_implementation_checklist.md` — Real-time tracker for marker integration status.

## Common Pitfalls & How to Avoid Them

1. **Editing `webapp.json` by hand**: Don't. It's a snapshot; regenerate via `sync_live_map`.
2. **Hardcoding tile URLs or overlay configs**: Use values from `map_summary.json` or `webapp.json`.
3. **Forgetting `pnpm build-data` before rebuilding docs**: This skips member/blog refresh; tests will fail.
4. **Using absolute imports instead of aliases** in Vue projects: Use `@/` and `~/` consistently.
5. **Storing Kongying tokens/cache exports in the repo**: This project accepts data inputs only; redact credentials before importing.
6. **Skipping Chinese text linting**: `pnpm lint:zh` catches spacing/punctuation; mandatory before PR.
7. **Low-confidence detections auto-marking pins**: Always emit `needs_review` status; require human confirmation.

## Immediate Next Steps for Development

1. **Live marker import**: Implement authenticated Kongying export or local client cache importer (redacting tokens).
2. **Layer selector**: Connect map region (`areaKey`) to active layer (normal/underground/overlay).
3. **Real pin integration**: Replace smoke-test fixtures with imported Kongying pins; filter by area + layer.
4. **Review queue UI**: Add local file or modal for uncertain detections requiring manual confirmation.
5. **Snapshot diffing**: Document changes between `webapp.json` versions (tile additions, overlay updates, resource versions).
