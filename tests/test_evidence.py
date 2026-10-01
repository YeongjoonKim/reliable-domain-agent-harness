"""공개 실행 snapshot이 실제 예제 계산과 일치하는지 검사한다."""
import json
from pathlib import Path
import unittest
from src.export_evidence import build


class EvidenceTests(unittest.TestCase):
    def test_recorded_execution(self):
        saved = json.loads((Path(__file__).parents[1] / "examples/execution.json").read_text())
        self.assertEqual(saved, build())

    def test_dashboard_snapshot_matches_artifact(self):
        root = Path(__file__).parents[1]
        script = (root / "demo/evidence.js").read_text()
        value = script.split("window.PUBLIC_EVIDENCE = ", 1)[1].strip().removesuffix(";")
        self.assertEqual(json.loads(value), json.loads((root / "examples/execution.json").read_text()))
