"""Actual-core export, tamper detection, and comparison-only normalization."""
import asyncio
import copy
import json
import math
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import urlsplit

from scripts import export_demo as exporter
from src.harness.evaluation import cases, candidate_function, evaluate
from src.harness.models import digest
from src.harness.policies import Policy
from src.harness.replay import replay
from src.harness.runtime import Runtime
from src.harness.tools import make_registry


class CoreExporterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = asyncio.run(exporter.build_artifact())

    def scenario(self, identifier):
        return next(row for row in self.artifact["scenarios"] if row["id"] == identifier)

    def test_four_real_cases_and_same_recovery_bundle_replay(self):
        actual_cases = {case["id"]: case for case in cases()}
        for scenario in self.artifact["scenarios"]:
            case = actual_cases[scenario["case_id"]]
            registry = make_registry(case["fixtures"], case["faults"])
            direct = asyncio.run(Runtime(registry).run(case["needs"], case["plan"], candidate_function(case)))
            self.assertEqual(direct["claims"], scenario["run"]["claims"])
            self.assertEqual(direct["verification"], scenario["run"]["verification"])
            self.assertEqual(direct["state"], scenario["run"]["state"])
            async def forbidden(_):
                raise AssertionError("replay must never execute tools")
            registry.handlers = {name: forbidden for name in registry.handlers}
            self.assertEqual(replay(scenario["run"]["replay_bundle"], registry, Policy()), scenario["replay"])
            self.assertEqual(scenario["replay"]["external_calls"], 0)
        recovery = self.scenario("retry_recovery")["run"]
        self.assertEqual(recovery, self.scenario("configuration_evidence_replay")["run"])
        self.assertEqual(recovery["calls"], 2)
        self.assertIn("RETRYING", [event["state"] for event in recovery["trajectory"]])
        first, second = recovery["replay_bundle"]["records"]
        self.assertFalse(first["verification"]["signals"]["evidence_relevance"])
        self.assertTrue(first["verification"]["signals"]["retrieval_success"])
        self.assertTrue(second["verification"]["accepted"])

    def test_failed_cases_export_actual_rejected_candidates_and_exact_raw_body(self):
        conflict = self.scenario("conflicting_evidence")["run"]
        invalid = self.scenario("invalid_citation_span")["run"]
        self.assertIn("conflicting_evidence", conflict["verification"]["reasons"])
        self.assertIn("invalid_citation", invalid["verification"]["reasons"])
        for run in (conflict, invalid):
            self.assertEqual(run["state"], "FAILED")
            self.assertEqual(run["claims"], [])
            self.assertEqual(run["verification"]["provenance"], [])
        record = invalid["replay_bundle"]["records"][0]
        row, claim = record["observations"][0]["evidence"][0], record["claims"][0]
        self.assertEqual(claim["start"], 0)
        self.assertNotEqual(claim["start"], row["start"])
        self.assertEqual(row["source_hash"], digest(row["body"]))
        good = self.scenario("valid_evidence")["run"]
        provenance = good["verification"]["provenance"][0]
        row = good["replay_bundle"]["records"][0]["observations"][0]["evidence"][0]
        self.assertEqual(provenance["evidence_span"], [row["start"], row["end"]])
        self.assertEqual(json.loads(row["body"][row["start"]:row["end"]])["value"], good["claims"][0]["value"])

    def test_actual_evaluation_matches_full_twenty_four_case_computation(self):
        direct = asyncio.run(evaluate())
        for arm in ("baseline", "harness"):
            self.assertEqual(direct["summary"][arm]["task_success"],
                             self.artifact["evaluation"]["summary"][arm]["task_success"])
            for expected, actual in zip(direct["cases"], self.artifact["evaluation"]["cases"]):
                self.assertEqual({k: v for k, v in expected[arm].items() if k != "latency_ms"},
                                 {k: v for k, v in actual[arm].items() if k != "latency_ms"})
        self.assertEqual(direct["summary"]["baseline"]["task_success"], 8)
        self.assertEqual(direct["summary"]["harness"]["task_success"], 24)
        self.assertIn("not an independent LLM benchmark", self.artifact["evaluation"]["kind"])

    def test_links_resolve_to_actual_public_source_tests_and_local_execution(self):
        for scenario in self.artifact["scenarios"]:
            for name in ("source", "test"):
                link = scenario["links"][name]
                self.assertTrue(link.startswith(exporter.GITHUB + "/blob/main/"))
                relative = urlsplit(link).path.split("/blob/main/")[1]
                self.assertTrue((exporter.ROOT / relative).is_file())
                self.assertIn(relative, self.artifact["scope"]["source_files"])
            self.assertEqual((exporter.ROOT / "demo" / scenario["links"]["execution"]).resolve(),
                             exporter.ROOT / "demo/core-evidence.json")

    def test_required_fields_case_mapping_and_links_cannot_be_forged(self):
        mutations = (
            lambda a: a.pop("evaluation"),
            lambda a: a["scenarios"].pop(),
            lambda a: a["scenarios"][0].update(case_id="retry_recovery-1"),
            lambda a: a["scenarios"][0]["links"].update(test=exporter.GITHUB + "/blob/main/tests/missing.py"),
            lambda a: a["scenarios"][0]["run"].update(calls=99),
            lambda a: a["scenarios"][0]["run"].update(claims=[]),
            lambda a: a["scenarios"][0]["run"].update(state="FAILED"),
            lambda a: a["scenarios"][0]["run"]["verification"].update(accepted=False),
            lambda a: a["scenarios"][0]["run"]["trajectory"][3].update(output_hash="0" * 64),
            lambda a: a["scope"]["source_files"].update({"src/harness/runtime.py": "0" * 64}),
            lambda a: a["evaluation"]["summary"]["baseline"].update(task_success=24),
        )
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                artifact = copy.deepcopy(self.artifact)
                mutate(artifact)
                with self.assertRaises((ValueError, KeyError)):
                    exporter.validate_artifact(artifact)

    def test_raw_integrity_is_checked_before_noise_is_normalized(self):
        for field, value in (("latency_ms", 999), ("output_hash", "0" * 64)):
            with self.subTest(field=field):
                artifact = copy.deepcopy(self.artifact)
                artifact["scenarios"][0]["run"]["replay_bundle"]["records"][0]["observations"][0][field] = value
                with self.assertRaisesRegex(ValueError, "bundle integrity"):
                    exporter.semantic_content(artifact)
        artifact = copy.deepcopy(self.artifact)
        artifact["scenarios"][0]["run"]["replay_bundle"]["integrity_hash"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "bundle integrity"):
            exporter.semantic_content(artifact)

    def test_rehashed_forged_body_value_or_observed_date_is_not_execution_noise(self):
        for key, value in (("body", "forged body"), ("value", 999), ("observed", "2026-09-02")):
            with self.subTest(key=key):
                artifact = copy.deepcopy(self.artifact)
                run = artifact["scenarios"][0]["run"]
                bundle = run["replay_bundle"]
                obs = bundle["records"][0]["observations"][0]
                obs["evidence"][0][key] = value
                obs["output_hash"] = digest(obs["evidence"])
                bundle["integrity_hash"] = digest({k: v for k, v in bundle.items() if k != "integrity_hash"})
                with self.assertRaises(ValueError):
                    exporter.semantic_content(artifact)

    def test_fresh_runs_compare_equal_but_raw_ids_times_and_integrity_remain_original(self):
        fresh = asyncio.run(exporter.build_artifact())
        before = copy.deepcopy(self.artifact)
        self.assertNotEqual(self.artifact["generated_at"], fresh["generated_at"])
        self.assertNotEqual(self.artifact["scenarios"][0]["run"]["trajectory"][0]["run_id"],
                            fresh["scenarios"][0]["run"]["trajectory"][0]["run_id"])
        self.assertEqual(exporter.semantic_content(self.artifact), exporter.semantic_content(fresh))
        self.assertEqual(before, self.artifact)
        text, script = exporter.artifact_texts(self.artifact)
        self.assertEqual(json.loads(text), json.loads(script[len(exporter.JS_PREFIX):-2]))
        loaded = json.loads(text)
        self.assertEqual(loaded["generated_at"], before["generated_at"])
        self.assertEqual(loaded["scenarios"][0]["run"]["trajectory"], before["scenarios"][0]["run"]["trajectory"])
        self.assertEqual(loaded["scenarios"][0]["run"]["replay_bundle"]["integrity_hash"],
                         before["scenarios"][0]["run"]["replay_bundle"]["integrity_hash"])
        self.assertEqual(exporter.semantic_content(loaded), exporter.semantic_content(fresh))

    def test_check_is_read_only_and_detects_ui_json_or_semantic_drift(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            exporter.write_artifacts(self.artifact, path)
            before = {p.name: p.read_bytes() for p in path.iterdir()}
            exporter.check_artifacts(asyncio.run(exporter.build_artifact()), path)
            self.assertEqual(before, {p.name: p.read_bytes() for p in path.iterdir()})
            script = path / "core-evidence.js"
            script.write_text(script.read_text().replace('"COMPLETED"', '"FAILED"', 1))
            with self.assertRaisesRegex(ValueError, "UI JS/JSON mismatch"):
                exporter.check_artifacts(self.artifact, path)
            changed = copy.deepcopy(self.artifact)
            changed["evaluation"]["cases"][0]["harness"]["state"] = "FAILED"
            # A change outside normalized execution noise is detected even when
            # the replay bundle itself has not changed.
            exporter.write_artifacts(changed, path)
            with self.assertRaisesRegex(ValueError, "stale demo artifact"):
                exporter.check_artifacts(self.artifact, path)

    def test_json_bool_integer_substitutions_are_not_semantic_equivalence(self):
        for index, key in ((0, "step_id"), (1, "sequence")):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.artifact)
                changed["scenarios"][0]["run"]["trajectory"][index][key] = True
                with self.assertRaisesRegex(ValueError, "identity/order"):
                    exporter.semantic_content(changed)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            changed = copy.deepcopy(self.artifact)
            # The summary can have equal Python values but a different JSON type.
            changed["evaluation"]["summary"]["harness"]["unsafe_answers"] = False
            with self.assertRaisesRegex(ValueError, "evaluation summary drift"):
                exporter.write_artifacts(changed, path)
            # JS must also remain exactly the same typed JSON, not bool == int.
            exporter.write_artifacts(self.artifact, path)
            script = path / "core-evidence.js"
            js_value = json.loads(script.read_text()[len(exporter.JS_PREFIX):-2])
            js_value["evaluation"]["summary"]["harness"]["unsafe_answers"] = False
            script.write_text(exporter.JS_PREFIX + json.dumps(js_value) + ";\n")
            with self.assertRaisesRegex(ValueError, "UI JS/JSON mismatch"):
                exporter.check_artifacts(self.artifact, path)

    def test_latency_summary_accepts_cross_version_rounding_without_rewriting_raw(self):
        for aggregator in (lambda values: math.fsum(values) / len(values),
                           lambda values: math.nextafter(math.fsum(values) / len(values), math.inf)):
            with self.subTest(aggregator=aggregator):
                changed = copy.deepcopy(self.artifact)
                for arm in ("baseline", "harness"):
                    latencies = [row[arm]["latency_ms"] for row in changed["evaluation"]["cases"]]
                    changed["evaluation"]["summary"][arm]["average_latency_ms"] = aggregator(latencies)
                original_hash = digest(changed)
                exporter.validate_artifact(changed)
                self.assertEqual(digest(exporter.semantic_content(changed)),
                                 digest(exporter.semantic_content(self.artifact)))
                text, script = exporter.artifact_texts(changed)
                loaded = json.loads(text)
                self.assertEqual(digest(loaded), original_hash)
                self.assertEqual(digest(json.loads(script[len(exporter.JS_PREFIX):-2])), original_hash)
                self.assertEqual(digest(changed), original_hash)
                with tempfile.TemporaryDirectory() as directory:
                    path = Path(directory)
                    exporter.write_artifacts(changed, path)
                    before = {p.name: p.read_bytes() for p in path.iterdir()}
                    exporter.check_artifacts(self.artifact, path)
                    self.assertEqual(before, {p.name: p.read_bytes() for p in path.iterdir()})

    def test_latency_summary_rejects_meaningful_drift_and_invalid_types(self):
        original = self.artifact["evaluation"]["summary"]["baseline"]["average_latency_ms"]
        for value in (original + 0.001, original * 1.1, -original,
                      True, None, "1.5", float("nan"), float("inf")):
            with self.subTest(value=value):
                changed = copy.deepcopy(self.artifact)
                changed["evaluation"]["summary"]["baseline"]["average_latency_ms"] = value
                with self.assertRaises(ValueError):
                    exporter.validate_artifact(changed)
        changed = copy.deepcopy(self.artifact)
        del changed["evaluation"]["summary"]["baseline"]["average_latency_ms"]
        with self.assertRaisesRegex(ValueError, "evaluation summary drift"):
            exporter.validate_artifact(changed)

    def test_non_latency_summary_is_exact_typed_json_even_for_tiny_rounding(self):
        for key, value in (("cases", 24.0), ("task_success", 8.0), ("unsafe_answers", False),
                           ("average_calls", math.nextafter(
                               self.artifact["evaluation"]["summary"]["baseline"]["average_calls"], math.inf)),
                           ("unknown", 0)):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.artifact)
                changed["evaluation"]["summary"]["baseline"][key] = value
                with self.assertRaisesRegex(ValueError, "evaluation summary drift"):
                    exporter.validate_artifact(changed)

    def test_exporter_uses_actual_runtime_candidate_and_evaluation_functions(self):
        with patch.object(exporter.Runtime, "run", autospec=True, side_effect=Runtime.run) as run:
            # autospec side_effect awaits the original coroutine through AsyncMock.
            artifact = asyncio.run(exporter.build_artifact())
        self.assertEqual(run.call_count, 28)  # four displayed runs + 24 paired-evaluation runs
        self.assertEqual(len(artifact["scenarios"]), 5)
        for call in run.call_args_list[:4]:
            self.assertTrue(callable(call.args[3]))


if __name__ == "__main__":
    unittest.main()
