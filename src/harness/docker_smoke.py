"""옵트인 실제 격리 검사와 과학 계산 세로 경로를 실행한다."""
import argparse
import asyncio
import json
from pathlib import Path
from .models import Need
from .planner import Call, Plan
from .policies import Policy
from .runtime import Runtime
from .sandbox import SandboxPolicy, run_python
from .scientific import add_isolated_tool
from .tools import make_registry


async def smoke(image):
    policy = SandboxPolicy(image)
    code = """import json, os, socket
checks = {"uid": os.getuid(), "cwd": os.getcwd()}
try:
    open('/root-probe', 'w').close()
    checks['root_readonly'] = False
except OSError:
    checks['root_readonly'] = True
try:
    socket.create_connection(('example.com', 443), timeout=1)
    checks['network_blocked'] = False
except OSError:
    checks['network_blocked'] = True
open('scratch', 'w').write('isolated')
checks['scratch_writable'] = True
print(json.dumps(checks))
"""
    isolation = run_python(code, policy)
    checks = json.loads(isolation["stdout"])
    assert isolation["status"] == "ok" and isolation["cleanup"]
    assert checks == dict(uid=65534, cwd="/work", root_readonly=True, network_blocked=True, scratch_writable=True)
    timeout = run_python("import time; time.sleep(20)", SandboxPolicy(image, timeout=2))
    assert timeout["status"] == "timeout" and timeout["cleanup"]
    overflow = run_python("print('x' * 100000)", SandboxPolicy(image, output_limit=1024))
    assert overflow["status"] == "output_limit" and overflow["cleanup"]
    failure = run_python("import sys; print('controlled failure', file=sys.stderr); sys.exit(3)", policy)
    assert failure["status"] == "execution_error" and failure["exit_code"] == 3 and failure["cleanup"]
    registry, artifacts = make_registry(), []
    add_isolated_tool(registry, policy, artifacts)
    needs = [Need("dataset", "mean", "units"), Need("dataset", "sample_variance", "units_squared")]
    run = await Runtime(registry, Policy(timeout=30, permissions=("compute:isolated",))).run(
        needs, Plan(((Call("isolated_numerical_analysis", {"values": [2, 4, 6, 8, 10]}),),)))
    assert run["state"] == "COMPLETED"
    return dict(kind="actual local Docker integration; not a mock", isolation=checks,
                timeout=timeout["status"], output_limit=overflow["status"], exit_code=failure["exit_code"],
                all_cleanup=True, artifact=artifacts[0], verification=run["verification"],
                trajectory=run["trajectory"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Already installed local sha256 image ID")
    args = parser.parse_args()
    result = asyncio.run(smoke(args.image))
    Path("examples/docker-validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in ("kind", "isolation", "timeout", "all_cleanup")}, indent=2))
