"""Shortest Job First (SJF) scheduler - non-preemptive."""
from src.schedulers.base import Scheduler


class SJF(Scheduler):
    """Shortest Job First scheduler (non-preemptive)."""
    
    def __init__(self):
        self.queue = []
    
    def add_process(self, process):
        self.queue.append(process)
    
    def pick_next(self):
        """Pick process with shortest remaining time."""
        if not self.queue:
            return None
        
        self.queue.sort(key=lambda p: p.remaining_time)
        return self.queue.pop(0)
    
    def time_slice(self, process, _):
        """Give entire burst time (non-preemptive)."""
        return process.remaining_time
    
    def has_work(self):
        return len(self.queue) > 0
