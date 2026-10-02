"""기본 추적에는 원문 대신 해시와 제어 정보만 저장한다."""
from datetime import datetime, timezone
from uuid import uuid4


class Trajectory:
    def __init__(self):
        self.run_id = uuid4().hex
        self.events = []

    def append(self, state, **details):
        allowed = {"tool_name", "tool_version", "input_hash", "output_hash", "verification",
                   "error_type", "retry_reason", "latency_ms"}
        if set(details) - allowed:
            raise ValueError("raw or unknown trajectory field")
        self.events.append(dict(run_id=self.run_id, step_id=len(self.events) + 1,
                                sequence=len(self.events), state=state,
                                timestamp=datetime.now(timezone.utc).isoformat(),
                                agent_role="harness", **details))
