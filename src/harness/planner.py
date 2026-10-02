"""외부 플래너와 연결 가능한 명시적 계획 계약이다. LLM 이해기를 흉내내지 않는다."""
from dataclasses import dataclass
from .models import digest


@dataclass(frozen=True)
class Call:
    tool: str
    arguments: dict


@dataclass(frozen=True)
class Plan:
    attempts: tuple

    def __post_init__(self):
        if not self.attempts or any(not group for group in self.attempts):
            raise ValueError("nonempty plan required")

    @property
    def fingerprint(self):
        return digest(self.to_dict())

    def to_dict(self):
        return [[dict(tool=call.tool, arguments=call.arguments) for call in group] for group in self.attempts]
