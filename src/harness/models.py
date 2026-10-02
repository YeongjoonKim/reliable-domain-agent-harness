"""정보 요구, 관측 근거와 주장 계약을 분리한다."""
from dataclasses import asdict, dataclass
from datetime import date
import hashlib
import json
import math


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     allow_nan=False, separators=(",", ":")).encode()).hexdigest()


@dataclass(frozen=True)
class Need:
    subject: str
    metric: str
    unit: str
    as_of: str = "2026-10-01"
    max_age_days: int = 60

    def __post_init__(self):
        date.fromisoformat(self.as_of)
        if not all((self.subject, self.metric, self.unit)) or self.max_age_days < 0:
            raise ValueError("invalid information need")


def statement(subject, metric, value, unit, observed):
    # 신뢰된 정형 어댑터의 표준 표현이며 일반 자연어 의미 분석기는 아니다.
    return json.dumps(dict(subject=subject, metric=metric, value=value,
                           unit=unit, observed=observed), sort_keys=True)


def evidence(identifier, subject, metric, value, unit, observed="2026-09-20"):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError("finite numeric evidence required")
    text = statement(subject, metric, value, unit, observed)
    body = "Synthetic observation.\n" + text + "\nEnd of observation."
    start = body.index(text)
    return dict(evidence_id=identifier, source_id="synthetic:" + identifier,
                subject=subject, metric=metric, value=value, unit=unit, observed=observed,
                body=body, source_hash=digest(body), start=start, end=start + len(text))


def claim_from(row):
    keys = ("subject", "metric", "value", "unit", "evidence_id", "start", "end")
    return {key: row[key] for key in keys}


def need_dict(need):
    return asdict(need)
