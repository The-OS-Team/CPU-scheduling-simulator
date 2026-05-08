"""Shortest Remaining Time First (SRTF) scheduler - preemptive."""

from src.schedulers.base import Scheduler
from src.models.state import ProcessState
import heapq


class SRTF(Scheduler):
    """Shortest Remaining Time First using min-heap."""

    def __init__(self):
        self.heap = []

    def add_process(self, process):

        if process.remaining_time <= 0:
            return

        heapq.heappush(
            self.heap,
            (
                process.remaining_time,
                process.arrival_time,
                process.pid,
                process
            )
        )

    def pick_next(self):

        while self.heap:

            remaining, _, _, process = heapq.heappop(self.heap)

            if process.state != ProcessState.FINISHED \
               and process.remaining_time > 0:

                return process

        return None

    def time_slice(self, process, current_time, next_arrival):

        remaining = process.remaining_time

        if next_arrival is None:
            return remaining

        ## Instead of 1 tick
        ## Nothing important can happen before the next arrival
        time_until_arrival = next_arrival - current_time

        return min(remaining, time_until_arrival)
 
    def requeue(self, process):
        if process.remaining_time > 0:
            self.add_process(process)

    def has_work(self):
        return len(self.heap) > 0
