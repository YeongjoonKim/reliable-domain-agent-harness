"""공개 런타임을 실제 실행해 화면과 문서에서 검토할 합성 snapshot을 만든다."""
import asyncio
import json
from .sample_agent import DemoRuntime, FIXTURES, verify


async def snapshot():
    request = {"session": "public-demo", "subject": "glassleaf", "needs": ["growth", "moisture"]}
    runtime = DemoRuntime()
    complete = await runtime.run(request)
    summary = await runtime.run({"session": "public-demo", "subject": "glassleaf", "mode": "summary"})
    partial = await DemoRuntime(faults={"observation": "timeout"}).run(request)
    altered = [dict(complete["claims"][0], value=999)]
    checks = {
        "complete_has_two_sources": len(complete["sources"]) == 2,
        "partial_preserves_one_source": len(partial["sources"]) == 1,
        "summary_has_no_new_calls": summary["tool_calls"] == 0,
        "summary_preserves_sources": summary["sources"] == complete["sources"],
        "tampered_value_rejected": not verify(altered, FIXTURES, "glassleaf"),
    }
    return {"scope": "executed_offline_synthetic_snapshot_not_production",
            "request": request, "cases": {"complete": complete, "partial": partial, "summary": summary},
            "probe_checks": checks,
            "limitations": ["No live LLM or external connector", "Logical events are not latency measurements"]}


def build():
    return asyncio.run(snapshot())


if __name__ == "__main__":
    print(json.dumps(build(), indent=2, ensure_ascii=False))
