"""회사 데이터와 무관한 합성 자료 및 신뢰된 수치 계산 도구다."""
import asyncio
import copy
import statistics
from .models import evidence, digest
from .registry import Registry, ToolSpec


def object_schema(properties, required=None):
    return dict(type="object", properties=properties,
                required=list(properties) if required is None else required,
                additionalProperties=False)


ROW = object_schema({
    **{key: {"type": "string"} for key in
       ("evidence_id", "source_id", "subject", "metric", "unit", "observed", "body", "source_hash")},
    "value": {"type": "number"}, "start": {"type": "integer"}, "end": {"type": "integer"},
})
OUTPUT = object_schema({"evidence": {"type": "array", "items": ROW, "maxItems": 20}})
LOOKUP = object_schema({"key": {"type": "string", "maxLength": 80}})
NUMERIC = object_schema({"values": {"type": "array", "items": {"type": "number"},
                                    "minItems": 2, "maxItems": 1000}})


def summary(values):
    return dict(count=len(values), mean=statistics.mean(values),
                sample_variance=statistics.variance(values), minimum=min(values), maximum=max(values))


def numeric_rows(values, result=None):
    result = summary(values) if result is None else result
    rows = [evidence("numeric-" + metric, "dataset", metric, value,
                     "count" if metric == "count" else "units_squared" if metric == "sample_variance" else "units")
            for metric, value in result.items()]
    for row in rows:
        row["source_id"] = "synthetic:dataset:" + digest(values)
    return rows


def make_registry(fixtures=None, faults=None):
    fixtures, faults = copy.deepcopy(fixtures or {}), dict(faults or {})
    registry = Registry()

    async def lookup(arguments):
        key = arguments["key"]
        if faults.get(key) == "timeout":
            await asyncio.sleep(1)
        if faults.get(key) == "error":
            raise RuntimeError("synthetic failure")
        return {"evidence": copy.deepcopy(fixtures.get(key, []))}

    async def numeric(arguments):
        return {"evidence": numeric_rows(arguments["values"])}

    for name in ("structured_lookup", "document_lookup"):
        registry.register(ToolSpec(name, "1.0", "Read synthetic " + name, LOOKUP, OUTPUT,
                                   "read:synthetic", timeout=0.02), lookup)
    registry.register(ToolSpec("numerical_analysis", "1.0", "Descriptive statistics of synthetic data",
                               NUMERIC, OUTPUT, "compute:trusted"), numeric)
    return registry
