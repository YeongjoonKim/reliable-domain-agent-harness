"""통합 및 회귀: 실제 레지스트리 경로, 취소, 복구, 재현을 검사한다."""
import asyncio
from dataclasses import replace
import unittest
from src.harness.evaluation import cases, candidate_function, score
from src.harness.policies import Policy
from src.harness.replay import replay
from src.harness.runtime import Runtime
from src.harness.tools import make_registry


class IntegrationTests(unittest.IsolatedAsyncioTestCase):
    def case(self, name="retry_recovery-1"):
        return next(case for case in cases() if case["id"] == name)

    async def run_case(self, name="retry_recovery-1", policy=None):
        case = self.case(name)
        registry = make_registry(case["fixtures"], case["faults"])
        result = await Runtime(registry, policy).run(case["needs"], case["plan"], candidate_function(case))
        return result, registry

    async def test_regression_cultivation_guide_does_not_support_area(self):
        result, _ = await self.run_case("irrelevant-1")
        self.assertEqual(result["state"], "FAILED")
        self.assertTrue(result["verification"]["signals"]["retrieval_success"])
        self.assertFalse(result["verification"]["signals"]["evidence_relevance"])

    async def test_recovery_state_sequence(self):
        result, _ = await self.run_case()
        self.assertEqual(result["state"], "COMPLETED")
        self.assertEqual(result["calls"], 2)
        self.assertIn("RETRYING", [event["state"] for event in result["trajectory"]])

    async def test_retry_budget(self):
        result, _ = await self.run_case(policy=Policy(max_retry=0))
        self.assertEqual(result["state"], "FAILED")
        self.assertEqual(result["calls"], 1)

    async def test_call_budget(self):
        result, _ = await self.run_case("multi_tool-1", Policy(max_steps=1))
        self.assertEqual(result["calls"], 0)

    async def test_deadline(self):
        result, _ = await self.run_case("timeout-1", Policy(timeout=0.001))
        self.assertEqual(result["trajectory"][-1]["error_type"], "deadline")

    async def test_cancel_propagates(self):
        case = self.case("timeout-1")
        runtime = Runtime(make_registry(case["fixtures"], case["faults"]))
        task = asyncio.create_task(runtime.run(case["needs"], case["plan"]))
        await asyncio.sleep(0.001)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertEqual(runtime.last_machine.state.value, "CANCELLED")

    async def test_permission_denied_before_handler(self):
        result, _ = await self.run_case(policy=Policy(permissions=()))
        self.assertEqual(result["calls"], 1)
        self.assertEqual(result["replay_bundle"]["records"][0]["observations"][0]["status"], "denied")

    async def test_replay_no_tools(self):
        result, registry = await self.run_case()
        async def forbidden(_):
            raise AssertionError("replay must not execute")
        registry.handlers = {name: forbidden for name in registry.handlers}
        self.assertEqual(replay(result["replay_bundle"], registry, Policy())["external_calls"], 0)

    async def test_replay_tamper(self):
        result, registry = await self.run_case()
        result["replay_bundle"]["records"][0]["claims"][0]["value"] = 9
        with self.assertRaises(ValueError):
            replay(result["replay_bundle"], registry, Policy())

    async def test_replay_version_drift(self):
        result, registry = await self.run_case()
        registry.specs["document_lookup"] = replace(registry.specs["document_lookup"], version="2")
        with self.assertRaises(ValueError):
            replay(result["replay_bundle"], registry, Policy())

    async def test_output_schema_checked(self):
        registry = make_registry()
        async def malformed(_):
            return {"evidence": [{"value": "bad"}]}
        registry.handlers["document_lookup"] = malformed
        result = await registry.call("document_lookup", {"key": "x"}, ("read:synthetic",))
        self.assertEqual(result["status"], "schema_error")


class ConformanceTests(unittest.IsolatedAsyncioTestCase):
    async def test_twenty_four_synthetic_scenarios(self):
        for case in cases():
            with self.subTest(case=case["id"]):
                run = await Runtime(make_registry(case["fixtures"], case["faults"])).run(
                    case["needs"], case["plan"], candidate_function(case))
                self.assertTrue(score(case, run["claims"]))
                self.assertEqual(run["state"], "FAILED" if case["expected"] is None else "COMPLETED")
