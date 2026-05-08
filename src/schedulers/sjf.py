"""Shortest Job First (SJF) scheduler - non-preemptive."""

from src.schedulers.base import Scheduler
from src.models.state import ProcessState
import heapq


class SJF(Scheduler):
    """
    Shortest Job First Scheduler (non-preemptive).

    Picks process with shortest burst/remaining time.
    """

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

            _, _, _, process = heapq.heappop(self.heap)

            if (
                process.state != ProcessState.FINISHED
                and process.remaining_time > 0
            ):
                return process

        return None

    def time_slice(self, process):
        """
        Non-preemptive:
        run process until completion.
        """

        return process.remaining_time

    def requeue(self, process):
        """
        SJF is non-preemptive.

        Engine should never requeue unfinished work here,
        but method exists for interface consistency.
        """
        pass

    def has_work(self):
        return len(self.heap) > 0