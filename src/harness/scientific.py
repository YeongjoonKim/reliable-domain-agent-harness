"""격리 계산 결과를 입력 데이터에서 독립 재계산한 값과 비교한다."""
import asyncio
import json
import math
from .models import digest
from .registry import ToolSpec, validate
from .sandbox import run_python
from .tools import NUMERIC, OUTPUT, numeric_rows


def check_statistics(values, actual):
    # 도구의 statistics 구현과 다른 계산식으로 산출물을 교차 검사한다.
    mean = math.fsum(values) / len(values)
    expected = dict(count=len(values), mean=mean, minimum=min(values), maximum=max(values),
                    sample_variance=math.fsum((value - mean) ** 2 for value in values) / (len(values) - 1))
    return (set(actual) == set(expected) and all(type(actual[k]) in (int, float)
            and math.isfinite(actual[k]) and math.isclose(actual[k], v, rel_tol=1e-10, abs_tol=1e-10)
            for k, v in expected.items()))


def analyze(values, policy):
    validate({"values": values}, NUMERIC)
    code = ("import json, statistics\nv = " + repr(values) + "\n"
            "print(json.dumps(dict(count=len(v), mean=statistics.mean(v), "
            "sample_variance=statistics.variance(v), minimum=min(v), maximum=max(v))))")
    execution = run_python(code, policy)
    if execution["status"] != "ok" or not execution["cleanup"]:
        raise RuntimeError("isolated analysis failed")
    result = json.loads(execution["stdout"])
    if not check_statistics(values, result):
        raise ValueError("numerical result rejected")
    artifact = dict(dataset_hash=digest(values), result=result, result_hash=digest(result),
                    image=policy.image, method="sample variance (n-1)", verification="PASS",
                    execution=execution)
    return artifact


def add_isolated_tool(registry, policy, artifacts):
    async def handler(arguments):
        # Docker 실행은 호출이 취소되더라도 자체 deadline과 finally 정리를 수행한다.
        artifact = await asyncio.to_thread(analyze, arguments["values"], policy)
        artifacts.append(artifact)
        return {"evidence": numeric_rows(arguments["values"], artifact["result"])}
    registry.register(ToolSpec("isolated_numerical_analysis", "1.0", "Isolated descriptive statistics",
                               NUMERIC, OUTPUT, "compute:isolated", timeout=min(policy.timeout + 12, 60)), handler)
