"""합성 근거로 실행 경계를 보여주는 독립 예제다. LLM이나 운영 API는 호출하지 않는다."""

from __future__ import annotations

import asyncio
from dataclasses import asdict, dataclass
import hashlib
import json
import re


@dataclass(frozen=True)
class Fact:
    key: str
    subject: str
    metric: str
    value: int
    unit: str


# 실제 작물·가격·처방과 관계없는 공개 예제 전용 값이다.
FIXTURES = (
    Fact("demo-growth", "glassleaf", "growth", 12, "synthetic_points"),
    Fact("demo-moisture", "glassleaf", "moisture", 7, "synthetic_points"),
)
TOOL_FOR = {"growth": "reference", "moisture": "observation"}


def digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def verify(claims, evidence, subject):
    """출처 존재뿐 아니라 주장 전체와 대상 일치를 검사한다."""
    index = {f.key: asdict(f) for f in evidence}
    return all(c == index.get(c.get("key")) and c.get("subject") == subject for c in claims)


class DemoRuntime:
    def __init__(self, *, max_calls=2, timeout=0.05, faults=None):
        if type(max_calls) is not int or not 1 <= max_calls <= 4:
            raise ValueError("invalid_budget")
        if type(timeout) not in (int, float) or not 0 < timeout <= 5:
            raise ValueError("invalid_timeout")
        self.max_calls, self.timeout = max_calls, timeout
        self.faults = dict(faults or {})
        self.memory = {}
        self.calls = 0

    async def tool(self, name, subject, metric):
        self.calls += 1
        mode = self.faults.get(name)
        if mode == "timeout":
            await asyncio.sleep(self.timeout + 1)
        if mode == "error":
            raise RuntimeError("injected_failure")
        if mode == "empty":
            return ()
        return tuple(f for f in FIXTURES if (f.subject, f.metric) == (subject, metric))

    async def _call(self, name, subject, metric):
        try:
            found = await asyncio.wait_for(self.tool(name, subject, metric), self.timeout)
            return {"tool": name, "metric": metric, "status": "found" if found else "empty"}, found
        except asyncio.TimeoutError:
            return {"tool": name, "metric": metric, "status": "timeout"}, ()
        except Exception:
            # 도구 예외 원문에 비밀정보가 있을 수 있어 고정 상태만 반환한다.
            return {"tool": name, "metric": metric, "status": "error"}, ()

    async def run(self, request):
        if not isinstance(request, dict) or set(request) - {"session", "subject", "needs", "mode"}:
            raise ValueError("invalid_request")
        session, subject = request.get("session"), request.get("subject")
        if any(not isinstance(v, str) or not re.fullmatch(r"[a-z0-9-]{1,40}", v)
               for v in (session, subject)):
            raise ValueError("invalid_scope")
        mode = request.get("mode", "answer")
        if mode not in ("answer", "summary"):
            raise ValueError("unsupported_mode")
        events = ["guard", "structured_task"]
        if mode == "summary":
            if request.get("needs"):
                raise ValueError("summary_cannot_search")
            previous = self.memory.get((session, subject))
            # 요약은 저장된 검증본만 재사용하며 검색이나 새 출처를 만들지 않는다.
            return {"status": "reused" if previous else "missing_context",
                    "answer": previous["answer"] if previous else "No matching session context.",
                    "sources": list(previous["sources"]) if previous else [],
                    "events": events + ["memory_read", "response"], "tool_calls": 0,
                    "disclosure": "Reconstructed Public Demo"}
        needs = request.get("needs")
        if (not isinstance(needs, list) or not 1 <= len(needs) <= 4
                or any(not isinstance(n, str) or n not in TOOL_FOR for n in needs)):
            raise ValueError("invalid_needs")
        plan = list(dict.fromkeys(needs))
        if len(plan) > self.max_calls:
            raise ValueError("budget_exceeded")
        events += ["plan", "select", "execute"]
        results = await asyncio.gather(*(self._call(TOOL_FOR[n], subject, n) for n in plan))
        statuses = [status for status, _ in results]
        evidence = tuple(f for _, found in results for f in found)
        events += ["observe", "evidence_check"]
        claims = [asdict(f) for f in evidence]
        accepted = verify(claims, evidence, subject)
        covered = {f.metric for f in evidence}
        missing = [n for n in plan if n not in covered]
        # 생성기는 의도적으로 단순 템플릿이다. 이 코드가 자연어 이해 모델은 아니다.
        answer = "\n".join(f"{f.subject}: {f.metric} = {f.value} {f.unit} [{f.key}]"
                           for f in evidence) if accepted else ""
        if missing:
            answer += "\nUnresolved: " + ", ".join(missing)
        answer = answer.strip() or "No supported claim."
        status = "complete" if accepted and not missing else "partial" if evidence else "unresolved"
        events += ["template_generation", "verification", "review", "response"]
        artifact = {"claims": claims, "subject": subject, "needs": plan, "version": "demo-1"}
        sources = [f.key for f in evidence]
        result = {"status": status, "answer": answer, "claims": claims, "sources": sources,
                  "missing": missing, "tool_status": statuses, "tool_calls": len(plan),
                  "events": events, "artifact_sha256": digest(artifact),
                  "disclosure": "Reconstructed Public Demo"}
        self.memory[(session, subject)] = {"answer": answer, "sources": tuple(sources)}
        return result


async def dispatch(runtime, method, path, payload=None):
    """네트워크 서버가 아닌 신규 공개 샘플 계약의 실행 가능한 라우터다."""
    if (method, path) == ("POST", "/api/demo/agent/query"):
        try:
            return 200, await runtime.run(payload)
        except ValueError as error:
            return 400, {"error": str(error)}
    if (method, path) == ("GET", "/api/demo/health"):
        return 200, {"mode": "offline_mock", "production_connected": False}
    return 404, {"error": "route_not_found"}


async def demo():
    runtime = DemoRuntime()
    request = {"session": "demo", "subject": "glassleaf", "needs": ["growth", "moisture"]}
    _, answer = await dispatch(runtime, "POST", "/api/demo/agent/query", request)
    print(json.dumps(answer, indent=2))
    summary = await runtime.run({"session": "demo", "subject": "glassleaf", "mode": "summary"})
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    asyncio.run(demo())
