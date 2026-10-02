"""외부 도구 호출 없이 설정과 저장 근거를 재검증한다. 서명 검증은 아니다."""
from .models import Need, digest
from .verifier import verify


def replay(bundle, registry, policy):
    unsigned = {key: value for key, value in bundle.items() if key != "integrity_hash"}
    if digest(unsigned) != bundle["integrity_hash"]:
        raise ValueError("bundle integrity mismatch")
    if (bundle["schema_version"] != 1 or registry.fingerprint != bundle["registry_hash"]
            or policy.fingerprint != bundle["policy_hash"]
            or digest(bundle["policy"]) != bundle["policy_hash"]
            or digest(bundle["plan"]) != bundle["plan_hash"]):
        raise ValueError("configuration mismatch")
    needs = [Need(**item) for item in bundle["needs"]]
    reports = []
    for record in bundle["records"]:
        group = bundle["plan"][record["attempt"]]
        if len(group) != len(record["observations"]):
            raise ValueError("observation count mismatch")
        for call, obs in zip(group, record["observations"]):
            if (call["tool"] != obs["tool"] or digest(call["arguments"]) != obs["input_hash"]
                    or registry.specs[obs["tool"]].version != obs["tool_version"]
                    or digest(obs["evidence"]) != obs["output_hash"]):
                raise ValueError("observation mismatch")
        report = verify(needs, record["claims"], record["observations"])
        if report != record["verification"]:
            raise ValueError("verification drift")
        reports.append(report)
    return dict(mode="configuration/evidence replay", external_calls=0, reports=reports)
