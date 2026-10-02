"""실패 이유에 따라 예산 내 대체 계획만 선택한다."""
def recovery_reason(report, observations, registry):
    for obs in observations:
        if obs["status"] != "ok":
            spec = registry.specs.get(obs["tool"])
            if spec is None or obs["status"] not in spec.retry_policy:
                return None
    return ",".join(report["reasons"]) or "retryable_tool_failure"
