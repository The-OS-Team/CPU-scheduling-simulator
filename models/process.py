"""Process model for simulation."""
from src.models.state import ProcessState


class Process:
    """Represents a process in the system."""
    
    def __init__(self, pid, arrival_time, burst_time, priority):
        self.pid = pid
        self.arrival_time = arrival_time
        self.total_burst = burst_time
        self.remaining_time = burst_time
        self.priority = priority

        # Metrics
        self.start_time = None
        self.finish_time = None
        self.state = ProcessState.READY
        
    
    def __repr__(self):
        return f"Process(pid={self.pid}, arrival={self.arrival_time}, burst={self.total_burst})"
    
    def __lt__(self, other):
        """Comparison for heap operations."""
        return self.remaining_time < other.remaining_time
    
    def get_turnaround_time(self):
        """Calculate turnaround time."""
        if self.finish_time:
            return self.finish_time - self.arrival_time
        return None
    
    def get_waiting_time(self):
        """Calculate waiting time."""
        if self.start_time:
            return self.start_time - self.arrival_time
        return None
