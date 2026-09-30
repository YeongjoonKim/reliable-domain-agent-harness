"""합성 실행의 정상·실패·메모리 격리 경계를 검증한다."""
import asyncio
from dataclasses import asdict
import unittest
from src.sample_agent import DemoRuntime, FIXTURES, dispatch, verify


class RuntimeTests(unittest.IsolatedAsyncioTestCase):
    def request(self, **changes):
        return dict({"session": "demo", "subject": "glassleaf", "needs": ["growth", "moisture"]}, **changes)

    async def test_complete(self):
        result = await DemoRuntime().run(self.request())
        self.assertEqual(result["status"], "complete")
        self.assertEqual(result["tool_calls"], 2)
        self.assertEqual(result["events"][-1], "response")

    async def test_deduplicates(self):
        runtime = DemoRuntime()
        result = await runtime.run(self.request(needs=["growth", "growth"]))
        self.assertEqual(result["tool_calls"], 1)
        self.assertEqual(runtime.calls, 1)

    async def test_budget_before_execution(self):
        runtime = DemoRuntime(max_calls=1)
        with self.assertRaisesRegex(ValueError, "budget"):
            await runtime.run(self.request())
        self.assertEqual(runtime.calls, 0)

    async def test_timeout_preserves_other_tool(self):
        result = await DemoRuntime(timeout=0.005, faults={"reference": "timeout"}).run(self.request())
        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["missing"], ["growth"])
        self.assertEqual(result["tool_status"][0]["status"], "timeout")

    async def test_error_is_not_empty(self):
        result = await DemoRuntime(faults={"reference": "error"}).run(self.request())
        self.assertEqual(result["tool_status"][0]["status"], "error")

    async def test_empty_is_not_error(self):
        result = await DemoRuntime(faults={"reference": "empty"}).run(self.request())
        self.assertEqual(result["tool_status"][0]["status"], "empty")

    async def test_summary_zero_new_search(self):
        runtime = DemoRuntime()
        answer = await runtime.run(self.request())
        summary = await runtime.run(self.request(needs=[], mode="summary"))
        self.assertEqual(runtime.calls, 2)
        self.assertEqual(summary["tool_calls"], 0)
        self.assertEqual(summary["sources"], answer["sources"])

    async def test_memory_isolation(self):
        runtime = DemoRuntime()
        await runtime.run(self.request())
        for session, subject in [("other", "glassleaf"), ("demo", "other")]:
            result = await runtime.run({"session": session, "subject": subject, "mode": "summary"})
            self.assertEqual(result["status"], "missing_context")

    async def test_no_fact_for_unknown_subject(self):
        result = await DemoRuntime().run(self.request(subject="unknown"))
        self.assertEqual(result["status"], "unresolved")
        self.assertEqual(result["sources"], [])

    async def test_invalid_request(self):
        for request in [None, self.request(needs=["sql"]), self.request(session=True),
                        self.request(mode="summary"), self.request(needs=["growth"], extra="bad")]:
            code, _ = await dispatch(DemoRuntime(), "POST", "/api/demo/agent/query", request)
            self.assertEqual(code, 400)

    async def test_deterministic_artifact(self):
        one = await DemoRuntime().run(self.request())
        two = await DemoRuntime().run(self.request())
        self.assertEqual(one["artifact_sha256"], two["artifact_sha256"])

    async def test_mock_api_boundaries(self):
        self.assertEqual((await dispatch(DemoRuntime(), "GET", "/api/demo/health"))[0], 200)
        self.assertEqual((await dispatch(DemoRuntime(), "POST", "/unknown"))[0], 404)

    def test_claim_cannot_change_value_or_scope(self):
        claim = asdict(FIXTURES[0])
        self.assertTrue(verify([claim], FIXTURES, "glassleaf"))
        self.assertFalse(verify([dict(claim, value=999)], FIXTURES, "glassleaf"))
        self.assertFalse(verify([claim], FIXTURES, "other"))

    async def test_cancel_propagates(self):
        runtime = DemoRuntime(timeout=1, faults={"reference": "timeout"})
        task = asyncio.create_task(runtime.run(self.request()))
        await asyncio.sleep(0)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task


if __name__ == "__main__":
    unittest.main()
