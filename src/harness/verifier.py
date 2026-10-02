"""검색 성공, 적합성, 주장 지지와 인용 구간을 별도로 검사한다."""
from datetime import date
from .models import digest, statement


def verify(needs, claims, observations):
    pairs = [(row, obs) for obs in observations if obs["status"] == "ok" for row in obs["evidence"]]
    reasons, provenance = [], []
    signals = dict(retrieval_success=bool(pairs), evidence_relevance=False,
                   claim_support=False, citation_valid=False)
    if not pairs:
        reasons.append("missing_evidence")
    relevant = [(row, obs) for row, obs in pairs
                if any((row["subject"], row["metric"], row["unit"]) ==
                       (need.subject, need.metric, need.unit) for need in needs)]
    signals["evidence_relevance"] = bool(relevant)
    if pairs and not relevant:
        reasons.append("irrelevant_evidence")
    supported, cited = 0, 0
    for need in needs:
        selected = [(row, obs) for row, obs in relevant if
                    (row["subject"], row["metric"], row["unit"]) == (need.subject, need.metric, need.unit)]
        fresh = []
        for row, obs in selected:
            try:
                age = (date.fromisoformat(need.as_of) - date.fromisoformat(row["observed"])).days
            except ValueError:
                age = -1
            if not 0 <= age <= need.max_age_days:
                reasons.append("stale_or_future_evidence")
            else:
                fresh.append((row, obs))
        # 동일 기준 시점 자료끼리만 충돌로 취급한다. 서로 다른 시점은 최신 자료를 선택한다.
        latest = max((row["observed"] for row, _ in fresh), default=None)
        current = [(row, obs) for row, obs in fresh if row["observed"] == latest]
        if len({row["value"] for row, _ in current}) > 1:
            reasons.append("conflicting_evidence")
        matching = [claim for claim in claims if (claim.get("subject"), claim.get("metric"),
                    claim.get("unit")) == (need.subject, need.metric, need.unit)]
        if len(matching) != 1:
            reasons.append("missing_or_duplicate_claim")
        for claim in matching:
            sources = [(row, obs) for row, obs in current if row["evidence_id"] == claim.get("evidence_id")]
            if (len(sources) != 1 or type(claim.get("value")) not in (int, float)
                    or sources[0][0]["value"] != claim.get("value")):
                reasons.append("unsupported_claim")
                continue
            row, obs = sources[0]
            supported += 1
            start, end = claim.get("start"), claim.get("end")
            exact = statement(row["subject"], row["metric"], row["value"], row["unit"], row["observed"])
            valid = (type(start) is int and type(end) is int and
                     0 <= start < end <= len(row["body"]) and
                     (start, end) == (row["start"], row["end"]) and
                     row["body"][start:end] == exact and digest(row["body"]) == row["source_hash"])
            if not valid:
                reasons.append("invalid_citation")
                continue
            cited += 1
            provenance.append(dict(claim_hash=digest(claim), source_id=row["source_id"],
                                   evidence_id=row["evidence_id"], evidence_span=[start, end],
                                   source_hash=row["source_hash"], tool=obs["tool"],
                                   tool_version=obs["tool_version"], verification_result="PASS"))
    if len(claims) != len(needs):
        reasons.append("unexpected_claim_count")
    signals["claim_support"] = bool(needs) and supported == len(needs)
    signals["citation_valid"] = bool(needs) and cited == len(needs)
    accepted = bool(needs) and all(signals.values()) and not reasons
    return dict(accepted=accepted, signals=signals, reasons=sorted(set(reasons)),
                provenance=provenance if accepted else [])
