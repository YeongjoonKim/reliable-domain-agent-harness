"""실행 경로에서 스키마, 권한, 제한 시간과 버전을 강제한다."""
import asyncio
from dataclasses import asdict, dataclass
import math
import time
from .models import digest


def validate(value, schema):
    # 공개 예제에서 사용하는 JSON Schema 부분집합만 지원한다.
    kind = schema.get("type")
    types = {"object": dict, "array": list, "string": str, "number": (int, float),
             "integer": int, "boolean": bool}
    if kind not in types or not isinstance(value, types[kind]):
        raise ValueError("schema type mismatch")
    if kind in {"number", "integer"} and (isinstance(value, bool) or not math.isfinite(value)):
        raise ValueError("finite number required")
    if kind == "object":
        if set(schema.get("required", [])) - set(value):
            raise ValueError("missing field")
        props = schema.get("properties", {})
        if schema.get("additionalProperties") is False and set(value) - set(props):
            raise ValueError("unknown field")
        for key, item in value.items():
            if key in props:
                validate(item, props[key])
    if kind == "array":
        if not schema.get("minItems", 0) <= len(value) <= schema.get("maxItems", 10000):
            raise ValueError("array size")
        for item in value:
            validate(item, schema["items"])
    if kind == "string" and len(value) > schema.get("maxLength", 10000):
        raise ValueError("string size")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    version: str
    description: str
    input_schema: dict
    output_schema: dict
    permission: str
    timeout: float = 0.2
    retry_policy: tuple = ("timeout", "tool_error")


class Registry:
    def __init__(self):
        self.specs, self.handlers = {}, {}

    def register(self, spec, handler):
        if spec.name in self.specs or not 0 < spec.timeout <= 60:
            raise ValueError("invalid or duplicate tool")
        self.specs[spec.name], self.handlers[spec.name] = spec, handler

    @property
    def fingerprint(self):
        return digest({name: asdict(spec) for name, spec in sorted(self.specs.items())})

    async def call(self, name, arguments, permissions):
        started = time.monotonic()
        spec = self.specs.get(name)
        result = dict(tool=name, tool_version=spec.version if spec else "unknown",
                      input_hash=digest(arguments), status="ok", evidence=[])
        try:
            if spec is None:
                raise LookupError("unknown tool")
            if spec.permission not in permissions:
                raise PermissionError("permission denied")
            validate(arguments, spec.input_schema)
            output = await asyncio.wait_for(self.handlers[name](arguments), spec.timeout)
            validate(output, spec.output_schema)
            result["evidence"] = output["evidence"]
        except asyncio.TimeoutError:
            result["status"] = "timeout"
        except PermissionError:
            result["status"] = "denied"
        except LookupError:
            result["status"] = "unknown_tool"
        except ValueError:
            result["status"] = "schema_error"
        except Exception:
            # 내부 예외 메시지는 추적이나 공개 응답에 복사하지 않는다.
            result["status"] = "tool_error"
        result["output_hash"] = digest(result["evidence"])
        result["latency_ms"] = round((time.monotonic() - started) * 1000, 3)
        return result
