from pathlib import Path

from tools.reward_detector import capture
from tools.reward_detector.image_io import load_png
from tools.reward_detector.nearest_pin import MapPin, MapPosition, infer_likely_source
from tools.reward_detector.primogem_detector import detect_primogem_reward, load_templates
from tools.reward_detector.reward_tracker import build_arg_parser, run_once


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
FIXTURES = ROOT / "smoke_tests" / "fixtures"


def test_app_parser_starts_without_crashing():
    parser = build_arg_parser()
    args = parser.parse_args(["--image", str(FIXTURES / "blank.png"), "--position", "1,2,3"])
    assert args.image.endswith("blank.png")
    assert args.position.x == 1


def test_capture_module_loads_and_crops_relative_roi():
    image = load_png(FIXTURES / "blank.png")
    roi = capture.DEFAULT_REWARD_ROI.to_pixels(image.shape)
    cropped = capture.crop(image, roi)
    assert cropped.shape[0] > 0
    assert cropped.shape[1] > 0


def test_detector_loads_templates():
    templates = load_templates(TEMPLATES)
    assert any(template.name == "primogem_icon" for template in templates)


def test_detector_returns_no_detection_on_blank_image():
    image = load_png(FIXTURES / "blank.png")
    result = detect_primogem_reward(image, templates_dir=TEMPLATES)
    assert result.detected is False
    assert result.confidence < 0.78


def test_detector_returns_positive_on_primogem_sample():
    image = load_png(FIXTURES / "primogem_reward_sample.png")
    result = detect_primogem_reward(image, templates_dir=TEMPLATES)
    assert result.detected is True
    assert result.kind == "primogem_reward"
    assert result.amount == 5
    assert result.confidence >= 0.78


def test_nearest_pin_chooses_closest_chest_candidate():
    pins = [
        MapPin(id="chest-a", x=103, y=101, kind="chest", map_id=1),
        MapPin(id="oculus-a", x=101, y=100, kind="oculus", map_id=1),
        MapPin(id="chest-b", x=200, y=200, kind="chest", map_id=1),
    ]
    inference = infer_likely_source(
        detection_confidence=0.98,
        detection_kind="primogem_reward",
        amount=5,
        position=MapPosition(100, 100, 1),
        pins=pins,
    )
    assert inference.pin is not None
    assert inference.pin.id == "chest-a"


def test_low_confidence_does_not_auto_mark():
    pins = [MapPin(id="chest-a", x=100, y=100, kind="chest", map_id=1)]
    inference = infer_likely_source(
        detection_confidence=0.35,
        detection_kind="primogem_reward",
        amount=5,
        position=MapPosition(100, 100, 1),
        pins=pins,
    )
    assert inference.action == "needs_review"


def test_debug_logs_and_roi_screenshot_are_saved(tmp_path):
    record = run_once(
        image_path=FIXTURES / "primogem_reward_sample.png",
        pins_path=FIXTURES / "pins.json",
        position=MapPosition(100, 100, 1),
        templates_dir=TEMPLATES,
        debug_dir=tmp_path,
    )
    assert record["detection"]["detected"] is True
    assert (tmp_path / "last_detection.json").exists()
    assert (tmp_path / "last_reward_roi.png").exists()
