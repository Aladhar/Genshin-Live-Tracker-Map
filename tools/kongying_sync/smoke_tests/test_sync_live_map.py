import json
from pathlib import Path

from tools.kongying_sync.sync_live_map import summarize_webapp


def test_summary_contains_latest_nod_krai_layers():
    webapp = json.loads((Path(__file__).resolve().parents[1] / "data" / "webapp.json").read_text())
    summary = summarize_webapp(webapp)

    assert summary["tileCount"] >= 36
    assert summary["pluginCount"] >= 33
    assert summary["latestOfficialTermStatus"]["A:MD:SHENDIAN"]
    assert summary["latestOfficialTermStatus"]["A:MD:FENGXISHAN"]
    assert summary["latestOfficialTermStatus"]["空之神殿"]
    assert summary["latestOfficialTermStatus"]["远古圣山"]
    assert summary["latestOfficialTermStatus"]["A:NDKL:NDKL"]
    assert summary["latestOfficialTermStatus"]["A:NDKL:NDKL2"]
    assert summary["latestOfficialTermStatus"]["HIISI_ISLAND"]
    assert summary["latestOfficialTermStatus"]["LEMPO_ISLAND"]
    assert summary["latestOfficialTermStatus"]["PAHA_ISLE"]

    coverage = {entry["id"]: entry for entry in summary["officialLogCoverage"]}
    assert coverage["hotfix-2026-04-07-6.5"]["present"]
    assert coverage["hotfix-2026-04-08-sky-temple-library"]["present"]
    assert coverage["hotfix-2026-04-09-ancient-sacred-mountain"]["present"]
    assert coverage["client-2025-12-03-6.2-layer"]["present"]
    assert coverage["hotfix-2025-09-10-6.0-nod-krai"]["present"]
    assert coverage["web-2025-09-10-nod-krai-icon"]["present"]
    assert coverage["hotfix-2025-07-29-5.8"]["present"]
