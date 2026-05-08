"""Metrics collection for simulation results."""


class Metrics:
    """Collects and tracks process execution metrics."""

    def __init__(self):
        self.completed = []
        self.total_time = 0

        # internal cache 
        self._cached_busy_time = None


    def record(self, process):
        """Record a completed process."""
        self.completed.append(process)
        self._cached_busy_time = None  # invalidate cache

    def set_total_time(self, total_time):
        """Set total simulation time."""
        self.total_time = total_time

    # Per-process metrics
    def get_turnaround_time(self, process):
        if process.finish_time is None:
            return None
        return process.finish_time - process.arrival_time

    def get_waiting_time(self, process):
        tat = self.get_turnaround_time(process)
        if tat is None:
            return None
        return tat - process.total_burst

    def get_response_time(self, process):
        if process.start_time is None:
            return None
        return process.start_time - process.arrival_time


    def get_avg_turnaround(self):
        times = [
            self.get_turnaround_time(p)
            for p in self.completed
            if self.get_turnaround_time(p) is not None
        ]
        return sum(times) / len(times) if times else 0

    def get_avg_waiting(self):
        times = [
            self.get_waiting_time(p)
            for p in self.completed
            if self.get_waiting_time(p) is not None
        ]
        return sum(times) / len(times) if times else 0

    def get_avg_response(self):
        times = [
            self.get_response_time(p)
            for p in self.completed
            if self.get_response_time(p) is not None
        ]
        return sum(times) / len(times) if times else 0

    # CPU accounting
    def get_total_busy_time(self):
        """Total CPU execution time (sum of bursts)."""
        if self._cached_busy_time is None:
            self._cached_busy_time = sum(
                p.total_burst for p in self.completed
            )
        return self._cached_busy_time

    def get_total_idle_time(self):
        """Total CPU idle time."""
        if self.total_time == 0:
            return 0
        return self.total_time - self.get_total_busy_time()

    def get_cpu_utilization(self):
        """CPU utilization percentage."""
        if self.total_time == 0:
            return 0

        busy = self.get_total_busy_time()
        return (busy / self.total_time) * 100
