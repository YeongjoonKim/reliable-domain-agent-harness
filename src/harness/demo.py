"""관련 없는 최초 근거를 거부한 뒤 재검색에 성공하는 실행 산출물을 만든다."""
import argparse
import asyncio
import json
from pathlib import Path
from .evaluation import cases
from .policies import Policy
from .replay import replay
from .runtime import Runtime
from .tools import make_registry


async def build():
    case = next(item for item in cases() if item["id"] == "retry_recovery-1")
    registry, policy = make_registry(case["fixtures"]), Policy()
    run = await Runtime(registry, policy).run(case["needs"], case["plan"])
    run["replay"] = replay(run["replay_bundle"], registry, policy)
    return run


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update-examples", action="store_true",
                        help="explicitly replace the tracked examples/recovery.json snapshot")
    args = parser.parse_args(argv)
    result = asyncio.run(build())
    directory = Path("examples" if args.update_examples else "outputs")
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "recovery.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(dict(state=result["state"], calls=result["calls"],
                         states=[event["state"] for event in result["trajectory"]],
                         replay_calls=result["replay"]["external_calls"]), indent=2))


if __name__ == "__main__":
    main()
