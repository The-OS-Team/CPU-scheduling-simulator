"""Priority Scheduling (non-preemptive or preemptive)"""

from src.schedulers.base import Scheduler
from src.models.state import ProcessState

class PriorityScheduler(Scheduler):
    """
    Priority Scheduling (non-preemptive or preemptive optional).
    
    Lower number = higher priority.
    """

    def __init__(self, preemptive=False):
        self.queue = []
        self.preemptive = preemptive

    def add_process(self, process):
        if process.state == ProcessState.READY and process.remaining_time > 0:
            self.queue.append(process)

    def pick_next(self, current_time):
        """Pick process with highest priority (lowest number)."""
        if not self.queue:
            return None

        # sort by priority first, then arrival (tie-breaker)
        self.queue.sort(key=lambda p: (p.priority, p.arrival_time))
        return self.queue[0]

    def time_slice(self, process, current_time):
        if self.preemptive:
            return 1  # simulate interrupt-driven preemption
        return process.remaining_time
 
    def has_work(self):
        self.queue = [p for p in self.queue if p.remaining_time > 0]
        return len(self.queue) > 0