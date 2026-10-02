"""단위: 상태, 입력 계약, 정책, 인용과 수치 결과를 검증한다."""
import unittest
from copy import deepcopy
from src.harness.models import Need, evidence, claim_from, digest
from src.harness.policies import Policy
from src.harness.registry import validate
from src.harness.scientific import check_statistics
from src.harness.state_machine import Machine, State
from src.harness.tools import NUMERIC
from src.harness.verifier import verify


class UnitTests(unittest.TestCase):
    def setUp(self):
        self.row = evidence("area", "glassleaf", "area", 42, "ha")
        self.need = Need("glassleaf", "area", "ha")

    def report(self, rows=None, claims=None):
        rows = [self.row] if rows is None else rows
        claims = [claim_from(self.row)] if claims is None else claims
        return verify([self.need], claims, [dict(status="ok", evidence=rows, tool="lookup", tool_version="1")])

    def test_valid_span_and_provenance(self):
        result = self.report()
        self.assertTrue(result["accepted"])
        self.assertEqual(result["provenance"][0]["source_hash"], digest(self.row["body"]))

    def test_invalid_span(self):
        claim = claim_from(self.row)
        claim["start"] = 0
        self.assertIn("invalid_citation", self.report(claims=[claim])["reasons"])

    def test_body_hash_mismatch(self):
        row = deepcopy(self.row)
        row["body"] += "tamper"
        self.assertFalse(self.report([row])["accepted"])

    def test_metadata_not_in_span(self):
        row = deepcopy(self.row)
        row["value"] = 99
        self.assertFalse(self.report([row], [claim_from(row)])["accepted"])

    def test_wrong_value(self):
        claim = claim_from(self.row)
        claim["value"] += 1
        result = self.report(claims=[claim])
        self.assertTrue(result["signals"]["evidence_relevance"])
        self.assertFalse(result["signals"]["claim_support"])

    def test_stale(self):
        row = evidence("old", "glassleaf", "area", 42, "ha", "2025-01-01")
        self.assertIn("stale_or_future_evidence", self.report([row], [claim_from(row)])["reasons"])

    def test_conflict_same_period(self):
        row = evidence("other", "glassleaf", "area", 99, "ha")
        self.assertIn("conflicting_evidence", self.report([self.row, row])["reasons"])

    def test_distinct_period_not_conflict(self):
        row = evidence("earlier", "glassleaf", "area", 39, "ha", "2026-09-01")
        self.assertTrue(self.report([self.row, row])["accepted"])

    def test_wrong_unit(self):
        row = evidence("other", "glassleaf", "area", 42, "acres")
        self.assertFalse(self.report([row], [claim_from(row)])["accepted"])

    def test_missing(self):
        self.assertFalse(self.report([], [])["signals"]["retrieval_success"])

    def test_invalid_transition(self):
        with self.assertRaises(ValueError):
            Machine().move(State.COMPLETED)

    def test_terminal_immutable(self):
        machine = Machine()
        machine.move(State.CANCELLED)
        with self.assertRaises(ValueError):
            machine.move(State.PLANNING)

    def test_trace_raw_rejected(self):
        with self.assertRaises(ValueError):
            Machine().trace.append("CREATED", raw="sensitive")

    def test_policy_bounds(self):
        for kwargs in ({"timeout": float("inf")}, {"max_retry": 20}, {"max_steps": True}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Policy(**kwargs)

    def test_schema_denies_extra_and_nonfinite(self):
        for data in ({"values": [1, True]}, {"values": [1, float("nan")]},
                     {"values": [1, 2], "extra": 1}, {"values": []}):
            with self.subTest(data=data), self.assertRaises(ValueError):
                validate(data, NUMERIC)

    def test_numeric_independent_check(self):
        good = dict(count=3, mean=2, sample_variance=1, minimum=1, maximum=3)
        self.assertTrue(check_statistics([1, 2, 3], good))
        self.assertFalse(check_statistics([1, 2, 3], dict(good, mean=9)))
