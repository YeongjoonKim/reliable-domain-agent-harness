"""CLI smoke tests never overwrite snapshots without an explicit update flag."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts import export_demo as exporter

ROOT = Path(__file__).resolve().parents[1]


class HarnessCLIOutputTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        # Execute real CLIs in a disposable source copy: no mocked Runtime or
        # writer, no modification of repository snapshots during tests.
        shutil.copytree(ROOT / "src", self.root / "src", ignore=shutil.ignore_patterns("__pycache__"))
        for relative in exporter.SOURCE_FILES:
            source, destination = ROOT / relative, self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        (self.root / "examples").mkdir()
        self.snapshots = {}
        for name in ("recovery.json", "paired-evaluation.json", "evaluation-cases.json"):
            data = b'{"unchanged_snapshot": true}\n'
            (self.root / "examples" / name).write_bytes(data)
            self.snapshots[name] = data

    def command(self, *arguments, expected=0):
        environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        result = subprocess.run([sys.executable, *arguments], cwd=self.root, env=environment,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def assert_snapshots_unchanged(self):
        self.assertEqual({name: (self.root / "examples" / name).read_bytes() for name in self.snapshots},
                         self.snapshots)

    def test_quick_start_writes_ignored_outputs_and_preserves_all_snapshots(self):
        self.command("-m", "src.harness.demo")
        self.command("-m", "src.harness.evaluation")
        self.assert_snapshots_unchanged()
        run = json.loads((self.root / "outputs/recovery.json").read_text())
        self.assertEqual((run["state"], run["calls"], run["replay"]["external_calls"]), ("COMPLETED", 2, 0))
        evaluation = json.loads((self.root / "outputs/paired-evaluation.json").read_text())
        self.assertEqual(evaluation["summary"]["harness"]["task_success"], 24)
        self.assertEqual(len(json.loads((self.root / "outputs/evaluation-cases.json").read_text())), 24)

    def test_only_explicit_update_examples_replaces_tracked_snapshot_targets(self):
        self.command("-m", "src.harness.demo", "--update-examples")
        self.assertEqual(json.loads((self.root / "examples/recovery.json").read_text())["state"], "COMPLETED")
        for name in ("paired-evaluation.json", "evaluation-cases.json"):
            self.assertEqual((self.root / "examples" / name).read_bytes(), self.snapshots[name])
        self.command("-m", "src.harness.evaluation", "--update-examples")
        self.assertEqual(len(json.loads((self.root / "examples/evaluation-cases.json").read_text())), 24)
        self.assertFalse((self.root / "outputs").exists())

    def test_exporter_default_and_explicit_demo_refresh_then_read_only_check(self):
        self.command("scripts/export_demo.py")
        self.assertTrue((self.root / "outputs/demo/core-evidence.json").is_file())
        self.assertFalse((self.root / "demo/core-evidence.json").exists())
        self.assert_snapshots_unchanged()
        self.command("scripts/export_demo.py", "--check", expected=1)
        self.assertFalse((self.root / "demo").exists())
        self.command("scripts/export_demo.py", "--update-demo")
        before = {name: (self.root / "demo" / name).read_bytes() for name in exporter.FILES}
        self.command("scripts/export_demo.py", "--check")
        self.assertEqual(before, {name: (self.root / "demo" / name).read_bytes() for name in exporter.FILES})
        self.assert_snapshots_unchanged()

    def test_exporter_check_rejects_semantic_tampering_without_replacing_it(self):
        self.command("scripts/export_demo.py", "--update-demo")
        path = self.root / "demo/core-evidence.json"
        artifact = json.loads(path.read_text())
        artifact["scenarios"][0]["run"]["claims"][0]["value"] += 1
        path.write_text(json.dumps(artifact))
        before = {name: (self.root / "demo" / name).read_bytes() for name in exporter.FILES}
        self.command("scripts/export_demo.py", "--check", expected=1)
        self.assertEqual(before, {name: (self.root / "demo" / name).read_bytes() for name in exporter.FILES})

    def test_exporter_modes_are_mutually_exclusive_before_execution(self):
        self.command("scripts/export_demo.py", "--check", "--update-demo", expected=2)
        self.assertFalse((self.root / "outputs").exists())
        self.assertFalse((self.root / "demo").exists())


if __name__ == "__main__":
    unittest.main()
