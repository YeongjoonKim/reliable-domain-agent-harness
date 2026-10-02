"""도구 호출 수, 재시도와 실행 시간을 독립적으로 제한한다."""
from dataclasses import dataclass, asdict
import math
from .models import digest


@dataclass(frozen=True)
class Policy:
    max_steps: int = 6
    max_retry: int = 2
    timeout: float = 3.0
    permissions: tuple = ("read:synthetic", "compute:trusted")
    version: str = "public-policy-1"

    def __post_init__(self):
        if (type(self.max_steps) is not int or not 1 <= self.max_steps <= 30
                or type(self.max_retry) is not int or not 0 <= self.max_retry <= 5
                or not math.isfinite(self.timeout) or not 0 < self.timeout <= 120):
            raise ValueError("invalid runtime budget")

    @property
    def fingerprint(self):
        return digest(asdict(self))
