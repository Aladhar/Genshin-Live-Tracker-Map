# Chest / Reward Popup Data Collection

This folder contains simple tools to collect and label screenshots for a chest/reward popup detector.

Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r tools/chest_detector/requirements.txt
```

Capture screenshots

```bash
python tools/chest_detector/capture_screenshots.py --output tools/chest_detector/dataset/raw --interval 0.5
```

Label screenshots

```bash
python tools/chest_detector/labeler.py --input tools/chest_detector/dataset/raw --pos tools/chest_detector/dataset/pos --neg tools/chest_detector/dataset/neg
```

Notes

- Use a region (`--region left,top,width,height`) to capture only the UI area where reward popups appear to reduce noise and save disk/CPU.
- Start with conservative capture interval (0.5s) and increase/decrease as needed.
