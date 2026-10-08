"""Export stored, real public-core runs; freshness excludes execution noise only.

The JSON remains untouched runtime output. Normalization is comparison-only and
runs after replay/fixture/trace integrity checks; it is not a replay signature.
"""
import argparse
import asyncio
import copy
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.harness.evaluation import cases, candidate_function, evaluate
from src.harness.models import digest
from src.harness.policies import Policy
from src.harness.replay import replay
from src.harness.runtime import Runtime
from src.harness.state_machine import NEXT, State, TERMINAL
from src.harness.tools import make_registry

GITHUB = "https://github.com/YeongjoonKim/reliable-domain-agent-harness"
JS_PREFIX = "window.CORE_EVIDENCE = "
FILES = ("core-evidence.json", "core-evidence.js")
SOURCE_FILES = tuple("src/harness/" + name + ".py" for name in (
    "evaluation", "models", "planner", "policies", "reflection", "registry",
    "replay", "runtime", "state_machine", "tools", "trajectory", "verifier")) + (
    "scripts/export_demo.py", "tests/test_harness_integration.py")
SCOPE = {
    "kind": "public synthetic core execution",
    "disclosure": "Stored execution of the public Python Core; no live LLM, API, DB or full environment replay.",
    "evaluation_disclosure": "Designed synthetic verification/recovery ablation; not an independent LLM benchmark.",
    "ci_url": GITHUB + "/actions",
}
SCENARIOS = (
    ("valid_evidence", "Valid Evidence", "Exact supporting evidence is accepted.",
     "single_tool-1", "runtime"),
    ("retry_recovery", "Irrelevant Evidence → Recovery",
     "An irrelevant first result is rejected before a bounded alternative lookup succeeds.",
     "retry_recovery-1", "reflection"),
    ("conflicting_evidence", "Conflicting Evidence",
     "Conflicting values at the same observation date cause safe abstention.",
     "conflicting-1", "verifier"),
    ("invalid_citation_span", "Invalid Citation Span",
     "The actual case candidate mutates a citation span; the verifier rejects it.",
     "invalid_span-1", "verifier"),
    ("configuration_evidence_replay", "Configuration / Evidence Replay",
     "The recovery run's original bundle is rechecked without executing tools; this is not a new run or full environment replay.",
     "retry_recovery-1", "replay"),
)


def links_for(source):
    return {"source": GITHUB + "/blob/main/src/harness/" + source + ".py",
            "test": GITHUB + "/blob/main/tests/test_harness_integration.py",
            "execution": "./core-evidence.json"}


def source_hashes():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCE_FILES}


async def build_artifact():
    catalogue = {case["id"]: case for case in cases()}
    runs, scenarios = {}, []
    for identifier, title, description, case_id, source in SCENARIOS:
        case = catalogue[case_id]
        registry, policy = make_registry(case["fixtures"], case["faults"]), Policy()
        if case_id not in runs:
            runs[case_id] = await Runtime(registry, policy).run(
                case["needs"], case["plan"], candidate_function(case))
        # The replay entry reuses the real recovery run, including its run ID and
        # trace. Only the actual replay function is invoked again, never tools.
        run = runs[case_id]
        result = replay(run["replay_bundle"], registry, policy)
        scenarios.append(dict(id=identifier, title=title, description=description,
                              case_id=case_id, run=copy.deepcopy(run), replay=result,
                              links=links_for(source)))
    artifact = dict(schema_version=1, generated_at=datetime.now(timezone.utc).isoformat(),
                    scope=dict(SCOPE, source_files=source_hashes()),
                    evaluation=await evaluate(), scenarios=scenarios)
    validate_artifact(artifact)
    return artifact


def require(condition, message):
    if not condition:
        raise ValueError(message)


def check_time(value):
    require(isinstance(value, str), "timestamp must be a string")
    require(datetime.fromisoformat(value).tzinfo is not None, "timezone required")


def check_latency(value):
    require(type(value) in (int, float) and value >= 0, "invalid execution latency")


def validate_run(run, case, stored_replay):
    require(set(run) == {"state", "claims", "verification", "calls", "latency_ms",
                         "trajectory", "replay_bundle"}, "incomplete or unknown run fields")
    registry, policy = make_registry(case["fixtures"], case["faults"]), Policy()
    bundle = run["replay_bundle"]
    require(bundle["needs"] == [asdict(need) for need in case["needs"]], "case needs drift")
    require(bundle["plan"] == case["plan"].to_dict(), "case plan drift")
    # JSON turns the policy permissions tuple into a list. Compare JSON values.
    require(digest(bundle["policy"]) == digest(asdict(policy)), "case policy drift")
    require(replay(bundle, registry, policy) == stored_replay, "stored replay drift")
    records = bundle["records"]
    require(bool(records), "missing execution records")
    require([record["attempt"] for record in records] == list(range(len(records))), "attempt order drift")
    for record in records:
        calls = bundle["plan"][record["attempt"]]
        for call, observation in zip(calls, record["observations"]):
            require(observation["status"] == "ok", "unexpected demo tool status")
            require(observation["evidence"] == case["fixtures"][call["arguments"]["key"]],
                    "evidence does not match the actual synthetic case")
            check_latency(observation["latency_ms"])
        require(record["claims"] == candidate_function(case)(case["needs"], record["observations"]),
                "candidate generation drift")
    final = records[-1]
    require(run["verification"] == final["verification"], "final verification drift")
    accepted = final["verification"]["accepted"]
    require(run["claims"] == (final["claims"] if accepted else []), "accepted claims drift")
    require(run["state"] == ("COMPLETED" if accepted else "FAILED"), "final state drift")
    observations = [obs for record in records for obs in record["observations"]]
    require(type(run["calls"]) is int and run["calls"] == len(observations), "call count drift")
    check_latency(run["latency_ms"])
    events = run["trajectory"]
    require(bool(events) and events[0]["state"] == "CREATED" and events[-1]["state"] == run["state"],
            "trajectory terminal drift")
    run_id = events[0]["run_id"]
    require(isinstance(run_id, str) and UUID(hex=run_id).hex == run_id, "invalid run UUID")
    for sequence, event in enumerate(events):
        require(type(event["sequence"]) is int and type(event["step_id"]) is int
                and event["run_id"] == run_id and event["sequence"] == sequence
                and event["step_id"] == sequence + 1 and event["agent_role"] == "harness",
                "trajectory identity/order drift")
        require(event["state"] in {state.value for state in State}, "unknown trajectory state")
        if sequence:
            previous, current = State(events[sequence - 1]["state"]), State(event["state"])
            tool_observation = previous == current == State.OBSERVING and "tool_name" in event
            require(previous not in TERMINAL and (tool_observation or current in NEXT.get(previous, set())
                    or current in {State.FAILED, State.CANCELLED}), "invalid trajectory transition")
        if event["state"] == "PLANNING":
            require(event["input_hash"] == bundle["plan_hash"], "planning trace hash drift")
        check_time(event["timestamp"])
        if "latency_ms" in event:
            check_latency(event["latency_ms"])
    group_events = [event for event in events if event["state"] == "OBSERVING" and "tool_name" not in event]
    require([event["output_hash"] for event in group_events] ==
            [digest(record["observations"]) for record in records], "observation trace hash drift")
    tool_events = [event for event in events if "tool_name" in event]
    require(len(tool_events) == len(observations), "tool trace count drift")
    for event, obs in zip(tool_events, observations):
        require(all(event[key] == obs[other] for key, other in (
            ("tool_name", "tool"), ("tool_version", "tool_version"), ("input_hash", "input_hash"),
            ("output_hash", "output_hash"), ("error_type", "status"), ("latency_ms", "latency_ms"))),
            "tool trace observation drift")


def validate_artifact(artifact):
    # Reject non-finite JSON before checking hashes or normalizing execution noise.
    json.dumps(artifact, allow_nan=False)
    require(set(artifact) == {"schema_version", "generated_at", "scope", "evaluation", "scenarios"},
            "incomplete or unknown artifact fields")
    require(type(artifact["schema_version"]) is int and artifact["schema_version"] == 1, "schema version drift")
    check_time(artifact["generated_at"])
    require(artifact["scope"] == dict(SCOPE, source_files=source_hashes()), "source/scope drift")
    catalogue = {case["id"]: case for case in cases()}
    require(len(artifact["scenarios"]) == len(SCENARIOS), "scenario count drift")
    for scenario, spec in zip(artifact["scenarios"], SCENARIOS):
        identifier, title, description, case_id, source = spec
        require(set(scenario) == {"id", "title", "description", "case_id", "run", "replay", "links"},
                "incomplete or unknown scenario fields")
        require((scenario["id"], scenario["title"], scenario["description"], scenario["case_id"]) ==
                (identifier, title, description, case_id), "scenario mapping drift")
        require(scenario["links"] == links_for(source), "scenario link drift")
        for name in ("source", "test"):
            relative = urlsplit(scenario["links"][name]).path.split("/blob/main/", 1)[1]
            require((ROOT / relative).is_file(), "missing source/test link target")
        require((ROOT / "demo" / scenario["links"]["execution"]).resolve() ==
                ROOT / "demo/core-evidence.json", "execution link scope drift")
        validate_run(scenario["run"], catalogue[case_id], scenario["replay"])
    require(artifact["scenarios"][1]["run"] == artifact["scenarios"][4]["run"], "replay must reuse original recovery run")
    evaluation = artifact["evaluation"]
    require(set(evaluation) == {"kind", "dataset_version", "categories", "summary", "cases"}, "evaluation fields drift")
    require(evaluation["kind"] == "paired synthetic evaluation; not an independent LLM benchmark"
            and evaluation["dataset_version"] == "synthetic-1", "evaluation scope drift")
    require([(row["id"], row["category"]) for row in evaluation["cases"]] ==
            [(case["id"], case["category"]) for case in cases()], "evaluation case mapping drift")
    require(evaluation["categories"] == len({case["category"] for case in cases()}), "evaluation categories drift")
    for arm in ("baseline", "harness"):
        rows = [row[arm] for row in evaluation["cases"]]
        for row in rows:
            require(type(row["success"]) is bool and type(row["unsafe_answer"]) is bool
                    and type(row["calls"]) is int and row["calls"] >= 0, "invalid evaluation outcome")
            check_latency(row["latency_ms"])
        expected = dict(cases=len(rows), task_success=sum(row["success"] for row in rows),
                        unsafe_answers=sum(row["unsafe_answer"] for row in rows),
                        average_calls=sum(row["calls"] for row in rows) / len(rows),
                        average_latency_ms=sum(row["latency_ms"] for row in rows) / len(rows))
        require(evaluation["summary"][arm] == expected, "evaluation summary drift")
    return artifact


def semantic_content(artifact):
    """Validate raw hashes first, then normalize only known execution noise.

    Observation-group and bundle hashes are recomputed after normalizing latency
    because they cover that latency. Source, plan, policy and registry hashes are
    never removed or rewritten. Raw exported JSON/JS remains unchanged.
    """
    validate_artifact(artifact)
    result = copy.deepcopy(artifact)
    result["generated_at"] = "<execution timestamp>"
    for scenario in result["scenarios"]:
        run = scenario["run"]
        run["latency_ms"] = 0
        bundle = run["replay_bundle"]
        for record in bundle["records"]:
            for obs in record["observations"]:
                obs["latency_ms"] = 0
        groups = iter(bundle["records"])
        for event in run["trajectory"]:
            event["run_id"], event["timestamp"] = "<execution UUID>", "<execution timestamp>"
            if "latency_ms" in event:
                event["latency_ms"] = 0
            if event["state"] == "OBSERVING" and "tool_name" not in event:
                event["output_hash"] = digest(next(groups)["observations"])
        bundle["integrity_hash"] = digest({key: value for key, value in bundle.items() if key != "integrity_hash"})
    for row in result["evaluation"]["cases"]:
        for arm in ("baseline", "harness"):
            row[arm]["latency_ms"] = 0
    for arm in ("baseline", "harness"):
        result["evaluation"]["summary"][arm]["average_latency_ms"] = 0
    # A loaded JSON policy uses lists where dataclasses use tuples.
    return json.loads(json.dumps(result, allow_nan=False))


def artifact_texts(artifact):
    validate_artifact(artifact)
    return (json.dumps(artifact, ensure_ascii=False, allow_nan=False, indent=2) + "\n",
            JS_PREFIX + json.dumps(artifact, ensure_ascii=True, allow_nan=False, indent=2) + ";\n")


def write_artifacts(artifact, directory):
    texts = artifact_texts(artifact)
    directory.mkdir(parents=True, exist_ok=True)
    for name, text in zip(FILES, texts):
        (directory / name).write_text(text, encoding="utf-8")


def check_artifacts(fresh, directory):
    stored = json.loads((directory / FILES[0]).read_text(encoding="utf-8"))
    script = (directory / FILES[1]).read_text(encoding="utf-8")
    require(script.startswith(JS_PREFIX) and script.endswith(";\n"), "invalid JS data envelope")
    require(digest(json.loads(script[len(JS_PREFIX):-2])) == digest(stored), "UI JS/JSON mismatch")
    require(digest(semantic_content(stored)) == digest(semantic_content(fresh)),
            "stale demo artifact: run --update-demo explicitly")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--update-demo", action="store_true", help="explicitly replace tracked demo evidence")
    mode.add_argument("--check", action="store_true", help="rerun core and check tracked demo evidence without writes")
    args = parser.parse_args(argv)
    directory = ROOT / ("demo" if args.update_demo or args.check else "outputs/demo")
    try:
        artifact = asyncio.run(build_artifact())
        if args.check:
            check_artifacts(artifact, directory)
        else:
            write_artifacts(artifact, directory)
    except (OSError, ValueError, KeyError, TypeError, IndexError) as error:
        print(json.dumps({"mode": "check" if args.check else "write", "ok": False,
                          "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps({"mode": "check" if args.check else "write", "ok": True,
                      "directory": str(directory.relative_to(ROOT)), "scenarios": len(artifact["scenarios"]),
                      "evaluation": artifact["evaluation"]["summary"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
