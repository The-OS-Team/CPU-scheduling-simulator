"""Priority Scheduling (preemptive/non-preemptive)."""

from src.schedulers.base import Scheduler
from src.models.state import ProcessState
import heapq


class PriorityScheduler(Scheduler):
    """
    Priority Scheduling Scheduler.

    Lower priority number = higher priority.

    Supports:
    - Non-preemptive
    - Preemptive
    """

    def __init__(self, preemptive=False):
        self.preemptive = preemptive
        self.heap = []

    def add_process(self, process):

        if process.remaining_time <= 0:
            return

        heapq.heappush(
            self.heap,
            (
                process.priority,
                process.arrival_time,
                process.pid,
                process
            )
        )

    def pick_next(self):

        while self.heap:

            _, _, _, process = heapq.heappop(self.heap)

            if (
                process.state != ProcessState.FINISHED
                and process.remaining_time > 0
            ):
                return process

        return None

    def time_slice(self, process, current_time, next_arrival):

        # NON-PREEMPTIVE:
        # Run until completion
        if not self.preemptive:
            return process.remaining_time

        # PREEMPTIVE:
        # Only important event is next arrival
        if next_arrival is None:
            return process.remaining_time

        time_until_arrival = next_arrival - current_time

        return min(process.remaining_time, time_until_arrival)

    def requeue(self, process):

        if process.remaining_time > 0:
            self.add_process(process)

    def has_work(self):
        return len(self.heap) > 0
