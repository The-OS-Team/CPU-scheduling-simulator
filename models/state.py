"""Process states enumeration."""
from enum import Enum


class ProcessState(Enum):
    """Possible states for a process."""
    READY = "READY"
    RUNNING = "RUNNING"
    BLOCKED = "BLOCKED"
    FINISHED = "FINISHED"
