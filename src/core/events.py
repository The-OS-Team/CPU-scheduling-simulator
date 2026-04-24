"""Event handling for process arrivals and completions."""
from enum import Enum


class EventType(Enum):
    """Types of events in the simulation."""
    ARRIVAL = "ARRIVAL"
    COMPLETION = "COMPLETION"
    PREEMPTION = "PREEMPTION"


class Event:
    """Represents an event in the simulation."""
    
    def __init__(self, event_type:EventType, time, process=None):
        self.event_type = event_type
        self.time = time
        self.process = process
    
    def __lt__(self, other):
        """For priority queue ordering."""
        return self.time < other.time
    
    def __repr__(self):
        return f"Event({self.event_type.value} at time={self.time}, process={self.process})"
