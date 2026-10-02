"""동일 후보 생성기를 사용하는 합성 기준선 대 하네스 비교 평가다."""
import asyncio
from dataclasses import asdict
import json
from pathlib import Path
import time
from .models import Need, evidence
from .planner import Call, Plan
from .runtime import Runtime, propose
from .tools import make_registry


CATEGORIES = ("single_tool", "multi_tool", "irrelevant", "conflicting", "missing",
              "timeout", "tool_failure", "retry_recovery", "unsupported_claim", "numeric",
              "stale", "invalid_span")


def cases():
    result = []
    for variant in range(2):
        for category in CATEGORIES:
            crop, value = ("glassleaf", 42) if variant == 0 else ("silverroot", 19)
            good = evidence("area", crop, "cultivated_area", value, "ha")
            wrong = evidence("guide", crop, "watering_interval", 3, "days")
            fixtures, faults = {"initial": [good], "fallback": [good]}, {}
            needs = [Need(crop, "cultivated_area", "ha")]
            attempts = ((Call("document_lookup", {"key": "initial"}),),)
            expected, mutation = [value], None
            if category in {"irrelevant", "retry_recovery"}:
                fixtures["initial"] = [wrong]
                if category == "retry_recovery":
                    attempts += ((Call("structured_lookup", {"key": "fallback"}),),)
                else:
                    expected = None
            elif category == "multi_tool":
                fixtures["moisture"] = [evidence("moisture", crop, "moisture", 7, "points")]
                needs.append(Need(crop, "moisture", "points"))
                attempts = (attempts[0] + (Call("structured_lookup", {"key": "moisture"}),),)
                expected.append(7)
            elif category == "conflicting":
                fixtures["initial"].append(evidence("conflict", crop, "cultivated_area", value + 10, "ha"))
                expected = None
            elif category == "missing":
                fixtures["initial"] = []
                expected = None
            elif category in {"timeout", "tool_failure"}:
                faults["initial"] = "timeout" if category == "timeout" else "error"
                attempts += ((Call("structured_lookup", {"key": "fallback"}),),)
            elif category == "unsupported_claim":
                mutation, expected = "value", None
            elif category == "invalid_span":
                mutation, expected = "span", None
            elif category == "stale":
                fixtures["initial"] = [evidence("old", crop, "cultivated_area", value, "ha", "2025-01-01")]
                expected = None
            elif category == "numeric":
                values = [1, 2, 3] if variant == 0 else [2, 4, 6]
                needs = [Need("dataset", "mean", "units")]
                attempts = ((Call("numerical_analysis", {"values": values}),),)
                expected = [2 if variant == 0 else 4]
            result.append(dict(id=f"{category}-{variant + 1}", category=category, needs=needs,
                               fixtures=fixtures, faults=faults, plan=Plan(attempts), expected=expected,
                               mutation=mutation))
    return result


def candidate_function(case):
    def generate(needs, observations):
        claims = propose(needs, observations)
        if claims and case["mutation"] == "value":
            claims[0]["value"] += 100
        if claims and case["mutation"] == "span":
            claims[0]["start"] = 0
        return claims
    return generate


def score(case, claims):
    # 평가 정답은 검증기의 판정이 아니라 케이스의 별도 기대값이다.
    if case["expected"] is None:
        return not claims
    return (len(claims) == len(case["needs"]) and all(
        (claim["subject"], claim["metric"], claim["unit"], claim["value"]) ==
        (need.subject, need.metric, need.unit, value)
        for claim, need, value in zip(claims, case["needs"], case["expected"])))


async def evaluate():
    outcomes = []
    for case in cases():
        registry = make_registry(case["fixtures"], case["faults"])
        generate = candidate_function(case)
        start = time.monotonic()
        observations = await asyncio.gather(*(registry.call(call.tool, call.arguments,
            ("read:synthetic", "compute:trusted")) for call in case["plan"].attempts[0]))
        baseline_claims = generate(case["needs"], observations)
        baseline = dict(success=score(case, baseline_claims), calls=len(observations),
                        latency_ms=round((time.monotonic() - start) * 1000, 3),
                        unsafe_answer=bool(baseline_claims) and not score(case, baseline_claims))
        run = await Runtime(registry).run(case["needs"], case["plan"], generate)
        harness = dict(success=score(case, run["claims"]), calls=run["calls"], latency_ms=run["latency_ms"],
                       unsafe_answer=bool(run["claims"]) and not score(case, run["claims"]), state=run["state"])
        outcomes.append(dict(id=case["id"], category=case["category"], baseline=baseline, harness=harness))
    summary = {}
    for arm in ("baseline", "harness"):
        summary[arm] = dict(cases=len(outcomes), task_success=sum(row[arm]["success"] for row in outcomes),
                            unsafe_answers=sum(row[arm]["unsafe_answer"] for row in outcomes),
                            average_calls=sum(row[arm]["calls"] for row in outcomes) / len(outcomes),
                            average_latency_ms=sum(row[arm]["latency_ms"] for row in outcomes) / len(outcomes))
    return dict(kind="paired synthetic evaluation; not an independent LLM benchmark",
                dataset_version="synthetic-1", categories=len(CATEGORIES), summary=summary, cases=outcomes)


def main():
    output = asyncio.run(evaluate())
    destination = Path("examples/paired-evaluation.json")
    destination.write_text(json.dumps(output, indent=2) + "\n")
    fixture = [dict(id=case["id"], category=case["category"], needs=[asdict(n) for n in case["needs"]],
                    fixtures=case["fixtures"], faults=case["faults"], plan=case["plan"].to_dict(),
                    expected=case["expected"], mutation=case["mutation"]) for case in cases()]
    Path("examples/evaluation-cases.json").write_text(json.dumps(fixture, indent=2) + "\n")
    print(json.dumps(output["summary"], indent=2))


if __name__ == "__main__":
    main()
