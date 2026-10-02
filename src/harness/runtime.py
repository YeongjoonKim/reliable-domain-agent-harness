"""제한된 병렬 도구 실행과 검증 실패 후 복구를 조정한다."""
import asyncio
from dataclasses import asdict
import time
from .models import claim_from, digest
from .policies import Policy
from .reflection import recovery_reason
from .state_machine import Machine, State, TERMINAL
from .verifier import verify


def propose(needs, observations):
    # 기준선과 하네스가 같은 단순 후보 생성기를 사용한다. 의미 검증은 별도다.
    rows = [row for obs in observations for row in obs["evidence"]]
    claims = []
    for need in needs:
        candidates = [row for row in rows if row["subject"] == need.subject and row["metric"] == need.metric]
        candidates = candidates or [row for row in rows if row["subject"] == need.subject]
        if candidates:
            row = max(candidates, key=lambda item: item["observed"])
            claims.append(claim_from(row))
    return claims


class Runtime:
    def __init__(self, registry, policy=None):
        self.registry, self.policy = registry, policy or Policy()
        self.last_machine = None

    async def run(self, needs, plan, proposer=propose):
        if not needs or len({(n.subject, n.metric, n.unit) for n in needs}) != len(needs):
            raise ValueError("distinct information needs required")
        machine, records = Machine(), []
        self.last_machine = machine
        started, calls = time.monotonic(), 0
        report, accepted = None, []
        machine.move(State.PLANNING, input_hash=plan.fingerprint)

        async def execute():
            nonlocal calls, report, accepted
            for attempt, group in enumerate(plan.attempts):
                if attempt > self.policy.max_retry or calls + len(group) > self.policy.max_steps:
                    machine.move(State.FAILED, error_type="budget_exhausted")
                    return
                machine.move(State.EXECUTING)
                calls += len(group)
                observations = await asyncio.gather(*(self.registry.call(call.tool, call.arguments,
                    self.policy.permissions) for call in group))
                machine.move(State.OBSERVING, output_hash=digest(observations))
                for obs in observations:
                    machine.trace.append(State.OBSERVING.value, tool_name=obs["tool"],
                        tool_version=obs["tool_version"], input_hash=obs["input_hash"],
                        output_hash=obs["output_hash"], error_type=obs["status"], latency_ms=obs["latency_ms"])
                claims = proposer(needs, observations)
                machine.move(State.VERIFYING)
                report = verify(needs, claims, observations)
                # 재현 묶음은 원문을 포함하므로 추적과 분리하고 호출자가 명시적으로 내보낸다.
                records.append(dict(attempt=attempt, observations=observations, claims=claims, verification=report))
                if report["accepted"]:
                    accepted = claims
                    machine.move(State.COMPLETED, verification="PASS")
                    return
                machine.move(State.REFLECTING, verification="REJECT", retry_reason=",".join(report["reasons"]))
                reason = recovery_reason(report, observations, self.registry)
                if reason is None or attempt == self.policy.max_retry or attempt + 1 == len(plan.attempts):
                    machine.move(State.FAILED, error_type="abstained")
                    return
                machine.move(State.RETRYING, retry_reason=reason)
        try:
            await asyncio.wait_for(execute(), self.policy.timeout)
        except asyncio.TimeoutError:
            machine.move(State.FAILED, error_type="deadline")
        except asyncio.CancelledError:
            machine.move(State.CANCELLED, error_type="caller_cancelled")
            raise
        except Exception:
            if machine.state not in TERMINAL:
                machine.move(State.FAILED, error_type="runtime_error")
            raise
        bundle = dict(schema_version=1, needs=[asdict(need) for need in needs], plan=plan.to_dict(),
                      plan_hash=plan.fingerprint, policy=asdict(self.policy), policy_hash=self.policy.fingerprint,
                      registry_hash=self.registry.fingerprint, records=records)
        bundle["integrity_hash"] = digest(bundle)
        return dict(state=machine.state.value, claims=accepted, verification=report,
                    calls=calls, latency_ms=round((time.monotonic() - started) * 1000, 3),
                    trajectory=machine.trace.events, replay_bundle=bundle)
