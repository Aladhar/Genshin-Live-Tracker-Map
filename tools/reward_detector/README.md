# Reward Detector Prototype

Screenshot-only Primogem/reward detection for the Genshin/Kongying map helper.

Safety boundary:

- Captures pixels only.
- Does not read game memory, inject DLLs, modify game files, automate gameplay, or upload account data.
- Marker completion is emitted as a local suggestion. Low-confidence detections become `needs_review`.

Workflow:

```bash
python3 -m tools.reward_detector.scripts.generate_synthetic_assets
python3 -m tools.reward_detector.reward_tracker \
  --image tools/reward_detector/smoke_tests/fixtures/primogem_reward_sample.png \
  --pins tools/reward_detector/smoke_tests/fixtures/pins.json \
  --position 100,100,1
python3 -m pytest tools/reward_detector/smoke_tests
```

Real capture:

```bash
python3 -m tools.reward_detector.reward_tracker --pins pins.json --position 1234,5678,1
```

For real-time use, install the existing screenshot stack in a virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r tools/chest_detector/requirements.txt
```

The detector searches a normalized reward ROI instead of hardcoding one resolution. The default ROI is deliberately broad around the middle/right reward stack, and can be overridden with `--roi x,y,width,height`.

