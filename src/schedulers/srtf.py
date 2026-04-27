"""Shortest Remaining Time First (SRTF) scheduler - preemptive."""

from src.schedulers.base import Scheduler
from src.models.state import ProcessState

class SRTF(Scheduler):
    """Shortest Remaining Time First (Preemptive SJF)."""
    
    def __init__(self):
        self.queue = []

    def add_process(self, process):
        if process.state == ProcessState.READY and process.remaining_time > 0:
            self.queue.append(process)
    
    def pick_next(self):
        """Pick process with shortest remaining time."""
        self.queue = [p for p in self.queue if p.remaining_time > 0 and p.state != ProcessState.FINISHED] 

        if not self.queue:
            return None

        self.queue.sort(key=lambda p: (p.remaining_time, p.arrival_time))
        return self.queue[0]
    
    def time_slice(self, process, current_time):
        """SRTF is preemptive → run only 1 unit."""
        return 1

    def has_work(self):
        self.queue = [p for p in self.queue if p.remaining_time > 0]
        return len(self.queue) > 0