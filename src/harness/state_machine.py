"""종료 상태를 포함한 허용 전이를 명시한다."""
from enum import Enum
from .trajectory import Trajectory


class State(str, Enum):
    CREATED = "CREATED"
    PLANNING = "PLANNING"
    EXECUTING = "EXECUTING"
    OBSERVING = "OBSERVING"
    VERIFYING = "VERIFYING"
    REFLECTING = "REFLECTING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


TERMINAL = {State.COMPLETED, State.FAILED, State.CANCELLED}
NEXT = {
    State.CREATED: {State.PLANNING}, State.PLANNING: {State.EXECUTING},
    State.EXECUTING: {State.OBSERVING}, State.OBSERVING: {State.VERIFYING},
    State.VERIFYING: {State.COMPLETED, State.REFLECTING},
    State.REFLECTING: {State.RETRYING}, State.RETRYING: {State.EXECUTING},
}


class Machine:
    def __init__(self):
        self.state = State.CREATED
        self.trace = Trajectory()
        self.trace.append(self.state.value)

    def move(self, target, **details):
        target = State(target)
        if self.state in TERMINAL or (target not in NEXT.get(self.state, set())
                                     and target not in {State.FAILED, State.CANCELLED}):
            raise ValueError("invalid state transition")
        self.state = target
        self.trace.append(target.value, **details)
